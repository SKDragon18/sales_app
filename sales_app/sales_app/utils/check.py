import re

def is_valid_email (email):
    email_regex =  r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex,email) is not None

def is_valid_phone(phone):
    phone_regex = r'^\+?\d{7,15}$'
    return re.match(phone_regex, phone) is not None