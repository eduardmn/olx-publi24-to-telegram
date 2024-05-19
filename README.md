# Telegram Bot for Sending Offers from OLX and Publi24

This repository contains a script that checks for new offers on OLX and Publi24 platforms and sends the offer details including all photos, title, description, and price to a specified Telegram chat. The script uses `httpx` for HTTP requests, `sqlite3` for database interactions, and `lxml` for HTML parsing. 

## Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/telegram-offer-bot.git
cd telegram-offer-bot
```

### 2. Install Dependencies

It is recommended to use a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Configure Your Telegram Bot
You need to have a Telegram bot. Create a bot using BotFather and get the bot token.

Update the following constants in the script with your Telegram credentials:

```python
TELEGRAM_CHAT_ID = 'your_chat_id'
TELEGRAM_TOKEN = 'your_telegram_bot_token'
```
### 4. Configure Offer Endpoints

Specify the endpoints for OLX and Publi24. Example placeholders are provided in the script. Replace them with actual API endpoints or URLs as required.

```python
OLX_OFFERS_LIMIT = 1
OLX_API_ENDPOINT = f'https://www.olx.ro/api/v1/offers/?offset=0&limit{OLX_OFFERS_LIMIT}&category_id=907&region_id=8&city_id=81351&owner_type=private&currency=EUR&sort_by=created_at%3Adesc&filter_refiners=spell_checker&suggest_filters=true'

PUBLI24_OFFERS_LIMIT = 1
PUBLI24_URL_ENDPOINT = f'https://www.publi24.ro/anunturi/imobiliare/de-vanzare/apartamente/dolj/craiova/?commercial=false&pag=1&pagesize={PUBLI24_OFFERS_LIMIT}'
```



## Run the script:

### Check once
The script will check for new offers on OLX and Publi24, process the offer details, and send them to the specified Telegram chat.
```python
python main.py
```

### Running as a Cronjob
To continuously check for new offers, you can set up a cron job to run the script at regular intervals, such as every 10 minutes.
Open your crontab file for editing:

```bash
crontab -e
```

Add the following line to schedule the script to run every 10 minutes:

```bash
*/10 * * * * /path/to/your/venv/bin/python /path/to/your/script/main.py
```
Replace /path/to/your/venv/bin/python with the path to your Python interpreter and /path/to/your/script/main.py with the path to the script.
Save and close the crontab file. The script will now run every 10 minutes and check for new offers.

## Functions

`setup_database()`
Creates the SQLite database and tables if they do not exist.

`send_telegram_request(url, data, timeout)`
Sends a request to the Telegram API with retry logic.

`clean_html_breaks(text)`
Replaces HTML break tags with newline characters.

`send_multiple_photos(photo_urls, chat_id)`
Sends multiple photos to the specified Telegram chat.

`send_telegram_message(text, chat_id)`
Sends a text message to the specified Telegram chat.

`send_telegram_photo(photo_url, chat_id, caption)`
Sends a photo with an optional caption to the specified Telegram chat.

`process_and_resolve_photos(photos)`
Processes a list of photo dictionaries to resolve their URLs.

`publi24_offer_process(url, xpath)`
Fetches a webpage and extracts all URLs and the description from a specific script identified by an XPath.

`record_exists(table, offer_id)`
Checks if a record with the specified offer ID exists in the database.

`insert_record(table, offer_id)`
Inserts a new offer ID into the specified table in the database.

`check_olx_offers()`
Checks for new offers on OLX, processes them, and sends them to the specified Telegram chat.

`check_publi24_offers()`
Checks for new offers on Publi24, processes them, and sends them to the specified Telegram chat.

`main()`
Sets up the database and checks for new offers on OLX and Publi24.

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

This project is licensed under the MIT License.

## Enjoy

Now you have a script for monitoring and sending offers from OLX and Publi24 to a Telegram chat. Simply update the placeholders with the actual endpoints and your Telegram bot credentials to get started. To run the script continuously, set up a cron job to execute the script at your desired interval, such as every 10 minutes.
