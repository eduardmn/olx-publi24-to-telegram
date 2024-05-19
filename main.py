
import httpx, sqlite3, re, json, time
from lxml import html
from log_config import logger
from time_convert import calculate_days_from_today
from httpx import Timeout

TELEGRAM_CHAT_ID = '0123456789'
TELEGRAM_TOKEN = '123456789:ABCDefghijklmnopqrstuvwxyz123456789'

OLX_OFFERS_LIMIT = 1
OLX_API_ENDPOINT = F'https://www.olx.ro/api/v1/offers/?offset=0&limit{OLX_OFFERS_LIMIT}&category_id=907&region_id=8&city_id=81351&owner_type=private&currency=EUR&sort_by=created_at%3Adesc&filter_refiners=spell_checker&suggest_filters=true'

PUBLI24_OFFERS_LIMIT = 1
PUBLI24_URL_ENDPOINT = F'https://www.publi24.ro/anunturi/imobiliare/de-vanzare/apartamente/dolj/craiova/?commercial=false&pag=1&pagesize={PUBLI24_OFFERS_LIMIT}'

DB_PATH = 'offers.db'

timeout = Timeout(69.0)

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS olx_offers (
            id TEXT PRIMARY KEY
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS publi24_offers (
            id TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def send_telegram_request(url, data, timeout=timeout):
    retry_delay = 1  # start with a 1 second delay
    max_retries = 5  # maximum number of retries

    for attempt in range(max_retries):
        try:
            response = httpx.post(url, json=data, timeout=timeout)
            if response.status_code == 200:
                logger.info("Message sent successfully")
                return response.json()
            elif response.status_code == 429:
                retry_after = response.json().get('parameters', {}).get('retry_after', 30)
                logger.error(f"Too Many Requests: retry after {retry_after} seconds")
                time.sleep(retry_after)
            else:
                logger.error(f"Failed to send request: {response.text}")
                break
        except httpx.RequestError as e:
            logger.error(f"An error occurred: {str(e)}")
            time.sleep(retry_delay)
            retry_delay *= 2  # exponential backoff
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            break
    return None  # in case all retries fail

def clean_html_breaks(text):
    """ Replaces HTML break tags with newline characters. """
    return text.replace('<br />', '').replace('<br>', '')

def send_multiple_photos(photo_urls, chat_id=TELEGRAM_CHAT_ID):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMediaGroup'
    media_group = []

    for photo_url in photo_urls:
        item = {
            'type': 'photo',
            'media': photo_url
        }
        media_group.append(item)

    data = {
        'chat_id': chat_id,
        'media': json.dumps(media_group)  # Serialize list of media items to JSON string
    }
    send_telegram_request(url, data)

def send_telegram_message(text, chat_id=TELEGRAM_CHAT_ID):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    cleaned_text = clean_html_breaks(text)
    data = {
        'chat_id': chat_id,
        'text': cleaned_text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': 'true'
    }
    send_telegram_request(url, data)

def send_telegram_photo(photo_url, chat_id=TELEGRAM_CHAT_ID, caption=None):
    """
    Sends a photo to a Telegram chat with an optional custom caption.

    Args:
    chat_id (int or str): Unique identifier for the target chat or username of the target channel.
    photo_url (str): URL of the photo to be sent.
    caption (str, optional): Caption for the photo, can be up to 1024 characters long, supports Markdown or HTML.
    """
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto'
    data = {
        'chat_id': chat_id,
        'photo': photo_url,
        'parse_mode': 'HTML'
    }
    if caption:
        data['caption'] = caption

    send_telegram_request(url, data)

def process_and_resolve_photos(photos):
    """
    Processes a list of photo dictionaries to resolve their URLs by replacing width and height placeholders
    and removing the port number :443.

    Args:
    photos (list of dict): A list of dictionaries, each representing a photo with an id, link, width, and height.

    Returns:
    list of str: A list of resolved URLs without the port number.
    """
    resolved_urls = []
    for photo in photos:
        # Replace width and height placeholders with actual values
        resolved_url = photo['link'].replace('{width}', str(photo['width'])).replace('{height}', str(photo['height']))
        
        # Remove the port :443 from the URL
        resolved_url_no_port = resolved_url.replace(':443', '')
        
        # Append the cleaned URL to the list
        resolved_urls.append(resolved_url_no_port)
    
    return resolved_urls

def publi24_offer_process(url, xpath):
    """
    Fetches a webpage and extracts all URLs from a specific script identified by an XPath.

    Args:
    url (str): The URL of the webpage to fetch.
    xpath (str): The XPath to locate the script tag.

    Returns:
    list[str]: A list of URLs extracted from the script content.
    """
    try:
        # Make the HTTP request
        response = httpx.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise an exception for HTTP error responses

        # Parse the HTML content
        tree = html.fromstring(response.text)
        
        # Extract the script content using XPath
        script_content = tree.xpath(xpath)[0]
        if not script_content:
            return []  # No script tag found

        # Regular expression to find URLs
        url_pattern = r"https?://[\w\-._~:/?#\[\]@!$&'()*+,;=]*\.jpg"

        urls = re.findall(url_pattern, script_content)
        
        description = tree.xpath('//*[@id="content"]/div/div/div[1]/div[6]/p[1]/span/text()')[0]

        return urls, description
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return []

def record_exists(table, offer_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f'SELECT 1 FROM {table} WHERE id = ?', (offer_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def insert_record(table, offer_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO {table} (id) VALUES (?)', (offer_id,))
    conn.commit()
    conn.close()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.olx.ro/d/oferte/q-apartament/',
    'Connection': 'keep-alive',
}

def check_olx_offers():
    with httpx.Client(headers=headers, timeout=timeout) as client:
        response = client.get(OLX_API_ENDPOINT)
        offers = response.json()['data']
        for offer in offers:
            offer_id = str(offer['id'])
            if not record_exists('olx_offers', offer_id):
                
                url = f"https://www.olx.ro/{offer['id']}"
                description = offer['description']
                titlu = f"<b>{offer['title']}</b>"
                zile_in_piata = 'Zile în piață: ' + str(calculate_days_from_today(offer['created_time']))
                logger.info(f'New olx offer found: {offer_id}')

                formatted_params = []
                m_value = None  # Variable to store the value for the parameter with key "m"
                price_value = None  # Variable to store the value for the parameter with key "price"

                for param in offer['params']:
                    if param.get('key') == "constructie":
                        continue

                    if 'name' in param and 'value' in param:
                        # Store the value for the parameter with key "m"
                        if param['key'] == "m":
                            m_value = int(param['value'].get('key'))

                        if param['key'] == "price":
                            price_value = param['value'].get('value')

                        if 'label' in param['value']:
                            formatted_param = f"<b>{param['name']}:</b> {param['value']['label']}"
                            formatted_params.append(formatted_param)

                if price_value is not None and m_value is not None and m_value != 0:
                    price_per_m = int(price_value / m_value)
                    formatted_params.append(f"<b>Pret mp:</b> {price_per_m} €")

                params_string = '\n'.join(formatted_params)
                
                photos_urls = process_and_resolve_photos(offer['photos'])
            
                message = f"{titlu}\n{zile_in_piata}\n\n{params_string}\n\n{description}\n\n{url}"
                
                send_multiple_photos(photos_urls)
                send_telegram_message(message)
                insert_record('olx_offers', offer_id)

def check_publi24_offers():
    with httpx.Client(headers=headers, timeout=timeout) as client:
        response = client.get(PUBLI24_URL_ENDPOINT)
        tree = html.fromstring(response.text)
        listings = tree.xpath('//li[@data-articleid]')
        for listing in listings:
            offer_id = listing.attrib['data-articleid']
            if not record_exists('publi24_offers', offer_id):
                url = listing.xpath('.//a[@href]/@href')[0]
                logger.info(f'New Publi24 offer found: {url}')
                
                title = listing.xpath('.//h3/a/text()')[0].strip()
                
                photo_unparsed = listing.xpath('.//a[@class="listing-image"]/@style')[0]
                photo = re.search(r"url\('([^']+)'\)", photo_unparsed).group(1)
                
                # Extract the price
                price_tag = listing.xpath('.//strong[contains(@class, "price")]/text()')[0]
                price_f = f"<b>Pret: </b>{price_tag}"
                
                # Extract the price per square meter
                price_mp = listing.xpath('.//label[contains(@class, "article-details")]/text()[2]')[0].strip()
                price_mp_f = f"<b>Preț: </b> {price_mp}p"
                
                (photos_urls, description) = publi24_offer_process(url,'//*[@id="content"]/div/div/div[1]/script/text()')
                
                message = f"{title}\n\n{price_f}\n{price_mp_f}\n\n{description}\n\n{url}"
                send_multiple_photos(photos_urls)
                send_telegram_message(message)
                insert_record('publi24_offers', offer_id)

def main():
    setup_database()
    check_olx_offers()
    check_publi24_offers()

if __name__ == '__main__':
    main()
