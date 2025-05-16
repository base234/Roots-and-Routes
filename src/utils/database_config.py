import os
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd

# Load environment variables
load_dotenv()

class SnowflakeConfig:
    def __init__(self):
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        self.database = os.getenv('SNOWFLAKE_DATABASE')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
        self.schema = os.getenv('SNOWFLAKE_SCHEMA')
        self.role = os.getenv('SNOWFLAKE_ROLE')

    def get_connection(self):
        """Create and return a Snowflake connection."""
        try:
            conn = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                database=self.database,
                warehouse=self.warehouse,
                schema=self.schema,
                role=self.role
            )
            return conn
        except Exception as e:
            print(f"Error connecting to Snowflake: {str(e)}")
            return None

    def execute_query(self, query, params=None):
        """Execute a query and return results."""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                conn.close()
                return results
            except Exception as e:
                print(f"Error executing query: {str(e)}")
                return None
        return None

    def execute_many(self, query, params_list):
        """Execute a query multiple times with different parameters."""
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"Error executing multiple queries: {str(e)}")
                return False
        return False

    def write_dataframe(self, df, table_name):
        """Write a pandas DataFrame to a Snowflake table."""
        conn = self.get_connection()
        if conn:
            try:
                success, nchunks, nrows, _ = write_pandas(
                    conn=conn,
                    df=df,
                    table_name=table_name,
                    database=self.database,
                    schema=self.schema
                )
                conn.close()
                return success
            except Exception as e:
                print(f"Error writing DataFrame to Snowflake: {str(e)}")
                return False
        return False

# Create a singleton instance
snowflake_config = SnowflakeConfig()
