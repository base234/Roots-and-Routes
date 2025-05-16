import openai
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class AIService:
    def __init__(self):
        self.model = "gpt-4-turbo-preview"

    def generate_site_description(self, site_data: Dict) -> str:
        """Generate an enhanced description for a heritage site using GPT-4."""
        prompt = f"""
        Write an engaging and informative description for the following heritage site:
        Name: {site_data['name']}
        Location: {site_data['location']}, {site_data['state']}
        Type: {site_data['heritage_type']}
        Established: {site_data['established_year']}
        Current Description: {site_data['description']}

        The description should:
        1. Be engaging and informative
        2. Highlight historical significance
        3. Include cultural context
        4. Be suitable for a tourism website
        5. Be between 150-200 words
        """

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )

        return response.choices[0].message.content

    def get_similar_sites(self, site_data: Dict, all_sites: List[Dict], top_n: int = 3) -> List[Dict]:
        """Find similar heritage sites using GPT-4 for semantic understanding."""
        prompt = f"""
        Given the following heritage site:
        Name: {site_data['name']}
        Location: {site_data['location']}, {site_data['state']}
        Type: {site_data['heritage_type']}
        Description: {site_data['description']}

        And these potential similar sites:
        {[f"Name: {site['name']}, Type: {site['heritage_type']}, Location: {site['location']}" for site in all_sites]}

        Return the indices of the top {top_n} most similar sites based on:
        1. Cultural significance
        2. Architectural style
        3. Historical period
        4. Geographic proximity
        5. Visitor experience

        Return only the indices as a comma-separated list.
        """

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50
        )

        # Parse the response to get indices
        indices = [int(idx.strip()) for idx in response.choices[0].message.content.split(',')]
        return [all_sites[idx] for idx in indices if idx < len(all_sites)]

    def analyze_review_sentiment(self, review: str) -> Dict:
        """Analyze the sentiment and extract key points from a review."""
        prompt = f"""
        Analyze the following review of a heritage site:
        "{review}"

        Provide a JSON response with:
        1. Overall sentiment (positive/negative/neutral)
        2. Sentiment score (0-1)
        3. Key points mentioned
        4. Suggested improvements (if any)
        """

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )

        return response.choices[0].message.content

    def generate_tour_plan(self, site_data: Dict, duration: str = "1 day") -> Dict:
        """Generate a detailed tour plan for a heritage site."""
        prompt = f"""
        Create a detailed tour plan for {site_data['name']} with a duration of {duration}.
        Site details:
        Location: {site_data['location']}, {site_data['state']}
        Type: {site_data['heritage_type']}
        Description: {site_data['description']}

        Include:
        1. Recommended time slots
        2. Must-see attractions
        3. Photography spots
        4. Rest areas
        5. Local tips
        """

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )

        return response.choices[0].message.content

    def translate_content(self, text: str, target_language: str) -> str:
        """Translate content to the target language."""
        prompt = f"""
        Translate the following text to {target_language}:
        "{text}"

        Maintain the original tone and cultural context while ensuring natural language in the target language.
        """

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )

        return response.choices[0].message.content

    def generate_site_recommendations(self, user_preferences: Dict, all_sites: List[Dict], top_n: int = 5) -> List[Dict]:
        """Generate personalized site recommendations based on user preferences."""
        prompt = f"""
        Given the following user preferences:
        {user_preferences}

        And these available heritage sites:
        {[f"Name: {site['name']}, Type: {site['heritage_type']}, Location: {site['location']}" for site in all_sites]}

        Recommend the top {top_n} most suitable sites based on:
        1. User preferences
        2. Site characteristics
        3. Cultural significance
        4. Accessibility
        5. Seasonal factors

        Return the indices of recommended sites as a comma-separated list.
        """

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )

        # Parse the response to get indices
        indices = [int(idx.strip()) for idx in response.choices[0].message.content.split(',')]
        return [all_sites[idx] for idx in indices if idx < len(all_sites)]
