import os
from langchain_community.llms import Ollama
from crewai import Agent, Task, Crew, Process
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from urllib.parse import urlparse
import csv
from io import StringIO

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler
file_handler = logging.FileHandler("scraper.log", encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Stream handler with utf-8 encoding
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Initialize the model
model = Ollama(model="llama3")

# Read websites from file
with open(r"D:\VM\AI\Target Websites.txt", 'r', encoding='utf-8') as file:
    websites = [line.strip() for line in file.readlines()]

# Define the agents
tagfinder = Agent(
    role="Product Information Extractor",
    goal="Extract relevant product information such as product name, price, and category from the given HTML content",
    backstory="You are an AI assistant whose job is to extract product-related information from the HTML content provided",
    verbose=True,
    allow_delegation=False,
    llm=model
)

# Function to scrape webpage content
def scrape_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we raise an error for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')
        logger.info(f"Successfully scraped {url}")
        return str(soup)
    except requests.RequestException as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return ""

# Function to save product information to an Excel file
def save_to_excel(data, filename="products.xlsx"):
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        for site, products in data.items():
            df = pd.DataFrame(products)
            # Get the main domain name for the sheet
            parsed_url = urlparse(site)
            main_domain = parsed_url.netloc.split('.')[1] if 'www' in parsed_url.netloc else parsed_url.netloc
            sheet_name = main_domain[:31]
            if sheet_name in writer.sheets:
                existing_df = pd.read_excel(writer, sheet_name=sheet_name)
                df = pd.concat([existing_df, df], ignore_index=True)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            logger.info(f"Saved data to sheet: {sheet_name}")

# Function to parse CSV output
def parse_csv_output(csv_string):
    csv_file = StringIO(csv_string)
    reader = csv.DictReader(csv_file)
    return list(reader)

# Collect all products information
all_products = {}

for website in websites:
    # Scrape the content of the website
    webpage_content = scrape_webpage(website)
    
    if not webpage_content:
        continue
    
    # Define the task for the agent
    find_products = Task(
        description=f"Extract product information from {website}",
        agent=tagfinder,
        expected_output="A CSV string with columns 'name', 'price', and 'category'",
        context=[{
            'description': f"HTML content of {website}",
            'expected_output': "HTML content",
            'html_content': webpage_content
        }]
    )

    # Define the crew for this task
    crew = Crew(
        agents=(tagfinder,),
        tasks=(find_products,),
        verbose=2,
        Process=Process.sequential,
    )

    # Execute the crew to extract product information
    product_info = crew.kickoff()

    # Log the raw output for debugging
    logger.debug(f"Raw output for {website}: {product_info}")

    # Parse the CSV output
    try:
        product_info = parse_csv_output(product_info)
        if website in all_products:
            all_products[website].extend(product_info)
        else:
            all_products[website] = product_info
        logger.info(f"Extracted product information from {website}")
    except Exception as e:
        logger.error(f"Error parsing CSV for {website}: {e}")
        continue

# Save all product information to an Excel file
save_to_excel(all_products)

logger.info("Product information has been successfully saved to products.xlsx")
