import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from lxml import html

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

from lxml import html

def get_product_info(url, name_selector, price_selector, url_selector):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []

    # Debug: Print the URL being scraped
    print(f"Scraping URL: {url}")

    # Convert BeautifulSoup object to lxml object
    tree = html.fromstring(response.content)

    # Find all product name elements
    name_elements = tree.cssselect(name_selector)

    # Debug: Print the count of name elements found
    print(f"Found {len(name_elements)} name elements")

    for name_element in name_elements:
        try:
            name = name_element.text_content().strip()
            # Debug: Print the product name
            print(f"Product Name: {name}")

            # Traverse to find the price element
            price_element = name_element.xpath(f'following-sibling::{price_selector}')
            if not price_element:
                price_element = name_element.xpath(f'ancestor::{price_selector}')
            if price_element:
                price = price_element[0].text_content().strip()
                # Debug: Print the product price
                print(f"Product Price: {price}")
            else:
                print(f"No price found for product: {name}")
                continue

            # Traverse to find the URL element
            url_element = name_element.xpath(f'ancestor::{url_selector}')
            if url_element and 'href' in url_element[0].attrib:
                product_url = url_element[0].attrib['href']
                # Debug: Print the product URL
                print(f"Product URL: {product_url}")
            else:
                print(f"No URL found for product: {name}")
                continue

            products.append({'name': name, 'price': price, 'url': product_url})
        except AttributeError as e:
            print(f"AttributeError: {e}")
            continue

    # Debug: Print the products found
    print(f"Products found: {products}")

    return products




def main():
    writer = pd.ExcelWriter('fish_products.xlsx', engine='openpyxl')
    for site_name, urls in websites.items():
        print(f"Scraping {site_name}...")
        all_products = []
        for url in urls:
            # Update these selectors based on the actual HTML structure of each website
            if site_name == "Shuk HaDagim":
                name_selector = "div.elementor-widget-container h2"  # Adjusted selector for product name
                price_selector = ".price ins"  # Adjusted selector for price within product container
                url_selector = "a.elementor-cta"
            elif site_name == "Udi Fish":
                name_selector = "div.item-name a"
                price_selector = "div.price-box.bold-price .price"
                url_selector = "div.item-name a"
            elif site_name == "Shaldag":
                name_selector = "li.product h2"
                price_selector = "li.product span.price ins"
                url_selector = "li.product a.woocommerce-loop-product__link"
            elif site_name == "Zano-Dagim":
                name_selector = "div.item.col-xs-3 p.product-name a"
                price_selector = "div.item.col-xs-3 span.price"
                url_selector = "div.item.col-xs-3 a.product-image"
            elif site_name == "BatShon":
                name_selector = "div.veg_price_content h3"
                price_selector = "div.price_veg p ins"
                url_selector = "a.getpopup"
            elif site_name == "Sea2door":
                name_selector = "div.item-wrap div.woocommerce-loop-product__title"
                price_selector = "div.item-wrap span.price span.woocommerce-Price-amount"
                url_selector = "a.woocommerce-LoopProduct-link"
            elif site_name == "Okyanos":
                name_selector = "div.astra-shop-summary-wrap h2.woocommerce-loop-product__title"
                price_selector = "div.astra-shop-summary-wrap span.price span.woocommerce-Price-amount"
                url_selector = "a.ast-loop-product__link"
            elif site_name == "Dagi-Kineret":
                name_selector = "li.product div.woocommerce-loop-product__title"
                price_selector = "li.product span.price span.woocommerce-Price-amount"
                url_selector = "a.woocommerce-LoopProduct-link"
            elif site_name == "Fisherman":
                name_selector = "div.inbox3 h2.woocommerce-loop-product__title"
                price_selector = "div.inbox3 span.price span.woocommerce-Price-amount"
                url_selector = "a.woocommerce-LoopProduct-link"
            elif site_name == "Butik-Dagim":
                name_selector = "div.jet-listing-grid__item h2.elementor-heading-title"
                price_selector = "div.jet-listing-grid__item div.jet-listing-dynamic-field__content ins span.woocommerce-Price-amount"
                url_selector = "a.elementor-element"
            elif site_name == "BitmanFish":
                name_selector = "div.jet-listing-grid__item h2.elementor-heading-title"
                price_selector = "div.jet-listing-grid__item div.jet-listing-dynamic-field__content ins span.woocommerce-Price-amount"
                url_selector = "a.jet-listing-dynamic-post"
            elif site_name == "Rupinfish":
                name_selector = "li.product h2.woocommerce-loop-product__title"
                price_selector = "li.product span.price"
                url_selector = "a.woocommerce-LoopProduct-link"
            else:
                name_selector = 'div.product'  # Generic selector as a fallback
                price_selector = 'span.price'
                url_selector = 'a.product-link'  # Hypothetical example, adjust as needed

            try:
                products = get_product_info(url, name_selector, price_selector, url_selector)
                all_products.extend(products)
            except requests.exceptions.RequestException as e:
                print(f"Error scraping {site_name} at {url}: {e}")

        if all_products:
            df = pd.DataFrame(all_products)
            df.to_excel(writer, sheet_name=site_name, index=False)
        else:
            print(f"No products found for {site_name}")
    writer.close()
    print("Scraping complete. Data saved to fish_products.xlsx")


if __name__ == "__main__":
    main()
