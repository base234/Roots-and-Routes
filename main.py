import streamlit as st
import pandas as pd
from config import get_snowflake_session

def main():
    st.title("🚀 Snowflake ETL Pipeline App")

    try:
        # Get Snowflake session
        session = get_snowflake_session()

        # First check what tables exist in the current schema
        st.subheader("Checking Available Tables...")
        tables_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = current_schema()
        """
        available_tables = session.sql(tables_query).collect()

        if not available_tables:
            st.error("No tables found in the current schema.")
            st.info("Please ensure you have the correct schema selected and tables created.")
            return

        # Display available tables
        st.subheader("Available Tables")
        table_names = [table['TABLE_NAME'] for table in available_tables]
        st.write(table_names)

        # Let user select a table
        selected_table = st.selectbox(
            "Select a table to view",
            options=table_names,
            index=0
        )

        if selected_table:
            # Show the selected table
            st.header(f"Table: {selected_table}")
            try:
                df = session.table(selected_table).to_pandas()
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error loading table {selected_table}: {str(e)}")
                st.info("Please check if you have the necessary permissions to access this table.")

    except Exception as e:
        st.error(f"Error connecting to Snowflake: {str(e)}")
        st.info("Please check your Snowflake connection settings in the config file.")

    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main()
