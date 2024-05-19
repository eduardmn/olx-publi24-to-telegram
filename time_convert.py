import datetime


def format_timestamp(input_timestamp):
    """
    Format a timestamp to "dd MMM yyyy - HH:MM".

    :param input_timestamp: Timestamp string in ISO format.
    :return: Formatted timestamp string.
    """
    from datetime import datetime

    # Parsing the input string to a datetime object
    datetime_obj = datetime.fromisoformat(input_timestamp)

    # Formatting the datetime
    formatted_timestamp = datetime_obj.strftime("%d %b %Y - %H:%M")
    return formatted_timestamp


def calculate_days_from_today(iso_date_string):
    # Convert the ISO format date string to a datetime object
    given_date = datetime.datetime.fromisoformat(iso_date_string).date()

    # Get today's date
    today = datetime.date.today()

    # Calculate the difference in days
    difference = today - given_date

    # Return the difference in days
    return difference.days
