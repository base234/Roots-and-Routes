import streamlit as st
from src.utils.database import get_user_reviews
from src.services.ai_service import AIService
import json

def render_reviews(site_id):
    """Render the reviews section with AI-powered sentiment analysis."""
    # Get reviews
    reviews = get_user_reviews(site_id)

    if not reviews:
        st.info("Be the first to review this site!")
        return

    # Initialize AI service
    ai_service = AIService()

    # Display each review with sentiment analysis
    for review in reviews:
        with st.container():
            # Analyze review sentiment
            sentiment_analysis = json.loads(ai_service.analyze_review_sentiment(review['review_text']))

            # Create columns for review content and sentiment
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**User {review['user_id']}**")
                st.markdown(f"*{review['interaction_date']}*")
                st.markdown(review['review_text'])

            with col2:
                # Display sentiment with color coding
                sentiment = sentiment_analysis['sentiment']
                score = sentiment_analysis['sentiment_score']

                if sentiment == 'positive':
                    st.success(f"Positive ({score:.2f})")
                elif sentiment == 'negative':
                    st.error(f"Negative ({score:.2f})")
                else:
                    st.info(f"Neutral ({score:.2f})")

                # Display key points
                st.markdown("**Key Points:**")
                for point in sentiment_analysis['key_points']:
                    st.markdown(f"- {point}")

            st.divider()
