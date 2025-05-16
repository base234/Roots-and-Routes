import pandas as pd
import json
from datetime import datetime, timedelta
import random
import snowflake.connector
from src.utils.database_config import snowflake_config

class DataLoader:
    def __init__(self):
        self.sf = snowflake_config

    def load_heritage_sites(self, data_file):
        """Load heritage sites data into Snowflake."""
        try:
            df = pd.read_csv(data_file)
            return self.sf.write_dataframe(df, 'heritage_sites')
        except Exception as e:
            print(f"Error loading heritage sites: {str(e)}")
            return False

    def load_art_forms(self, data_file):
        """Load traditional art forms data into Snowflake."""
        try:
            df = pd.read_csv(data_file)
            return self.sf.write_dataframe(df, 'traditional_art_forms')
        except Exception as e:
            print(f"Error loading art forms: {str(e)}")
            return False

    def generate_visitor_statistics(self, start_date, end_date):
        """Generate and load visitor statistics data."""
        try:
            # Generate date range
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')

            # Get all site IDs
            sites_query = "SELECT site_id FROM heritage_sites"
            sites = self.sf.execute_query(sites_query)

            # Generate statistics
            stats_data = []
            for site_id in sites:
                for date in date_range:
                    # Generate random visitor count (100-1000)
                    visitors = random.randint(100, 1000)
                    # Calculate revenue (₹100 per visitor)
                    revenue = visitors * 100

                    stats_data.append({
                        'site_id': site_id[0],
                        'visit_date': date.strftime('%Y-%m-%d'),
                        'visitor_count': visitors,
                        'revenue': revenue
                    })

            # Convert to DataFrame and load
            df = pd.DataFrame(stats_data)
            return self.sf.write_dataframe(df, 'visitor_statistics')
        except Exception as e:
            print(f"Error generating visitor statistics: {str(e)}")
            return False

    def generate_user_interactions(self, num_interactions=44):
        """Generate and load user interactions data."""
        try:
            # Get all site IDs
            sites_query = "SELECT site_id FROM heritage_sites"
            sites = self.sf.execute_query(sites_query)

            # Generate interactions
            interactions_data = []
            for _ in range(num_interactions):
                site_id = random.choice(sites)[0]
                user_id = f"user_{random.randint(1, 100)}"
                interaction_type = random.choice(['visit', 'review', 'rating'])
                rating = random.randint(1, 5) if interaction_type in ['review', 'rating'] else None
                review_text = f"Great experience at this heritage site!" if interaction_type == 'review' else None

                interactions_data.append({
                    'user_id': user_id,
                    'site_id': site_id,
                    'interaction_type': interaction_type,
                    'rating': rating,
                    'review_text': review_text
                })

            # Convert to DataFrame and load
            df = pd.DataFrame(interactions_data)
            return self.sf.write_dataframe(df, 'user_interactions')
        except Exception as e:
            print(f"Error generating user interactions: {str(e)}")
            return False

    def generate_cultural_events(self, num_events=30):
        """Generate and load cultural events data."""
        try:
            # Get all site IDs
            sites_query = "SELECT site_id FROM heritage_sites"
            sites = self.sf.execute_query(sites_query)

            # Generate events
            events_data = []
            event_types = ['Festival', 'Exhibition', 'Workshop', 'Performance', 'Tour']

            for _ in range(num_events):
                site_id = random.choice(sites)[0]
                start_date = datetime.now() + timedelta(days=random.randint(1, 365))
                end_date = start_date + timedelta(days=random.randint(1, 7))

                events_data.append({
                    'name': f"{random.choice(event_types)} at Heritage Site",
                    'description': "Join us for this cultural event!",
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'location': "Main Venue",
                    'site_id': site_id
                })

            # Convert to DataFrame and load
            df = pd.DataFrame(events_data)
            return self.sf.write_dataframe(df, 'cultural_events')
        except Exception as e:
            print(f"Error generating cultural events: {str(e)}")
            return False

    def generate_health_index(self):
        """Generate and load heritage health index data."""
        try:
            # Get all site IDs
            sites_query = "SELECT site_id FROM heritage_sites"
            sites = self.sf.execute_query(sites_query)

            # Generate health index data
            health_data = []
            for site_id in sites:
                health_data.append({
                    'site_id': site_id[0],
                    'assessment_date': datetime.now().strftime('%Y-%m-%d'),
                    'structural_condition': random.randint(1, 5),
                    'preservation_status': random.randint(1, 5),
                    'visitor_impact': random.randint(1, 5),
                    'environmental_factors': random.randint(1, 5),
                    'recommendations': "Regular maintenance and monitoring required."
                })

            # Convert to DataFrame and load
            df = pd.DataFrame(health_data)
            return self.sf.write_dataframe(df, 'heritage_health_index')
        except Exception as e:
            print(f"Error generating health index: {str(e)}")
            return False

    def load_all_sample_data(self):
        """Load all sample data into the database."""
        # Load heritage sites
        self.load_heritage_sites('data/heritage_sites.csv')

        # Load art forms
        self.load_art_forms('data/art_forms.csv')

        # Generate and load other data
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()

        self.generate_visitor_statistics(start_date, end_date)
        self.generate_user_interactions()
        self.generate_cultural_events()
        self.generate_health_index()

        print("All sample data loaded successfully!")
