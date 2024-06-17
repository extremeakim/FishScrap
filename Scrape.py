import requests
from bs4 import BeautifulSoup
from lxml import html
import pandas as pd
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import logging
import sys
import random
import time
import urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Initialize WebDriver with headless options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Disable SSL warnings temporarily (Not recommended for production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# List of websites to scrape
websites = {
    "Shuk HaDagim": [
        "https://shukadagim.co.il",
        "https://shukadagim.co.il/%d7%a1%d7%a4%d7%99%d7%99%d7%a9%d7%9c-%d7%94%d7%a9%d7%91%d7%95%d7%a2/",
        "https://shukadagim.co.il/%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d-%d7%a9%d7%95%d7%a7-%d7%94%d7%93%d7%92%d7%99%d7%9d/",
        "https://shukadagim.co.il/%d7%9e%d7%95%d7%a6%d7%a8%d7%99%d7%9d-%d7%a0%d7%95%d7%a1%d7%a4%d7%99%d7%9d/"
    ],
    "Udi Fish": [
        "https://www.udifish.co.il",
        "https://www.udifish.co.il/category/%D7%93%D7%92-%D7%98%D7%A8%D7%99",
        "https://www.udifish.co.il/category/%D7%9E%D7%99%D7%95%D7%97%D7%93%D7%99%D7%9D",
        "https://www.udifish.co.il/category/%D7%AA%D7%91%D7%9C%D7%99%D7%A0%D7%99%D7%9D",
        "https://www.udifish.co.il/category/%D7%9E%D7%A2%D7%93%D7%A0%D7%99%D7%94",
        "https://www.udifish.co.il/category/%D7%93%D7%92%D7%99%D7%9D-%D7%9E%D7%A2%D7%95%D7%A9%D7%A0%D7%99%D7%9D",
        "https://www.udifish.co.il/category/%D7%9E%D7%95%D7%A6%D7%A8%D7%99-%D7%A4%D7%A8%D7%99%D7%9E%D7%99%D7%95%D7%9D",
        "https://www.udifish.co.il/category/%D7%90%D7%A1%D7%99%D7%99%D7%90%D7%AA%D7%99",
        "https://www.udifish.co.il/category/%D7%A7%D7%A4%D7%95%D7%90%D7%99%D7%9D"
    ],
    "Shaldag": [
        "https://shaldag.net",
        "https://shaldag.net/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d/",
        "https://shaldag.net/product-category/%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%99%d7%9d/",
        "https://shaldag.net/product-category/%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%99%d7%9d-%d7%a7%d7%a4%d7%95%d7%90%d7%99%d7%9d/",
        "https://shaldag.net/product-category/%d7%94%d7%9e%d7%98%d7%91%d7%97-%d7%94%d7%90%d7%a1%d7%99%d7%99%d7%90%d7%aa%d7%99/",
        "https://shaldag.net/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%a7%d7%a4%d7%95%d7%90%d7%99%d7%9d/",
        "https://shaldag.net/product-category/%d7%92%d7%91%d7%99%d7%a0%d7%95%d7%aa-%d7%9e%d7%a2%d7%93%d7%a0%d7%99%d7%99%d7%aa-%d7%92%d7%95%d7%a8%d7%9e%d7%94/",
        "https://shaldag.net/product-category/%d7%94%d7%9e%d7%98%d7%91%d7%97-%d7%94%d7%90%d7%99%d7%98%d7%9c%d7%a7%d7%99/",
        "https://shaldag.net/product-category/%d7%9e%d7%91%d7%a6%d7%a2%d7%99-%d7%94%d7%a9%d7%91%d7%95%d7%a2/",
        "https://shaldag.net/shop/"
    ],
    "Zano-Dagim": [
        "https://www.zano-dagim.co.il",
        "https://www.zano-dagim.co.il/all-fish"
    ],
    "BatShon": [
        "https://batshon.co.il",
        "https://batshon.co.il/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d/",
        "https://batshon.co.il/product-category/%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d/",
        "https://batshon.co.il/product-category/%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%99%d7%9d-%d7%a7%d7%a4%d7%95%d7%90%d7%99%d7%9d/",
        "https://batshon.co.il/product-category/%d7%99%d7%99%d7%a0%d7%95%d7%aa/",
        "https://batshon.co.il/product-category/%d7%9e%d7%95%d7%a6%d7%a8%d7%99%d7%9d-%d7%a0%d7%9c%d7%95%d7%95%d7%99%d7%9d/",
        "https://batshon.co.il/product-category/%d7%94%d7%9e%d7%99%d7%95%d7%97%d7%93%d7%99%d7%9d-%d7%a9%d7%9c-%d7%98%d7%95%d7%98%d7%95/",
        "https://batshon.co.il/product-category/%d7%9e%d7%91%d7%a6%d7%a2%d7%99%d7%9d/"
    ],
    "Sea2door": [
        "https://sea2door.co.il",
        "https://sea2door.co.il/product-category/%D7%93%D7%92%D7%99%D7%9D-%D7%98%D7%A8%D7%99%D7%99%D7%9D/",
        "https://sea2door.co.il/product-category/%D7%A4%D7%99%D7%A8%D7%95%D7%AA-%D7%99%D7%9D-%D7%98%D7%A8%D7%99%D7%99%D7%9D/",
        "https://sea2door.co.il/product-category/%D7%A4%D7%99%D7%A8%D7%95%D7%AA-%D7%99%D7%9D-%D7%A7%D7%A4%D7%95%D7%90%D7%99%D7%9D/",
        "https://sea2door.co.il/product-category/%D7%94%D7%9E%D7%A2%D7%93%D7%A0%D7%99%D7%94/",
        "https://sea2door.co.il/product-category/%D7%9E%D7%99%D7%95%D7%97%D7%93%D7%99%D7%9D-%D7%95%D7%9E%D7%A2%D7%95%D7%A9%D7%A0%D7%99%D7%9D/",
        "https://sea2door.co.il/product-category/%D7%AA%D7%91%D7%9C%D7%99%D7%A0%D7%99%D7%9D/",
        "https://sea2door.co.il/product-category/%D7%99%D7%99%D7%A0%D7%95%D7%AA/",
        "https://sea2door.co.il/product-category/%D7%9E%D7%95%D7%A6%D7%A8%D7%99%D7%9D-%D7%90%D7%A1%D7%99%D7%99%D7%AA%D7%99%D7%99%D7%9D/",
        "https://sea2door.co.il/product-category/%D7%9E%D7%91%D7%A6%D7%A2%D7%99-%D7%94%D7%97%D7%95%D7%93%D7%A9/",
        "https://sea2door.co.il/product-category/%D7%A8%D7%98%D7%91%D7%99%D7%9D-%D7%95%D7%A9%D7%9E%D7%A0%D7%99%D7%9D/",
        "https://sea2door.co.il/product-category/%D7%A8%D7%9B%D7%99%D7%A9%D7%94-%D7%A1%D7%99%D7%98%D7%95%D7%A0%D7%90%D7%99%D7%AA/"
    ],
    "Okyanos": [
        "https://okyanos-seafood.co.il",
        "https://okyanos-seafood.co.il/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d/",
        "https://okyanos-seafood.co.il/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%a7%d7%a4%d7%95%d7%90%d7%99%d7%9d/",
        "https://okyanos-seafood.co.il/product-category/current-sale/",
        "https://okyanos-seafood.co.il/product-category/%d7%9e%d7%a2%d7%93%d7%a0%d7%99%d7%94/",
        "https://okyanos-seafood.co.il/product-category/%d7%91%d7%a9%d7%a8-%d7%95%d7%a2%d7%95%d7%a3-%d7%a7%d7%a4%d7%95%d7%90/",
        "https://okyanos-seafood.co.il/product-category/%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%99%d7%9d-%d7%a7%d7%a4%d7%95%d7%90%d7%99%d7%9d/",
        "https://okyanos-seafood.co.il/product-category/%d7%a4%d7%99%d7%a8%d7%95%d7%aa-%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d/"
    ],
    "Dagi-Kineret": [
        "https://dagi-kinneret.co.il",
        "https://dagi-kinneret.co.il/product-category/%d7%9b%d7%9c-%d7%94%d7%93%d7%92%d7%99%d7%9d/",
        "https://dagi-kinneret.co.il/product-category/%d7%9e%d7%94%d7%9b%d7%a0%d7%a8%d7%aa/",
        "https://dagi-kinneret.co.il/product-category/%d7%9e%d7%94%d7%99%d7%9d/",
        "https://dagi-kinneret.co.il/product-category/%d7%9e%d7%94%d7%91%d7%a8%d7%99%d7%9b%d7%94/",
        "https://dagi-kinneret.co.il/product-category/%d7%9b%d7%9c-%d7%94%d7%93%d7%92%d7%99%d7%9d/%d7%94%d7%93%d7%92%d7%99%d7%9d-%d7%94%d7%9e%d7%a4%d7%95%d7%9c%d7%98%d7%99%d7%9d-%d7%a9%d7%9c%d7%a0%d7%95/",
        "https://dagi-kinneret.co.il/product-category/%d7%a7%d7%a4%d7%95%d7%90%d7%99%d7%9d/",
        "https://dagi-kinneret.co.il/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%97%d7%95%d7%a0%d7%99%d7%9d/"
    ],
    "Fisherman": [
        "https://www.fisherman.co.il",
        "https://www.fisherman.co.il/shop/",
        "https://www.fisherman.co.il/product-category/fresh-fish/",
        "https://www.fisherman.co.il/product-category/special-smoked-fish/",
        "https://www.fisherman.co.il/product-category/pickled-fish/",
        "https://www.fisherman.co.il/product-category/frozen-fish/",
        "https://www.fisherman.co.il/product-category/japanese-food/"
    ],
    "Butik-Dagim": [
        "https://butik-dagim.co.il",
        "https://butik-dagim.co.il/product-category/fresh-fish/",
        "https://butik-dagim.co.il/product-category/frozen-fish/",
        "https://butik-dagim.co.il/product-category/minced-fish/",
        "https://butik-dagim.co.il/product-category/%d7%aa%d7%91%d7%9c%d7%99%d7%a0%d7%99%d7%9d/",
        "https://butik-dagim.co.il/product-category/%d7%9c%d7%99%d7%93-%d7%94%d7%93%d7%92/",
        "https://butik-dagim.co.il/product-category/fish-packages/",
        "https://butik-dagim.co.il/sales/"
    ],
    "BitmanFish": [
        "https://bitmanfish.com",
        "https://bitmanfish.com/shop/",
        "https://bitmanfish.com/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d/%d7%93%d7%92%d7%99-%d7%99%d7%9d-%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d/",
        "https://bitmanfish.com/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d/%d7%93%d7%92%d7%99-%d7%91%d7%a8%d7%99%d7%9b%d7%94-%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%a8%d7%99%d7%99%d7%9d/",
        "https://bitmanfish.com/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%a7%d7%a4%d7%95%d7%90%d7%99%d7%9d/",
        "https://bitmanfish.com/product-category/%d7%9e%d7%a2%d7%93%d7%a0%d7%99%d7%99%d7%94/",
        "https://bitmanfish.com/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%a0%d7%90%d7%99%d7%9d/",
        "https://bitmanfish.com/product-category/%d7%9e%d7%a2%d7%93%d7%a0%d7%99%d7%99%d7%94/%d7%9e%d7%a2%d7%95%d7%a9%d7%a0%d7%99%d7%9d/"
    ],
    "Rupinfish": [
        "https://rupinfish.co.il",
        "https://rupinfish.co.il/product-category/%d7%93%d7%92%d7%99-%d7%91%d7%a8%d7%99%d7%9b%d7%95%d7%aa/",
        "https://rupinfish.co.il/product-category/%d7%93%d7%92%d7%99-%d7%99%d7%9d/",
        "https://rupinfish.co.il/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%98%d7%97%d7%95%d7%a0%d7%99%d7%9d/",
        "https://rupinfish.co.il/product-category/%d7%93%d7%92%d7%99%d7%9d-%d7%a7%d7%a4%d7%95%d7%90%d7%99%d7%9d/"
    ]
}

# Set up logging to both console and file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create handlers
file_handler = logging.FileHandler('scraper.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatters and add them to handlers
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Configure retries
session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# List of user agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
]

# Initialize WebDriver (assuming ChromeDriver is in your PATH)
driver = webdriver.Chrome()

def is_javascript_heavy(url):
    headers = {
        'User-Agent': random.choice(user_agents),
    }
    response = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Heuristic: Check for common AJAX indicators
    if soup.find_all(['script', 'noscript']):
        return True
    return False

def extract_products_with_selenium(url):
    logger.info(f"Scraping URL with Selenium: {url}")
    driver.get(url)
    time.sleep(3)  # Wait for JavaScript to load content
    products = []

    price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '₪') or contains(text(), 'NIS')]")
    for price_element in price_elements:
        try:
            # Get the parent element that contains the product details
            product_element = price_element.find_element(By.XPATH, "./ancestor::*[contains(@class, 'product') or contains(@class, 'item')]")
            price = price_element.text.strip()
            logger.info(f"Product Price: {price}")

            name = product_element.text.split(price)[0].strip()  # Extract name from the product element
            logger.info(f"Product Name: {name}")

            product_url = product_element.find_element(By.XPATH, "./ancestor-or-self::a[contains(@href, 'product') or contains(@href, 'item')]").get_attribute('href')
            logger.info(f"Product URL: {product_url}")

            products.append({'name': name, 'price': price, 'url': product_url})
        except Exception as e:
            logger.error(f"Error extracting product with Selenium: {e}")
            continue

    return products


def extract_products_with_requests(url):
    logger.info(f"Scraping URL with requests: {url}")
    headers = {
        'User-Agent': random.choice(user_agents),
        'Referer': url
    }
    try:
        response = session.get(url, headers=headers, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return []

    tree = html.fromstring(response.content)
    products = []

    price_elements = tree.xpath("//*[contains(text(), '₪') or contains(text(), 'NIS')]")
    for price_element in price_elements:
        try:
            price = price_element.text_content().strip()
            logger.info(f"Product Price: {price}")

            product_element = price_element.xpath("./ancestor::*[contains(@class, 'product') or contains(@class, 'item')]")[0]
            name = product_element.text_content().split(price)[0].strip()  # Extract name from the product element
            logger.info(f"Product Name: {name}")

            product_url_elements = product_element.xpath("./ancestor-or-self::a[contains(@href, 'product') or contains(@href, 'item')]")
            product_url = product_url_elements[0].get('href') if product_url_elements else 'N/A'
            logger.info(f"Product URL: {product_url}")

            products.append({'name': name, 'price': price, 'url': product_url})
        except Exception as e:
            logger.error(f"Error extracting product with requests: {e}")
            continue

    return products


def get_product_info(url):
    if is_javascript_heavy(url):
        return extract_products_with_selenium(url)
    else:
        return extract_products_with_requests(url)


def main():
    logger.info("Starting scraping process")
    writer = pd.ExcelWriter('fish_products.xlsx', engine='openpyxl')
    for site_name, urls in websites.items():
        logger.info(f"Scraping {site_name}...")
        all_products = []
        for url in urls:
            try:
                products = get_product_info(url)
                all_products.extend(products)
                time.sleep(1)  # Add delay to prevent triggering firewalls
            except requests.exceptions.RequestException as e:
                logger.error(f"Error scraping {site_name} at {url}: {e}")

        if all_products:
            df = pd.DataFrame(all_products)
            df.to_excel(writer, sheet_name=site_name, index=False)
        else:
            logger.warning(f"No products found for {site_name}")
            # Ensure at least one empty sheet is created
            df = pd.DataFrame([{'name': 'No products', 'price': 'N/A', 'url': 'N/A'}])
            df.to_excel(writer, sheet_name=site_name, index=False)
    writer.close()
    logger.info("Scraping complete. Data saved to fish_products.xlsx")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Script interrupted by user")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()