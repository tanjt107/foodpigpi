import demoji
import json
import re
import urllib
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_config(fp: str) -> dict:
    "fp: File path of a json document."
    with open(fp) as f:
        return json.load(f)


def get_template(name: str):
    "name: Name of the template to load."
    return Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    ).get_template(name)


def map_dict_keys(record: dict, arg: dict) -> dict:
    "For mapping column names."
    return {arg[k]: v for k, v in record.items() if k in arg}


def format_phone_number(number: str) -> str:
    "Remove non-digits and add Hong Kongcountry code if phone number has 8 digits."
    number = re.sub(r"\D", "", str(number))
    return f"852{number}" if len(number) == 8 else number


def encode_url(test: str) -> str:
    return urllib.parse.quote(test)


def get_whatsapp_link(number: str, text: str) -> str:
    number = format_phone_number(number)
    text = encode_url(text)
    return f"https://api.whatsapp.com/send?phone={number}&text={text}"


def remove_emoji(string: str) -> str:
    """Remove emoji from string."""
    return demoji.replace(string, "")


def dict_to_list_of_rows(data: dict) -> list:
    "Convert a dictionary to a list of [[key, value], [key, value], ...]."
    values = []
    for key, value in data.items():
        key = list(key) if isinstance(key, tuple) else [key]
        value = list(value) if isinstance(value, tuple) else [value]
        values.append(key + value)
    return values
