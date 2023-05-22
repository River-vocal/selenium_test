from io import BytesIO

import PyPDF2
import requests
import re
from constants import context_length


def search_with_context(target_str, keyword, context=context_length) -> list:
    """
    Searches the text for the keyword and returns it with context.

    :param target_str: The text to search
    :param keyword: The keyword to search for
    :param context: The number of characters of context to provide on each side of the keyword
    :return: A list of strings, each containing the keyword and the surrounding context
    """
    results: list = []
    loc = target_str.find(keyword)
    while loc != -1:
        start = max(0, loc - context)
        end = min(len(target_str), loc + len(keyword) + context)
        results.append(target_str[start:end])
        loc = target_str.find(keyword, loc + 1)
    return results


def extract_text_content_from_url(url: str) -> str:
    print(f"Extracting text from {url}")
    response = requests.get(url)
    my_raw_data = response.content

    with BytesIO(my_raw_data) as data:
        read_pdf = PyPDF2.PdfReader(data)
        str_list: list = []
        for page in read_pdf.pages:
            tmp_str: str = page.extract_text().strip()
            str_list.append(re.sub(" +", ' ', tmp_str.replace('\n', ' ')))
    return " ".join(str_list)
