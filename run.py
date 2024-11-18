import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta
import json
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import matplotlib.pyplot as plt
import seaborn as sns

class AdvancedMarketIntelligence:
    def __init__(self):
        self.setup_browser()
        self.metrics_cache = {}
        self.historical_data = {}
        
    def setup_browser(self):
        """Initialize headless browser for dynamic content"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def calculate_advanced_metrics(self, gigs_data):
        """Calculate comprehensive market metrics"""
        metrics = {
            'basic_stats': self.calculate_basic_stats(gigs_data),
            'market_dynamics': self.analyze_market_dynamics(gigs_data),
            'competitor_analysis': self.analyze_competitors(gigs_data),
            'price_analysis': self.analyze_pricing(gigs_data),
            'quality_metrics': self.analyze_quality_metrics(gigs_data),
            'market_trends': self.analyze_trends(gigs_data)
        }
        return metrics
    
    def calculate_basic_stats(self, gigs_data):
        """Calculate basic statistical metrics"""
        prices = [float(gig['price'].replace('$', '')) for gig in gigs_data]
        orders = [int(gig['orders'].replace('K', '000').replace('+', '')) for gig in gigs_data]
        
        return {
            'price_stats': {
                'mean': np.mean(prices),
                'median': np.median(prices),
                'std': np.std(prices),
                'quartiles': np.percentile(prices, [25, 50, 75])
            },
            'order_stats': {
                'mean': np.mean(orders),
                'median': np.median(orders),
                'total': sum(orders)
            }
        }
    
    def analyze_market_dynamics(self, gigs_data):
        """Analyze market dynamics and competition"""
        seller_levels = [gig['level'] for gig in gigs_data]
        total_sellers = len(gigs_data)
        
        level_distribution = {
            level: seller_levels.count(level) / total_sellers * 100
            for level in set(seller_levels)
        }
        
        # Calculate market concentration (HHI)
        market_shares = [
            (int(gig['orders'].replace('K', '000').replace('+', '')) / 
             sum(int(g['orders'].replace('K', '000').replace('+', '')) for g in gigs_data)) * 100
            for gig in gigs_data
        ]
        hhi = sum(share ** 2 for share in market_shares)
        
        return {
            'level_distribution': level_distribution,
            'market_concentration': {
                'hhi': hhi,
                'concentration_level': 'High' if hhi > 2500 else 'Moderate' if hhi > 1500 else 'Low'
            }
        }
    
    def analyze_competitors(self, gigs_data):
        """Detailed competitor analysis"""
        response_times = [random.uniform(1, 24) for _ in gigs_data]  # Simulated data
        ratings = [float(gig['rating']) for gig in gigs_data]
        
        return {
            'response_metrics': {
                'avg_response_time': np.mean(response_times),
                'fast_responders': sum(1 for t in response_times if t < 3)
            },
            'quality_metrics': {
                'avg_rating': np.mean(ratings),
                'rating_distribution': np.histogram(ratings, bins=5)[0].tolist()
            }
        }
    
    def analyze_pricing(self, gigs_data):
        """Advanced price analysis"""
        prices = [float(gig['price'].replace('$', '')) for gig in gigs_data]
        
        return {
            'price_segments': {
                'budget': sum(1 for p in prices if p < np.percentile(prices, 33)),
                'mid_range': sum(1 for p in prices if np.percentile(prices, 33) <= p < np.percentile(prices, 66)),
                'premium': sum(1 for p in prices if p >= np.percentile(prices, 66))
            },
            'price_elasticity': self.calculate_price_elasticity(gigs_data)
        }
    
    def analyze_quality_metrics(self, gigs_data):
        """Analysis of quality indicators"""
        return {
            'service_quality': self.calculate_service_quality(gigs_data),
            'reliability_score': self.calculate_reliability_score(gigs_data)
        }
    
    def analyze_trends(self, gigs_data):
        """Market trend analysis"""
        # Simulate historical data for trend analysis
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        trend_data = {
            'dates': dates.strftime('%Y-%m-%d').tolist(),
            'avg_prices': self.simulate_trend_data(30),
            'total_orders': self.simulate_trend_data(30),
            'active_sellers': self.simulate_trend_data(30)
        }
        return trend_data
    
    def generate_visualizations(self, metrics, keyword):
        """Generate comprehensive market visualizations"""
        Path('visualizations').mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Price Distribution
        self.create_price_distribution_plot(metrics, keyword, timestamp)
        
        # Market Trends
        self.create_market_trends_plot(metrics, keyword, timestamp)
        
        # Competitor Analysis
        self.create_competitor_analysis_plot(metrics, keyword, timestamp)
        
        # Market Segments
        self.create_market_segments_plot(metrics, keyword, timestamp)
        
        return f"visualizations/{keyword}_{timestamp}"
    
    def create_price_distribution_plot(self, metrics, keyword, timestamp):
        """Create price distribution visualization"""
        fig = go.Figure()
        prices = metrics['basic_stats']['price_stats']
        
        fig.add_trace(go.Box(
            y=prices['quartiles'],
            name='Price Distribution',
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ))
        
        fig.update_layout(
            title=f'Price Distribution Analysis - {keyword}',
            yaxis_title='Price ($)',
            template='plotly_white'
        )
        
        fig.write_html(f'visualizations/{keyword}_price_dist_{timestamp}.html')
    
    def create_market_trends_plot(self, metrics, keyword, timestamp):
        """Create market trends visualization"""
        trends = metrics['market_trends']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trends['dates'],
            y=trends['avg_prices'],
            name='Average Price',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=trends['dates'],
            y=trends['total_orders'],
            name='Total Orders',
            mode='lines+markers',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=f'Market Trends Analysis - {keyword}',
            yaxis=dict(title='Average Price ($)'),
            yaxis2=dict(title='Total Orders', overlaying='y', side='right'),
            template='plotly_white'
        )
        
        fig.write_html(f'visualizations/{keyword}_trends_{timestamp}.html')
    
    def create_report(self, keyword, metrics, visualization_path):
        """Generate comprehensive market report"""
        report = {
            'keyword': keyword,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'market_metrics': metrics,
            'visualization_path': visualization_path,
            'market_summary': self.generate_market_summary(metrics),
            'recommendations': self.generate_recommendations(metrics)
        }
        
        return report
    
    def save_report(self, report):
        """Save report in multiple formats"""
        Path('reports').mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        keyword_slug = report['keyword'].replace(' ', '_').lower()
        
        # Save detailed JSON report
        json_path = f'reports/{keyword_slug}_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Create Excel report with multiple sheets
        excel_path = f'reports/{keyword_slug}_{timestamp}.xlsx'
        with pd.ExcelWriter(excel_path) as writer:
            # Market Summary
            pd.DataFrame([report['market_summary']]).to_excel(writer, sheet_name='Market Summary', index=False)
            
            # Detailed Metrics
            metrics_df = pd.DataFrame(report['market_metrics']['basic_stats'])
            metrics_df.to_excel(writer, sheet_name='Detailed Metrics', index=True)
            
            # Recommendations
            pd.DataFrame(report['recommendations']).to_excel(writer, sheet_name='Recommendations', index=False)
        
        return {
            'json_report': json_path,
            'excel_report': excel_path,
            'visualizations': report['visualization_path']
        }

def main():
    analyzer = AdvancedMarketIntelligence()
    
    print("Advanced Market Intelligence System")
    print("==================================")
    
    while True:
        keyword = input("\nEnter keyword to analyze (or 'quit' to exit): ").strip()
        if keyword.lower() == 'quit':
            break
            
        print(f"\nAnalyzing market for: {keyword}")
        print("This may take a few minutes...")
        
        try:
            # Collect and analyze data
            gigs_data = analyzer.scrape_market_data(keyword)
            metrics = analyzer.calculate_advanced_metrics(gigs_data)
            
            # Generate visualizations
            viz_path = analyzer.generate_visualizations(metrics, keyword)
            
            # Create and save report
            report = analyzer.create_report(keyword, metrics, viz_path)
            report_paths = analyzer.save_report(report)
            
            print("\nAnalysis complete!")
            print("\nReport locations:")
            print(f"Detailed report: {report_paths['json_report']}")
            print(f"Excel report: {report_paths['excel_report']}")
            print(f"Visualizations: {report_paths['visualizations']}")
            
        except Exception as e:
            print(f"\nError analyzing {keyword}: {str(e)}")
            print("Please try again with a different keyword.")

if __name__ == "__main__":
    main()
