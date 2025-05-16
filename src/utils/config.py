import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Snowflake configuration
SNOWFLAKE_CONFIG = {
    'user': os.getenv('SNOWFLAKE_USER', ''),
    'password': os.getenv('SNOWFLAKE_PASSWORD', ''),
    'account': os.getenv('SNOWFLAKE_ACCOUNT', ''),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', ''),
    'database': os.getenv('SNOWFLAKE_DATABASE', ''),
    'schema': os.getenv('SNOWFLAKE_SCHEMA', '')
}

# OpenAI API configuration
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')

# Unsplash API configuration
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', 'your_access_key_here')
UNSPLASH_SECRET_KEY = os.getenv('UNSPLASH_SECRET_KEY', 'your_secret_key_here')
UNSPLASH_REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"  # Default redirect URI for desktop apps

# Application Settings
APP_CONFIG = {
    'title': 'Roots & Routes',
    'description': 'Discover and explore cultural heritage sites',
    'theme': {
        'primaryColor': '#1E88E5',
        'backgroundColor': '#FFFFFF',
        'secondaryBackgroundColor': '#F0F2F6',
        'textColor': '#262730',
        'font': 'sans serif'
    }
}

# Dashboard Settings
DASHBOARD_CONFIG = {
    'refresh_interval': 300,  # 5 minutes
    'max_trending_sites': 5,
    'default_map_zoom': 5,
    'default_map_center': [20.5937, 78.9629],  # Center of India
    'metrics': {
        'total_sites': 0,
        'total_visitors': 0,
        'total_revenue': 0,
        'avg_health': 0
    }
}

# Cultural Discovery Settings
DISCOVERY_CONFIG = {
    'search_limit': 10,
    'filter_options': {
        'heritage_types': ['Cultural', 'Natural', 'Mixed'],
        'risk_levels': ['Low', 'Medium', 'High'],
        'seasons': ['Spring', 'Summer', 'Monsoon', 'Autumn', 'Winter']
    }
}

# Tourism Analytics Settings
ANALYTICS_CONFIG = {
    'prediction_horizon': 30,  # days
    'seasonal_periods': 12,  # months
    'confidence_interval': 0.95
}

# Heritage Health Settings
HEALTH_CONFIG = {
    'health_thresholds': {
        'critical': 30,
        'high': 50,
        'medium': 70,
        'low': 90
    },
    'monitoring_interval': 24  # hours
}

# Admin Portal Settings
ADMIN_CONFIG = {
    'session_timeout': 3600,  # 1 hour
    'max_login_attempts': 3,
    'password_min_length': 8,
    'log_retention_days': 30
}

# Pipeline Settings
PIPELINE_CONFIG = {
    'data_refresh_interval': 86400,  # 24 hours
    'batch_size': 1000,
    'max_retries': 3,
    'timeout': 300,  # 5 minutes
    'metrics': {
        'total_sites': 0,
        'total_visitors': 0,
        'total_revenue': 0
    }
}

# Error Messages
ERROR_MESSAGES = {
    'database_connection': 'Unable to connect to the database. Please check your credentials.',
    'api_error': 'Error accessing external API. Please try again later.',
    'invalid_input': 'Invalid input provided. Please check your input and try again.',
    'unauthorized': 'You are not authorized to perform this action.',
    'not_found': 'The requested resource was not found.',
    'query_execution': 'Error executing the query.',
    'data_not_found': 'No data found.'
}

# Success Messages
SUCCESS_MESSAGES = {
    'data_updated': 'Data successfully updated.',
    'operation_complete': 'Operation completed successfully.',
    'login_success': 'Login successful.',
    'logout_success': 'Logout successful.',
    'data_loaded': 'Data loaded successfully.',
    'query_executed': 'Query executed successfully.'
}

# Page Configuration
PAGES = {
    'Home': '🏠',
    'Cultural Discovery': '🔍',
    'Tourism Analytics': '📊',
    'Interactive Maps': '🗺️',
    'Cultural Stories': '📚',
    'Heritage Health': '🏛️',
    'Admin Portal': '🔐',
    'Explore': '🗺️',
    'Map View': '🗺️',
    'About': 'ℹ️'
}
