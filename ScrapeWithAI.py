import os
from langchain_community.llms import Ollama
from crewai import Agent, Task, Crew, Process
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# Initialize the model
model = Ollama(model="llama3")

# Read websites from file
with open(r"D:\VM\AI\Target Websites.txt", 'r') as file:
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
        return str(soup)
    except requests.RequestException as e:
        print(f"Failed to scrape {url}: {e}")
        return ""

# Function to save product information to an Excel file
def save_to_excel(data, filename="products.xlsx"):
    with pd.ExcelWriter(filename) as writer:
        for site, products in data.items():
            df = pd.DataFrame(products)
            # Sanitize the sheet name by removing invalid characters
            sheet_name = site.replace("https://", "").replace("/", "_")
            df.to_excel(writer, sheet_name=sheet_name, index=False)

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
        expected_output="A list of dictionaries with keys 'name', 'price', and 'category'",
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

    # Parse the output into a usable format (assume output is a JSON string)
    try:
        product_info = json.loads(product_info)
        all_products[website] = product_info
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for {website}: {e}")
        continue

# Save all product information to an Excel file
save_to_excel(all_products)

print("Product information has been successfully saved to products.xlsx")
