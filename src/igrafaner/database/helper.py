import re

def validate_datetime_format(datetime_str):
    datetime_pattern = r'^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?$'
    if not re.match(datetime_pattern, datetime_str):
        raise ValueError(f"The date time is incorrect: {datetime_str}")
