import time
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to initialize the headless browser
def init_browser():
    options = Options()
    options.headless = True  # Ensure headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Scrape gig details from Fiverr
def scrape_gigs(platform, category):
    url = f'https://www.fiverr.com/search/gigs?query={category}'
    driver = init_browser()
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    # Extract page source using BeautifulSoup for parsing
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extracting gig elements from the page
    gigs = soup.find_all('div', {'class': 'gig-card-layout'})

    gigs_data = []
    for gig in gigs:
        try:
            title = gig.find('a', {'class': 'gig-title'}).text.strip()
            price = gig.find('span', {'class': 'price'}).text.strip()
            rating = gig.find('div', {'class': 'star-rating'}).text.strip() if gig.find('div', {'class': 'star-rating'}) else 'No rating'
            orders = gig.find('span', {'class': 'gig-orders'}).text.strip() if gig.find('span', {'class': 'gig-orders'}) else 'No orders'
            reviews = gig.find('div', {'class': 'gig-reviews'}).text.strip() if gig.find('div', {'class': 'gig-reviews'}) else 'No reviews'
            seller = gig.find('span', {'class': 'seller-name'}).text.strip() if gig.find('span', {'class': 'seller-name'}) else 'Unknown'

            # Calculate competition level (low/high based on reviews)
            competition = 'Low' if int(reviews.split()[0]) < 50 else 'High'

            gig_data = {
                'title': title,
                'price': price,
                'rating': rating,
                'orders': orders,
                'reviews': reviews,
                'seller': seller,
                'competition': competition,
            }
            gigs_data.append(gig_data)
        except Exception as e:
            logging.error(f"Error scraping gig: {e}")
            continue
    
    driver.quit()
    return gigs_data

# Analyze and calculate demand percentage and competition
def analyze_gigs(gigs_data):
    total_gigs = len(gigs_data)
    gigs_with_orders = len([gig for gig in gigs_data if gig['orders'] != 'No orders'])
    demand_percentage = (gigs_with_orders / total_gigs) * 100 if total_gigs > 0 else 0

    # Sort gigs by orders to find the top 10
    top_10_gigs = sorted(gigs_data, key=lambda x: int(x['orders'].split()[0]) if x['orders'] != 'No orders' else 0, reverse=True)[:10]

    # Log the analysis
    logging.info(f"Total Gigs: {total_gigs}")
    logging.info(f"Gigs with Orders: {gigs_with_orders} ({demand_percentage:.2f}%)")
    
    return top_10_gigs, demand_percentage

# Save scraped data to JSON file
def save_data_to_json(gigs_data, category):
    filename = f"fiverr_gigs_{category}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(gigs_data, f, ensure_ascii=False, indent=4)
    logging.info(f"Data saved to {filename}")

# Main function to orchestrate the scraping process
def main():
    category = input("Enter the category or keyword to search: ").strip()
    logging.info(f"Starting scrape for Fiverr in category: {category}")

    gigs_data = scrape_gigs('Fiverr', category)
    
    if gigs_data:
        top_10_gigs, demand_percentage = analyze_gigs(gigs_data)
        logging.info(f"Top 10 Gigs: {top_10_gigs}")
        logging.info(f"Demand Percentage: {demand_percentage:.2f}%")
        save_data_to_json(gigs_data, category)
    else:
        logging.warning("No gigs found.")

if __name__ == "__main__":
    main()
  
