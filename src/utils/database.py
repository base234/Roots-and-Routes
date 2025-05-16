import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd
from src.utils.config import SNOWFLAKE_CONFIG, DISCOVERY_CONFIG
from typing import Dict, List, Optional
import time

class SnowflakeConnection:
    _instance = None
    _connection = None
    _last_used = 0
    _timeout = 300  # 5 minutes timeout
    _max_retries = 3
    _retry_delay = 1  # seconds

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_connection(self):
        current_time = time.time()

        # Check if connection exists and is not timed out
        if (self._connection is not None and
            current_time - self._last_used < self._timeout):
            try:
                # Test if connection is still alive
                self._connection.cursor().execute('SELECT 1')
                self._last_used = current_time
                return self._connection
            except Exception as e:
                print(f"Connection test failed: {e}")
                self.close_connection()

        # Create new connection with retries
        for attempt in range(self._max_retries):
            try:
                self._connection = snowflake.connector.connect(
                    user=SNOWFLAKE_CONFIG['user'],
                    password=SNOWFLAKE_CONFIG['password'],
                    account=SNOWFLAKE_CONFIG['account'],
                    warehouse=SNOWFLAKE_CONFIG['warehouse'],
                    database=SNOWFLAKE_CONFIG['database'],
                    schema=SNOWFLAKE_CONFIG['schema'],
                    # Add connection pooling settings
                    connection_timeout=60,
                    session_parameters={
                        'QUERY_TIMEOUT': 300,
                        'STATEMENT_TIMEOUT_IN_SECONDS': 300
                    }
                )
                self._last_used = current_time
                return self._connection
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay)
                else:
                    print("Max retries reached. Could not establish connection.")
                    return None

    def close_connection(self):
        if self._connection is not None:
            try:
                self._connection.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
            finally:
                self._connection = None

    def __del__(self):
        """Destructor to ensure connection is closed when object is destroyed."""
        self.close_connection()

# Initialize the connection when the module is loaded
_connection_manager = SnowflakeConnection.get_instance()

def get_db_connection():
    """Get a connection to the Snowflake database."""
    return SnowflakeConnection.get_instance().get_connection()

print(get_db_connection())

def get_heritage_sites(filters: Optional[Dict] = None) -> List[Dict]:
    """Fetch heritage sites with optional filters."""
    query = """
    SELECT
        h.site_id,
        h.name,
        h.description,
        h.location,
        h.latitude,
        h.longitude,
        h.state,
        h.city,
        h.established_year,
        h.heritage_type,
        h.unesco_status,
        h.risk_level,
        h.health_index,
        h.created_at,
        COUNT(DISTINCT v.visit_date) as visit_days,
        COALESCE(SUM(v.visitor_count), 0) as total_visitors,
        COALESCE(AVG(u.rating), 0) as avg_rating
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
    WHERE 1=1
    """
    params = []

    if filters:
        if 'search_query' in filters:
            query += """ AND (
                CONTAINS(LOWER(h.name), LOWER(%s)) OR
                CONTAINS(LOWER(h.description), LOWER(%s)) OR
                CONTAINS(LOWER(h.location), LOWER(%s)) OR
                CONTAINS(LOWER(h.city), LOWER(%s)) OR
                SOUNDEX(h.name) = SOUNDEX(%s) OR
                SOUNDEX(h.location) = SOUNDEX(%s)
            )"""
            search_term = filters['search_query']
            params.extend([search_term, search_term, search_term, search_term, search_term, search_term])
        if 'type' in filters:
            placeholders = ','.join(['%s'] * len(filters['type']))
            query += f" AND h.heritage_type IN ({placeholders})"
            params.extend(filters['type'])
        if 'state' in filters:
            query += " AND h.state = %s"
            params.append(filters['state'])
        if 'risk_level' in filters:
            placeholders = ','.join(['%s'] * len(filters['risk_level']))
            query += f" AND h.risk_level IN ({placeholders})"
            params.extend(filters['risk_level'])
        if 'year_range' in filters:
            query += " AND h.established_year BETWEEN %s AND %s"
            params.extend(filters['year_range'])
        if 'unesco_status' in filters:
            query += " AND h.unesco_status = %s"
            params.append(filters['unesco_status'])

    query += """
    GROUP BY
        h.site_id,
        h.name,
        h.description,
        h.location,
        h.latitude,
        h.longitude,
        h.state,
        h.city,
        h.established_year,
        h.heritage_type,
        h.unesco_status,
        h.risk_level,
        h.health_index,
        h.created_at
    ORDER BY total_visitors DESC, avg_rating DESC
    LIMIT %s
    """
    params.append(DISCOVERY_CONFIG['search_limit'])

    result = execute_query(query, params)
    if result is None:
        return []

    # Convert the result to a list of dictionaries
    sites = []
    for row in result:
        site = {
            'site_id': row[0],
            'name': row[1],
            'description': row[2],
            'location': row[3],
            'latitude': row[4],
            'longitude': row[5],
            'state': row[6],
            'city': row[7],
            'established_year': row[8],
            'heritage_type': row[9],
            'unesco_status': row[10],
            'risk_level': row[11],
            'health_index': row[12],
            'created_at': row[13],
            'visit_days': row[14],
            'total_visitors': row[15],
            'avg_rating': row[16]
        }
        sites.append(site)

    return sites

def get_site_details(site_id: str) -> Dict:
    """Fetch details of a specific heritage site."""
    query = """
    SELECT
        h.*,
        COUNT(DISTINCT v.visit_date) as visit_days,
        SUM(v.visitor_count) as total_visitors,
        AVG(u.rating) as avg_rating
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
    WHERE h.site_id = %s
    GROUP BY h.site_id, h.name, h.description, h.location, h.latitude, h.longitude,
             h.state, h.city, h.established_year, h.heritage_type, h.unesco_status,
             h.risk_level, h.health_index, h.created_at
    """
    result = execute_query(query, [site_id])
    if result is None or len(result) == 0:
        return None

    row = result[0]
    site = {
        'site_id': row[0],
        'name': row[1],
        'description': row[2],
        'location': row[3],
        'latitude': row[4],
        'longitude': row[5],
        'state': row[6],
        'city': row[7],
        'established_year': row[8],
        'heritage_type': row[9],
        'unesco_status': row[10],
        'risk_level': row[11],
        'health_index': row[12],
        'visit_days': row[13],
        'total_visitors': row[14],
        'avg_rating': row[15]
    }
    return site

def get_visitor_stats(site_id: str) -> List[Dict]:
    """Fetch visitor statistics for a specific heritage site."""
    query = """
    SELECT
        visit_date,
        visitor_count,
        revenue
    FROM VISITOR_STATS
    WHERE site_id = %s
    ORDER BY visit_date DESC
    """
    result = execute_query(query, [site_id])
    if result is None:
        return []

    stats = []
    for row in result:
        stat = {
            'visit_date': row[0],
            'visitor_count': row[1],
            'revenue': row[2]
        }
        stats.append(stat)

    return stats

def get_user_reviews(site_id: str) -> List[Dict]:
    """Fetch user reviews for a specific heritage site."""
    query = """
    SELECT
        u.user_id,
        u.rating,
        u.comment,
        u.review_date
    FROM USER_INTERACTIONS u
    WHERE u.site_id = %s
    ORDER BY u.review_date DESC
    """
    result = execute_query(query, [site_id])
    if result is None:
        return []

    reviews = []
    for row in result:
        review = {
            'user_id': row[0],
            'rating': row[1],
            'comment': row[2],
            'review_date': row[3]
        }
        reviews.append(review)

    return reviews

def execute_query(query, params=None):
    """Execute a query on the Snowflake database."""
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()

        # Execute each permission statement separately
        permission_statements = [
            "USE DATABASE ROOTS_ROUTES",
            "USE SCHEMA PUBLIC",
            "USE WAREHOUSE COMPUTE_WH"
        ]

        for statement in permission_statements:
            cursor.execute(statement)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        # Try to reconnect once
        SnowflakeConnection.get_instance().close_connection()
        conn = get_db_connection()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()

            # Execute each permission statement separately after reconnection
            for statement in permission_statements:
                cursor.execute(statement)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Error executing query after reconnect: {e}")
            return None
    finally:
        cursor.close()

def execute_update(query, params=None):
    """Execute an update query (INSERT, UPDATE, DELETE)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()

def load_dataframe_to_table(df, table_name):
    """Load a pandas DataFrame into a Snowflake table."""
    conn = get_db_connection()
    try:
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name,
            database=SNOWFLAKE_CONFIG['database'],
            schema=SNOWFLAKE_CONFIG['schema']
        )
        return success, nrows
    finally:
        conn.close()

def get_table_schema(table_name):
    """Get the schema of a Snowflake table."""
    conn = get_db_connection()
    try:
        query = f"""
        SELECT
            column_name,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def check_table_exists(table_name):
    """Check if a table exists in the database."""
    conn = get_db_connection()
    try:
        query = f"""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{table_name}'
        """
        result = pd.read_sql(query, conn)
        return result.iloc[0][0] > 0
    finally:
        conn.close()

def create_table_if_not_exists(table_name, columns):
    """Create a table if it doesn't exist."""
    if not check_table_exists(table_name):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            create_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns)}
            )
            """
            cursor.execute(create_query)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

def drop_table_if_exists(table_name):
    """Drop a table if it exists."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_overview_metrics() -> Dict:
    """Fetch overview metrics for the dashboard."""
    query = """
    SELECT
        COUNT(DISTINCT h.site_id) as total_sites,
        SUM(v.visitor_count) as total_visitors,
        SUM(v.revenue) as total_revenue,
        AVG(h.health_index) as avg_health
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    """
    result = execute_query(query)
    if result is None or len(result) == 0:
        return {
            'total_sites': 0,
            'total_visitors': 0,
            'total_revenue': 0,
            'avg_health': 0
        }

    row = result[0]
    metrics = {
        'total_sites': row[0],
        'total_visitors': row[1],
        'total_revenue': row[2],
        'avg_health': row[3]
    }
    return metrics

def get_trending_sites(limit: int = 5) -> List[Dict]:
    """Fetch trending heritage sites."""
    query = """
    SELECT
        h.site_id,
        h.name,
        h.description,
        h.location,
        h.latitude,
        h.longitude,
        h.state,
        h.city,
        h.established_year,
        h.heritage_type,
        h.unesco_status,
        h.risk_level,
        h.health_index,
        COUNT(DISTINCT v.visit_date) as visit_days,
        COALESCE(SUM(v.visitor_count), 0) as total_visitors,
        COALESCE(AVG(u.rating), 0) as avg_rating
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
    GROUP BY
        h.site_id,
        h.name,
        h.description,
        h.location,
        h.latitude,
        h.longitude,
        h.state,
        h.city,
        h.established_year,
        h.heritage_type,
        h.unesco_status,
        h.risk_level,
        h.health_index,
        h.created_at
    ORDER BY total_visitors DESC, avg_rating DESC
    LIMIT %s
    """
    result = execute_query(query, [limit])
    if result is None:
        return []

    sites = []
    for row in result:
        site = {
            'site_id': row[0],
            'name': row[1],
            'description': row[2],
            'location': row[3],
            'latitude': row[4],
            'longitude': row[5],
            'state': row[6],
            'city': row[7],
            'established_year': row[8],
            'heritage_type': row[9],
            'unesco_status': row[10],
            'risk_level': row[11],
            'health_index': row[12],
            'visit_days': row[13],
            'total_visitors': row[14],
            'avg_rating': row[15]
        }
        sites.append(site)

    return sites

def get_visitor_trends() -> List[Dict]:
    """Fetch visitor trends for heritage sites."""
    query = """
    SELECT
        DATE_TRUNC('month', v.visit_date) as month,
        SUM(v.visitor_count) as total_visitors,
        SUM(v.revenue) as total_revenue
    FROM VISITOR_STATS v
    WHERE v.visit_date >= DATEADD(month, -12, CURRENT_DATE())
    GROUP BY month
    ORDER BY month ASC
    """
    result = execute_query(query)
    if result is None:
        return []

    trends = []
    for row in result:
        trend = {
            'month': row[0],
            'total_visitors': row[1] or 0,
            'total_revenue': row[2] or 0
        }
        trends.append(trend)

    return trends

def get_art_forms(filters: Optional[Dict] = None) -> List[Dict]:
    """Fetch art forms with optional filters."""
    query = """
    SELECT
        a.art_form_id,
        a.name,
        a.description,
        a.origin_state,
        a.category,
        a.risk_level,
        a.practitioners_count
    FROM ART_FORMS a
    WHERE 1=1
    """
    params = []

    if filters:
        if 'search_query' in filters:
            query += """ AND (
                CONTAINS(LOWER(a.name), LOWER(%s)) OR
                CONTAINS(LOWER(a.description), LOWER(%s)) OR
                SOUNDEX(a.name) = SOUNDEX(%s) OR
                SOUNDEX(a.origin_state) = SOUNDEX(%s)
            )"""
            search_term = filters['search_query']
            params.extend([search_term, search_term, search_term, search_term])
        if 'category' in filters:
            query += " AND a.category = %s"
            params.append(filters['category'])
        if 'origin_state' in filters:
            query += " AND a.origin_state = %s"
            params.append(filters['origin_state'])
        if 'risk_level' in filters:
            query += " AND a.risk_level = %s"
            params.append(filters['risk_level'])

    query += """
    ORDER BY a.name
    LIMIT %s
    """
    params.append(DISCOVERY_CONFIG['search_limit'])

    result = execute_query(query, params)
    if result is None:
        return []

    art_forms = []
    for row in result:
        art_form = {
            'art_form_id': row[0],
            'name': row[1],
            'description': row[2],
            'origin_state': row[3],
            'category': row[4],
            'risk_level': row[5],
            'practitioners_count': row[6]
        }
        art_forms.append(art_form)

    return art_forms

def get_cultural_events(filters: Optional[Dict] = None) -> List[Dict]:
    """Fetch cultural events with optional filters."""
    query = """
    SELECT
        e.event_id,
        e.name,
        e.description,
        e.start_date,
        e.end_date,
        e.location,
        e.event_type,
        e.organizer
    FROM CULTURAL_EVENTS e
    WHERE 1=1
    """
    params = []

    if filters:
        if 'search_query' in filters:
            query += """ AND (
                CONTAINS(LOWER(e.name), LOWER(%s)) OR
                CONTAINS(LOWER(e.description), LOWER(%s)) OR
                CONTAINS(LOWER(e.location), LOWER(%s)) OR
                SOUNDEX(e.name) = SOUNDEX(%s) OR
                SOUNDEX(e.location) = SOUNDEX(%s) OR
                SOUNDEX(e.organizer) = SOUNDEX(%s)
            )"""
            search_term = filters['search_query']
            params.extend([search_term, search_term, search_term, search_term, search_term, search_term])
        if 'event_type' in filters:
            query += " AND e.event_type = %s"
            params.append(filters['event_type'])
        if 'location' in filters:
            query += " AND e.location = %s"
            params.append(filters['location'])
        if 'organizer' in filters:
            query += " AND e.organizer = %s"
            params.append(filters['organizer'])

    query += """
    ORDER BY e.start_date DESC
    LIMIT %s
    """
    params.append(DISCOVERY_CONFIG['search_limit'])

    result = execute_query(query, params)
    if result is None:
        return []

    events = []
    for row in result:
        event = {
            'event_id': row[0],
            'name': row[1],
            'description': row[2],
            'start_date': row[3],
            'end_date': row[4],
            'location': row[5],
            'event_type': row[6],
            'organizer': row[7]
        }
        events.append(event)

    return events

def get_street_view(latitude: float, longitude: float) -> Dict:
    """Fetch street view for a heritage site."""
    query = """
    SELECT
        s.street_view_id,
        s.image_url,
        s.capture_date
    FROM STREET_VIEWS s
    WHERE s.latitude = %s AND s.longitude = %s
    ORDER BY s.capture_date DESC
    LIMIT 1
    """
    result = execute_query(query, [latitude, longitude])
    if result is None or len(result) == 0:
        return None

    row = result[0]
    street_view = {
        'street_view_id': row[0],
        'image_url': row[1],
        'capture_date': row[2]
    }
    return street_view

def get_site_image(site_id: str) -> Dict:
    """Fetch image for a heritage site."""
    query = """
    SELECT
        i.image_id,
        i.image_url,
        i.capture_date
    FROM SITE_IMAGES i
    WHERE i.site_id = %s
    ORDER BY i.capture_date DESC
    LIMIT 1
    """
    result = execute_query(query, [site_id])
    if result is None or len(result) == 0:
        return None

    row = result[0]
    image = {
        'image_id': row[0],
        'image_url': row[1],
        'capture_date': row[2]
    }
    return image

def get_related_sites(site_id: str) -> List[Dict]:
    """Fetch related heritage sites."""
    query = """
    SELECT
        h.*,
        COUNT(DISTINCT v.visit_date) as visit_days,
        SUM(v.visitor_count) as total_visitors,
        AVG(u.rating) as avg_rating
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
    WHERE h.site_id != %s
    GROUP BY h.site_id, h.name, h.description, h.location, h.latitude, h.longitude,
             h.state, h.city, h.established_year, h.heritage_type, h.unesco_status,
             h.risk_level, h.health_index, h.created_at, h.updated_at
    ORDER BY total_visitors DESC, avg_rating DESC
    LIMIT 5
    """
    result = execute_query(query, [site_id])
    if result is None:
        return []

    sites = []
    for row in result:
        site = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'location': row[3],
            'latitude': row[4],
            'longitude': row[5],
            'state': row[6],
            'city': row[7],
            'established_year': row[8],
            'heritage_type': row[9],
            'unesco_status': row[10],
            'risk_level': row[11],
            'health_index': row[12],
            'visit_days': row[13],
            'total_visitors': row[14],
            'avg_rating': row[15]
        }
        sites.append(site)

    return sites

def get_site_health(site_id: str) -> Dict:
    """Fetch health metrics for a heritage site."""
    query = """
    SELECT
        h.health_index,
        h.risk_level,
        COUNT(DISTINCT v.visit_date) as visit_days,
        SUM(v.visitor_count) as total_visitors,
        AVG(u.rating) as avg_rating
    FROM HERITAGE_SITES h
    LEFT JOIN VISITOR_STATS v ON h.site_id = v.site_id
    LEFT JOIN USER_INTERACTIONS u ON h.site_id = u.site_id
    WHERE h.site_id = %s
    GROUP BY h.health_index, h.risk_level
    """
    result = execute_query(query, [site_id])
    if result is None or len(result) == 0:
        return {
            'health_index': 0,
            'risk_level': 'Unknown',
            'visit_days': 0,
            'total_visitors': 0,
            'avg_rating': 0
        }

    row = result[0]
    health = {
        'health_index': row[0],
        'risk_level': row[1],
        'visit_days': row[2],
        'total_visitors': row[3],
        'avg_rating': row[4]
    }
    return health

def get_site_revenue(site_id: str) -> Dict:
    """Fetch revenue metrics for a heritage site."""
    query = """
    SELECT
        SUM(v.revenue) as total_revenue,
        AVG(v.revenue) as avg_revenue,
        COUNT(DISTINCT v.visit_date) as visit_days
    FROM VISITOR_STATS v
    WHERE v.site_id = %s
    """
    result = execute_query(query, [site_id])
    if result is None or len(result) == 0:
        return {
            'total_revenue': 0,
            'avg_revenue': 0,
            'visit_days': 0
        }

    row = result[0]
    revenue = {
        'total_revenue': row[0],
        'avg_revenue': row[1],
        'visit_days': row[2]
    }
    return revenue

def get_site_visitors(site_id: str) -> Dict:
    """Fetch visitor metrics for a heritage site."""
    query = """
    SELECT
        SUM(v.visitor_count) as total_visitors,
        AVG(v.visitor_count) as avg_visitors,
        COUNT(DISTINCT v.visit_date) as visit_days
    FROM VISITOR_STATS v
    WHERE v.site_id = %s
    """
    result = execute_query(query, [site_id])
    if result is None or len(result) == 0:
        return {
            'total_visitors': 0,
            'avg_visitors': 0,
            'visit_days': 0
        }

    row = result[0]
    visitors = {
        'total_visitors': row[0],
        'avg_visitors': row[1],
        'visit_days': row[2]
    }
    return visitors

def get_site_ratings(site_id: str) -> Dict:
    """Fetch rating metrics for a heritage site."""
    query = """
    SELECT
        AVG(u.rating) as avg_rating,
        COUNT(u.rating) as total_ratings,
        MIN(u.rating) as min_rating,
        MAX(u.rating) as max_rating
    FROM USER_INTERACTIONS u
    WHERE u.site_id = %s
    """
    result = execute_query(query, [site_id])
    if result is None or len(result) == 0:
        return {
            'avg_rating': 0,
            'total_ratings': 0,
            'min_rating': 0,
            'max_rating': 0
        }

    row = result[0]
    ratings = {
        'avg_rating': row[0],
        'total_ratings': row[1],
        'min_rating': row[2],
        'max_rating': row[3]
    }
    return ratings

def get_site_comments(site_id: str) -> List[Dict]:
    """Fetch comments for a heritage site."""
    query = """
    SELECT
        u.user_id,
        u.comment,
        u.review_date
    FROM USER_INTERACTIONS u
    WHERE u.site_id = %s AND u.comment IS NOT NULL
    ORDER BY u.review_date DESC
    """
    result = execute_query(query, [site_id])
    if result is None:
        return []

    comments = []
    for row in result:
        comment = {
            'user_id': row[0],
            'comment': row[1],
            'review_date': row[2]
        }
        comments.append(comment)

    return comments

def get_site_photos(site_id: str) -> List[Dict]:
    """Fetch photos for a heritage site."""
    query = """
    SELECT
        p.photo_id,
        p.image_url,
        p.capture_date
    FROM SITE_PHOTOS p
    WHERE p.site_id = %s
    ORDER BY p.capture_date DESC
    """
    result = execute_query(query, [site_id])
    if result is None:
        return []

    photos = []
    for row in result:
        photo = {
            'photo_id': row[0],
            'image_url': row[1],
            'capture_date': row[2]
        }
        photos.append(photo)

    return photos

def get_site_videos(site_id: str) -> List[Dict]:
    """Fetch videos for a heritage site."""
    query = """
    SELECT
        v.video_id,
        v.video_url,
        v.title,
        v.description,
        v.upload_date
    FROM SITE_VIDEOS v
    WHERE v.site_id = %s
    ORDER BY v.upload_date DESC
    """
    result = execute_query(query, [site_id])
    if result is None:
        return []

    videos = []
    for row in result:
        video = {
            'video_id': row[0],
            'video_url': row[1],
            'title': row[2],
            'description': row[3],
            'upload_date': row[4]
        }
        videos.append(video)

    return videos

def get_site_articles(site_id: str) -> List[Dict]:
    """Fetch articles for a heritage site."""
    query = """
    SELECT
        a.article_id,
        a.title,
        a.content,
        a.author,
        a.publication_date,
        a.source_url
    FROM SITE_ARTICLES a
    WHERE a.site_id = %s
    ORDER BY a.publication_date DESC
    """
    result = execute_query(query, [site_id])
    if result is None:
        return []

    articles = []
    for row in result:
        article = {
            'article_id': row[0],
            'title': row[1],
            'content': row[2],
            'author': row[3],
            'publication_date': row[4],
            'source_url': row[5]
        }
        articles.append(article)

    return articles

def get_site_resources(site_id: str) -> List[Dict]:
    """Fetch resources for a heritage site."""
    query = """
    SELECT
        r.resource_id,
        r.title,
        r.description,
        r.resource_type,
        r.file_url,
        r.upload_date
    FROM SITE_RESOURCES r
    WHERE r.site_id = %s
    ORDER BY r.upload_date DESC
    """
    result = execute_query(query, [site_id])
    if result is None:
        return []

    resources = []
    for row in result:
        resource = {
            'resource_id': row[0],
            'title': row[1],
            'description': row[2],
            'resource_type': row[3],
            'file_url': row[4],
            'upload_date': row[5]
        }
        resources.append(resource)

    return resources

def get_site_events(site_id: str) -> List[Dict]:
    """Fetch events for a heritage site."""
    query = """
    SELECT
        e.event_id,
        e.name,
        e.description,
        e.start_date,
        e.end_date,
        e.organizer,
        e.event_type,
        e.venue
    FROM SITE_EVENTS e
    WHERE e.site_id = %s
    ORDER BY e.start_date DESC
    """
    result = execute_query(query, [site_id])
    if result is None:
        return []

    events = []
    for row in result:
        event = {
            'event_id': row[0],
            'name': row[1],
            'description': row[2],
            'start_date': row[3],
            'end_date': row[4],
            'organizer': row[5],
            'event_type': row[6],
            'venue': row[7]
        }
        events.append(event)

    return events
