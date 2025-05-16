import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from utils.database_config import snowflake_config
from utils.data_loader import DataLoader

def init_database():
    """Initialize the database and load sample data."""
    try:
        # Read and execute the schema SQL
        schema_path = os.path.join(project_root, 'src', 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        # Split the SQL into individual statements
        statements = schema_sql.split(';')

        # Execute each statement
        for statement in statements:
            if statement.strip():
                snowflake_config.execute_query(statement)

        print("Database schema created successfully!")

        # Initialize data loader
        loader = DataLoader()

        # Load sample data
        loader.load_all_sample_data()

        print("Database initialization completed successfully!")

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
