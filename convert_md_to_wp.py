import os
import markdown
import requests
from slugify import slugify
from requests.exceptions import RequestException
import chardet
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from .env file
load_dotenv()

# Load configuration with fallback values
WORDPRESS_URL = os.getenv("WORDPRESS_URL")
USERNAME = os.getenv("WORDPRESS_USERNAME")
PASSWORD = os.getenv("WORDPRESS_PASSWORD")
MARKDOWN_DIRECTORY = os.getenv("MARKDOWN_DIRECTORY")


def convert_markdown_to_html(markdown_file):
    """Converts a Markdown file to HTML."""
    try:
        with open(markdown_file, "rb") as file:
            raw_data = file.read()
            detected = chardet.detect(raw_data)
            encoding = detected["encoding"]

        with open(markdown_file, "r", encoding=encoding) as file:
            text = file.read()
            html = markdown.markdown(
                text, extensions=["fenced_code", "tables", "codehilite"]
            )
        return html
    except IOError as e:
        print(f"Error reading file {markdown_file}: {e}")
        return None


def create_wordpress_page(title, content, slug):
    """Creates a new WordPress page via the REST API."""
    data = {
        "title": title,
        "content": content,
        "slug": slug,
        "status": "draft",
    }

    try:
        response = requests.post(WORDPRESS_URL, auth=(USERNAME, PASSWORD), json=data)
        response.raise_for_status()
        print(f"Page '{title}' created successfully.")
    except RequestException as e:
        print(f"Failed to create page '{title}'. Error: {e}")
        if hasattr(e.response, "text"):
            print(f"Response content: {e.response.text}")


def process_markdown_files(directory):
    """Processes each Markdown file in the directory and converts them to WordPress pages."""
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            file_path = os.path.join(directory, filename)
            title = os.path.splitext(filename)[0]
            slug = slugify(title)
            content = convert_markdown_to_html(file_path)
            if content:
                create_wordpress_page(title, content, slug)


if __name__ == "__main__":
    if not all([WORDPRESS_URL, USERNAME, PASSWORD, MARKDOWN_DIRECTORY]):
        logging.error("Please set all required environment variables.")
    else:
        logging.info(f"Processing markdown files from {MARKDOWN_DIRECTORY}")
        process_markdown_files(MARKDOWN_DIRECTORY)
