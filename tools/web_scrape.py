import requests
from bs4 import BeautifulSoup
from core.app_config import settings
from ._common import parse_input

DESCRIPTION = "Fetches the text content of a given URL, stripping all HTML tags."
ARGS_SCHEMA = '{"url": "<string: The full URL to scrape>"}'

def run(action_input):
    if not settings.get("ALLOW_NETWORK", True):
        return "Error: Network access is disabled by permissions."
        
    try:
        args = parse_input(action_input)
        url = args.get("url", "")
        if not url:
            return "Error: 'url' argument is required."

        headers = {"User-Agent": "JaraxxusAgent/1.0 (AI Assistant)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text
        
    except Exception as e:
        return f"Error retrieving or parsing URL: {e}"
