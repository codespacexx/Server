import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime
import json
from pathlib import Path

class MarketIntelligence:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        self.platforms = {
            'fiverr': 'https://www.fiverr.com/search/gigs?query=',
            'upwork': 'https://www.upwork.com/search/jobs/?q='
        }
        
    def safe_request(self, url):
        """Makes safe requests with random delays"""
        try:
            delay = random.uniform(2, 4)
            time.sleep(delay)
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Error accessing {url}: {e}")
            return None

    def analyze_competition(self, data):
        """Analyzes competition level based on multiple factors"""
        total_sellers = len(data)
        total_orders = sum(int(gig.get('orders', '0').replace('K', '000').replace('+', '')) for gig in data)
        avg_rating = sum(float(gig.get('rating', '0')) for gig in data) / total_sellers if total_sellers > 0 else 0
        
        # Competition metrics
        if total_sellers == 0:
            return {
                'competition_level': 'Unknown',
                'market_saturation': 0,
                'avg_rating': 0
            }
            
        saturation = min((total_sellers / 10) * 100, 100)  # Normalized to 100%
        
        if saturation < 30:
            competition = 'Low'
        elif saturation < 70:
            competition = 'Medium'
        else:
            competition = 'High'
            
        return {
            'competition_level': competition,
            'market_saturation': round(saturation, 2),
            'avg_rating': round(avg_rating, 2)
        }

    def analyze_demand(self, data):
        """Analyzes market demand based on orders and pricing"""
        if not data:
            return {
                'demand_level': 'Unknown',
                'total_orders': 0,
                'avg_price': 0,
                'price_range': {'min': 0, 'max': 0}
            }
            
        total_orders = sum(int(gig.get('orders', '0').replace('K', '000').replace('+', '')) for gig in data)
        prices = [float(gig.get('price', '0').replace('$', '')) for gig in data if gig.get('price')]
        
        if not prices:
            return {
                'demand_level': 'Unknown',
                'total_orders': total_orders,
                'avg_price': 0,
                'price_range': {'min': 0, 'max': 0}
            }
            
        avg_price = sum(prices) / len(prices)
        
        # Demand calculation
        demand_score = min((total_orders / 1000) * 100, 100)  # Normalize to 100%
        
        if demand_score < 30:
            demand = 'Low'
        elif demand_score < 70:
            demand = 'Medium'
        else:
            demand = 'High'
            
        return {
            'demand_level': demand,
            'demand_score': round(demand_score, 2),
            'total_orders': total_orders,
            'avg_price': round(avg_price, 2),
            'price_range': {
                'min': round(min(prices), 2),
                'max': round(max(prices), 2)
            }
        }

    def scrape_fiverr_gigs(self, keyword):
        """Scrapes top 10 Fiverr gigs with detailed metrics"""
        url = f"{self.platforms['fiverr']}{keyword}"
        html = self.safe_request(url)
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        gigs = []
        
        # Find top 10 gigs (adjust selectors as needed)
        for gig in soup.find_all('div', {'class': 'gig-card'})[:10]:
            try:
                # Basic gig info
                title = gig.find('h3').text.strip()
                seller = gig.find('div', {'class': 'seller-name'}).text.strip()
                rating = gig.find('span', {'class': 'rating'}).text.strip() or '0'
                orders = gig.find('span', {'class': 'orders'}).text.strip() or '0'
                price = gig.find('span', {'class': 'price'}).text.strip() or '$0'
                
                # Level and badges (if available)
                level = gig.find('span', {'class': 'level'})
                level = level.text.strip() if level else 'New Seller'
                
                gigs.append({
                    'title': title,
                    'seller': seller,
                    'rating': rating,
                    'orders': orders,
                    'price': price,
                    'level': level
                })
            except AttributeError:
                continue
                
        return gigs

    def generate_market_report(self, keyword):
        """Generates comprehensive market report"""
        print(f"\nAnalyzing market for: {keyword}")
        
        # Get gig data
        gigs = self.scrape_fiverr_gigs(keyword)
        if not gigs:
            print(f"No data found for {keyword}")
            return None
            
        # Analyze market
        competition_metrics = self.analyze_competition(gigs)
        demand_metrics = self.analyze_demand(gigs)
        
        # Calculate opportunity score
        opportunity_score = (
            (100 - competition_metrics['market_saturation']) * 
            demand_metrics['demand_score']
        ) / 100
        
        report = {
            'keyword': keyword,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'market_summary': {
                'competition': competition_metrics,
                'demand': demand_metrics,
                'opportunity_score': round(opportunity_score, 2)
            },
            'top_gigs': gigs
        }
        
        return report

    def save_report(self, report):
        """Saves market analysis report"""
        if not report:
            return
            
        # Create reports directory
        Path('market_reports').mkdir(exist_ok=True)
        
        # Generate filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        keyword_slug = report['keyword'].replace(' ', '_').lower()
        
        # Save detailed JSON report
        json_path = f'market_reports/{keyword_slug}_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        # Create CSV summary
        summary_data = {
            'Keyword': [report['keyword']],
            'Analysis Date': [report['analysis_date']],
            'Competition Level': [report['market_summary']['competition']['competition_level']],
            'Market Saturation': [f"{report['market_summary']['competition']['market_saturation']}%"],
            'Demand Level': [report['market_summary']['demand']['demand_level']],
            'Demand Score': [f"{report['market_summary']['demand']['demand_score']}%"],
            'Average Price': [f"${report['market_summary']['demand']['avg_price']}"],
            'Total Orders': [report['market_summary']['demand']['total_orders']],
            'Opportunity Score': [f"{report['market_summary']['opportunity_score']}%"]
        }
        
        csv_path = f'market_reports/{keyword_slug}_{timestamp}.csv'
        pd.DataFrame(summary_data).to_csv(csv_path, index=False)
        
        print(f"\nReports saved:")
        print(f"Detailed report: {json_path}")
        print(f"Summary: {csv_path}")

def main():
    analyzer = MarketIntelligence()
    
    # Get keywords from user
    print("Enter keywords to analyze (one per line, blank line to finish):")
    keywords = []
    while True:
        keyword = input().strip()
        if not keyword:
            break
        keywords.append(keyword)
    
    # Process each keyword
    for keyword in keywords:
        report = analyzer.generate_market_report(keyword)
        if report:
            analyzer.save_report(report)
            
            # Print quick insights
            print(f"\nQuick Insights for {keyword}:")
            print(f"Competition Level: {report['market_summary']['competition']['competition_level']}")
            print(f"Demand Level: {report['market_summary']['demand']['demand_level']}")
            print(f"Opportunity Score: {report['market_summary']['opportunity_score']}%")
            print(f"Average Price: ${report['market_summary']['demand']['avg_price']}")

if __name__ == "__main__":
    main()
