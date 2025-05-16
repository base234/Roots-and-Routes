import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import time
import os
import json
import uuid
import ipaddress
from utils.database import execute_query, execute_update
from utils.config import ADMIN_CONFIG

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_session(username, ip_address):
    """Create a new admin session."""
    session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=8)

    query = """
    INSERT INTO USER_SESSIONS (
        session_id, username, ip_address, expires_at
    ) VALUES (%s, %s, %s, %s)
    """
    execute_update(query, [session_id, username, ip_address, expires_at])
    return session_id

def validate_session(session_id, ip_address):
    """Validate an admin session."""
    query = """
    SELECT username, expires_at
    FROM USER_SESSIONS
    WHERE session_id = %s AND ip_address = %s
    """
    result = execute_query(query, [session_id, ip_address])

    if result.empty:
        return False

    session = result.iloc[0]
    if datetime.now() > session['expires_at']:
        # Session expired
        query = "DELETE FROM USER_SESSIONS WHERE session_id = %s"
        execute_update(query, [session_id])
        return False

    return True

def log_activity(username, action, status="SUCCESS"):
    """Log admin activity."""
    query = """
    INSERT INTO USER_ACTIVITY_LOG (
        username, action, ip_address, user_agent, status
    ) VALUES (%s, %s, %s, %s, %s)
    """
    execute_update(query, [
        username,
        action,
        st.session_state.get('ip_address'),
        st.session_state.get('user_agent'),
        status
    ])

def is_ip_allowed(ip_address):
    """Check if IP address is allowed to access admin portal."""
    try:
        # Check if IP is in allowed range
        ip = ipaddress.ip_address(ip_address)
        allowed_ranges = [
            ipaddress.ip_network('10.0.0.0/8'),
            ipaddress.ip_network('172.16.0.0/12'),
            ipaddress.ip_network('192.168.0.0/16')
        ]

        return any(ip in network for network in allowed_ranges)
    except ValueError:
        return False

def verify_credentials(username, password):
    """Verify admin credentials with rate limiting."""
    # Check if IP is allowed
    if not is_ip_allowed(st.session_state.get('ip_address')):
        log_activity(username, "LOGIN_ATTEMPT", "FAILED_IP_NOT_ALLOWED")
        return False

    # Check for failed attempts
    query = """
    SELECT COUNT(*) as attempts
    FROM USER_ACTIVITY_LOG
    WHERE username = %s
    AND action = 'LOGIN_ATTEMPT'
    AND status = 'FAILED'
    AND timestamp > DATEADD(minute, -15, CURRENT_TIMESTAMP())
    """
    result = execute_query(query, [username])

    if not result.empty and result.iloc[0]['attempts'] >= 5:
        log_activity(username, "LOGIN_ATTEMPT", "FAILED_RATE_LIMIT")
        return False

    # Verify credentials
    query = """
    SELECT password_hash
    FROM ADMIN_USERS
    WHERE username = %s
    """
    result = execute_query(query, [username])

    if result.empty:
        log_activity(username, "LOGIN_ATTEMPT", "FAILED_USER_NOT_FOUND")
        return False

    stored_hash = result.iloc[0]['password_hash']
    input_hash = hashlib.sha256(password.encode()).hexdigest()

    if stored_hash == input_hash:
        # Update last login
        query = """
        UPDATE ADMIN_USERS
        SET last_login = CURRENT_TIMESTAMP()
        WHERE username = %s
        """
        execute_update(query, [username])

        # Create session
        session_id = create_session(username, st.session_state.get('ip_address'))
        st.session_state['session_id'] = session_id

        log_activity(username, "LOGIN_SUCCESS")
        return True
    else:
        log_activity(username, "LOGIN_ATTEMPT", "FAILED_INVALID_PASSWORD")
        return False

def get_pipeline_status():
    """Get current status of data pipelines."""
    query = """
    SELECT
        pipeline_name,
        last_run_time,
        status,
        records_processed,
        error_message
    FROM PIPELINE_STATUS
    ORDER BY last_run_time DESC
    """
    return execute_query(query)

def get_system_health():
    """Get system health metrics."""
    query = """
    SELECT
        metric_name,
        metric_value,
        timestamp,
        status
    FROM SYSTEM_HEALTH
    WHERE timestamp >= %s
    ORDER BY timestamp DESC
    """
    return execute_query(query, [datetime.now() - timedelta(hours=24)])

def get_user_activity():
    """Get recent user activity."""
    query = """
    SELECT
        u.username,
        u.action,
        u.timestamp,
        u.ip_address
    FROM USER_ACTIVITY_LOG u
    ORDER BY u.timestamp DESC
    LIMIT 100
    """
    return execute_query(query)

def trigger_pipeline(pipeline_name):
    """Trigger a data pipeline."""
    try:
        # Update pipeline status
        query = """
        UPDATE PIPELINE_STATUS
        SET
            status = 'RUNNING',
            last_run_time = CURRENT_TIMESTAMP(),
            error_message = NULL
        WHERE pipeline_name = %s
        """
        execute_update(query, [pipeline_name])

        # Log activity
        log_query = """
        INSERT INTO USER_ACTIVITY_LOG (username, action, timestamp, ip_address)
        VALUES (%s, %s, CURRENT_TIMESTAMP(), %s)
        """
        execute_update(log_query, [
            st.session_state.get('admin_username'),
            f'Triggered pipeline: {pipeline_name}',
            st.experimental_get_query_params().get('client_ip', [''])[0]
        ])

        return True
    except Exception as e:
        st.error(f"Error triggering pipeline: {str(e)}")
        return False

def create_backup(backup_type):
    """Create a backup of specified data."""
    try:
        # Generate backup name
        backup_name = f"backup_{backup_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Log backup start
        query = """
        INSERT INTO DATA_BACKUP_LOG (
            backup_name, backup_type, status, created_by
        ) VALUES (%s, %s, 'IN_PROGRESS', %s)
        """
        execute_update(query, [
            backup_name,
            backup_type,
            st.session_state.get('admin_username')
        ])

        # Perform backup based on type
        if backup_type == "full":
            # Backup all tables
            tables = [
                "HERITAGE_SITES", "ART_FORMS", "CULTURAL_EVENTS",
                "VISITOR_STATS", "USER_INTERACTIONS", "PIPELINE_STATUS",
                "SYSTEM_HEALTH", "USER_ACTIVITY_LOG"
            ]
        else:
            # Backup specific tables
            tables = [backup_type]

        # Create backup directory if it doesn't exist
        backup_dir = os.path.join("backups", backup_name)
        os.makedirs(backup_dir, exist_ok=True)

        # Backup each table
        for table in tables:
            data = execute_query(f"SELECT * FROM {table}")
            if not data.empty:
                # Save as CSV
                csv_path = os.path.join(backup_dir, f"{table}.csv")
                data.to_csv(csv_path, index=False)

        # Update backup status
        query = """
        UPDATE DATA_BACKUP_LOG
        SET
            status = 'COMPLETED',
            end_time = CURRENT_TIMESTAMP(),
            size_bytes = %s,
            location = %s
        WHERE backup_name = %s
        """
        execute_update(query, [
            sum(os.path.getsize(os.path.join(backup_dir, f)) for f in os.listdir(backup_dir)),
            backup_dir,
            backup_name
        ])

        return True
    except Exception as e:
        # Log backup failure
        query = """
        UPDATE DATA_BACKUP_LOG
        SET
            status = 'FAILED',
            end_time = CURRENT_TIMESTAMP(),
            error_message = %s
        WHERE backup_name = %s
        """
        execute_update(query, [str(e), backup_name])
        return False

def cleanup_data(cleanup_options):
    """Clean up specified data."""
    try:
        for option in cleanup_options:
            if option == "Old visitor logs":
                # Delete visitor logs older than 1 year
                query = """
                DELETE FROM VISITOR_STATS
                WHERE visit_date < DATEADD(year, -1, CURRENT_DATE())
                """
                execute_update(query)

            elif option == "Expired sessions":
                # Delete expired sessions
                query = """
                DELETE FROM USER_SESSIONS
                WHERE expires_at < CURRENT_TIMESTAMP()
                """
                execute_update(query)

            elif option == "Temporary files":
                # Clean up temporary files
                temp_dir = "temp"
                if os.path.exists(temp_dir):
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)

        return True
    except Exception as e:
        st.error(f"Error during cleanup: {str(e)}")
        return False

def export_data(export_options):
    """Export specified data."""
    try:
        export_data = {}

        for option in export_options:
            if option == "Visitor statistics":
                query = """
                SELECT
                    v.visit_date,
                    h.name as site_name,
                    v.visitor_count,
                    v.revenue
                FROM VISITOR_STATS v
                JOIN HERITAGE_SITES h ON v.site_id = h.site_id
                ORDER BY v.visit_date DESC
                """
                export_data['visitor_stats'] = execute_query(query)

            elif option == "User activity logs":
                query = """
                SELECT *
                FROM USER_ACTIVITY_LOG
                ORDER BY timestamp DESC
                """
                export_data['user_activity'] = execute_query(query)

            elif option == "System metrics":
                query = """
                SELECT *
                FROM SYSTEM_HEALTH
                ORDER BY timestamp DESC
                """
                export_data['system_metrics'] = execute_query(query)

        # Create export directory
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)

        # Export each dataset
        export_files = []
        for name, data in export_data.items():
            if not data.empty:
                # Export as CSV
                filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                filepath = os.path.join(export_dir, filename)
                data.to_csv(filepath, index=False)
                export_files.append(filepath)

        return export_files
    except Exception as e:
        st.error(f"Error during export: {str(e)}")
        return []

def get_system_metrics():
    """Get current system metrics."""
    metrics = {}

    # Database connection pool
    query = """
    SELECT
        COUNT(*) as active_connections,
        MAX(created_at) as last_connection
    FROM CONNECTION_POOL
    WHERE status = 'ACTIVE'
    """
    result = execute_query(query)
    if not result.empty:
        metrics['db_connections'] = result.iloc[0]

    # Pipeline performance
    query = """
    SELECT
        pipeline_name,
        AVG(EXECUTION_TIME) as avg_execution_time,
        COUNT(*) as total_runs,
        COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_runs
    FROM PIPELINE_STATUS
    WHERE start_time > DATEADD(hour, -24, CURRENT_TIMESTAMP())
    GROUP BY pipeline_name
    """
    result = execute_query(query)
    if not result.empty:
        metrics['pipeline_performance'] = result

    # Storage usage
    query = """
    SELECT
        table_name,
        row_count,
        bytes
    FROM TABLE_STORAGE_METRICS
    ORDER BY bytes DESC
    """
    result = execute_query(query)
    if not result.empty:
        metrics['storage_usage'] = result

    # API response times
    query = """
    SELECT
        endpoint,
        AVG(response_time) as avg_response_time,
        COUNT(*) as total_requests,
        COUNT(CASE WHEN status_code >= 400 THEN 1 END) as failed_requests
    FROM API_METRICS
    WHERE timestamp > DATEADD(hour, -24, CURRENT_TIMESTAMP())
    GROUP BY endpoint
    """
    result = execute_query(query)
    if not result.empty:
        metrics['api_performance'] = result

    return metrics

def update_system_health():
    """Update system health metrics."""
    try:
        metrics = get_system_metrics()

        # Update database connection health
        if 'db_connections' in metrics:
            query = """
            INSERT INTO SYSTEM_HEALTH (
                metric_name, value, status, description
            ) VALUES (
                'DB_CONNECTIONS',
                %s,
                CASE WHEN %s > 80 THEN 'WARNING' ELSE 'HEALTHY' END,
                'Active database connections'
            )
            """
            execute_update(query, [
                metrics['db_connections']['active_connections'],
                metrics['db_connections']['active_connections']
            ])

        # Update pipeline health
        if 'pipeline_performance' in metrics:
            for _, row in metrics['pipeline_performance'].iterrows():
                query = """
                INSERT INTO SYSTEM_HEALTH (
                    metric_name, value, status, description
                ) VALUES (
                    %s,
                    %s,
                    CASE WHEN %s > 0.1 THEN 'WARNING' ELSE 'HEALTHY' END,
                    'Pipeline failure rate'
                )
                """
                execute_update(query, [
                    f"PIPELINE_{row['pipeline_name']}",
                    row['failed_runs'] / row['total_runs'],
                    row['failed_runs'] / row['total_runs']
                ])

        # Update storage health
        if 'storage_usage' in metrics:
            total_storage = metrics['storage_usage']['bytes'].sum()
            query = """
            INSERT INTO SYSTEM_HEALTH (
                metric_name, value, status, description
            ) VALUES (
                'STORAGE_USAGE',
                %s,
                CASE WHEN %s > 1000000000 THEN 'WARNING' ELSE 'HEALTHY' END,
                'Total storage usage in bytes'
            )
            """
            execute_update(query, [total_storage, total_storage])

        # Update API health
        if 'api_performance' in metrics:
            for _, row in metrics['api_performance'].iterrows():
                query = """
                INSERT INTO SYSTEM_HEALTH (
                    metric_name, value, status, description
                ) VALUES (
                    %s,
                    %s,
                    CASE WHEN %s > 0.05 THEN 'WARNING' ELSE 'HEALTHY' END,
                    'API failure rate'
                )
                """
                execute_update(query, [
                    f"API_{row['endpoint']}",
                    row['failed_requests'] / row['total_requests'],
                    row['failed_requests'] / row['total_requests']
                ])

        return True
    except Exception as e:
        log_activity(st.session_state['admin_username'], "UPDATE_SYSTEM_HEALTH", f"FAILED: {str(e)}")
        return False

def render_admin_portal():
    """Render the admin portal page."""
    # Initialize session state
    if 'admin_username' not in st.session_state:
        st.session_state['admin_username'] = None
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = None
    if 'ip_address' not in st.session_state:
        st.session_state['ip_address'] = st.experimental_get_query_params().get('ip', ['127.0.0.1'])[0]
    if 'user_agent' not in st.session_state:
        st.session_state['user_agent'] = st.experimental_get_query_params().get('user_agent', ['Unknown'])[0]

    # Check if user is logged in
    if not st.session_state['admin_username'] or not st.session_state['session_id']:
        # Login form
        st.title("Admin Portal Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if verify_credentials(username, password):
                st.session_state['admin_username'] = username
                st.experimental_rerun()
            else:
                st.error("Invalid credentials or access denied")

        return

    # Validate session
    if not validate_session(st.session_state['session_id'], st.session_state['ip_address']):
        st.error("Session expired. Please login again.")
        st.session_state['admin_username'] = None
        st.session_state['session_id'] = None
        st.experimental_rerun()

    # Admin portal content
    st.title("Admin Portal")

    # Logout button
    if st.sidebar.button("Logout"):
        log_activity(st.session_state['admin_username'], "LOGOUT")
        st.session_state['admin_username'] = None
        st.session_state['session_id'] = None
        st.experimental_rerun()

    # Create tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "Pipeline Control",
        "System Health",
        "User Activity",
        "Data Management"
    ])

    with tab1:
        st.subheader("Data Pipeline Control")

        # Get pipeline status
        pipeline_status = get_pipeline_status()

        if not pipeline_status.empty:
            # Display pipeline status
            for _, pipeline in pipeline_status.iterrows():
                with st.expander(f"{pipeline['pipeline_name']} - {pipeline['status']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Last Run: {pipeline['last_run_time']}")
                        st.write(f"Records Processed: {pipeline['records_processed']}")
                    with col2:
                        if pipeline['error_message']:
                            st.error(f"Error: {pipeline['error_message']}")
                        if st.button("Trigger Pipeline", key=f"trigger_{pipeline['pipeline_name']}"):
                            if trigger_pipeline(pipeline['pipeline_name']):
                                st.success("Pipeline triggered successfully!")
                                time.sleep(1)
                                st.experimental_rerun()

            # Pipeline status visualization
            st.subheader("Pipeline Status Overview")
            fig = px.bar(
                pipeline_status,
                x='pipeline_name',
                y='records_processed',
                color='status',
                title='Pipeline Processing Status',
                labels={
                    'pipeline_name': 'Pipeline',
                    'records_processed': 'Records Processed',
                    'status': 'Status'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("System Health Monitoring")

        # Get system health metrics
        health_metrics = get_system_health()

        if not health_metrics.empty:
            # Display current system status
            st.write("Current System Status")
            current_metrics = health_metrics[health_metrics['timestamp'] == health_metrics['timestamp'].max()]

            cols = st.columns(4)
            for i, (_, metric) in enumerate(current_metrics.iterrows()):
                with cols[i % 4]:
                    st.metric(
                        metric['metric_name'],
                        f"{metric['metric_value']:.2f}",
                        delta=None,
                        delta_color="normal"
                    )

            # System health trends
            st.subheader("System Health Trends")
            for metric in health_metrics['metric_name'].unique():
                metric_data = health_metrics[health_metrics['metric_name'] == metric]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=metric_data['timestamp'],
                    y=metric_data['metric_value'],
                    name=metric,
                    line=dict(color='#1E88E5')
                ))
                fig.update_layout(
                    title=f'{metric} Trend',
                    xaxis_title='Time',
                    yaxis_title='Value',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("System Health")

        # Update system health
        if st.button("Update System Health"):
            if update_system_health():
                st.success("System health metrics updated successfully!")
            else:
                st.error("Failed to update system health metrics")

        # Display current system health
        query = """
        SELECT *
        FROM SYSTEM_HEALTH
        WHERE timestamp > DATEADD(hour, -24, CURRENT_TIMESTAMP())
        ORDER BY timestamp DESC
        """
        health_data = execute_query(query)

        if not health_data.empty:
            # Health status overview
            col1, col2, col3 = st.columns(3)

            with col1:
                healthy_count = len(health_data[health_data['status'] == 'HEALTHY'])
                st.metric("Healthy Metrics", healthy_count)

            with col2:
                warning_count = len(health_data[health_data['status'] == 'WARNING'])
                st.metric("Warning Metrics", warning_count)

            with col3:
                critical_count = len(health_data[health_data['status'] == 'CRITICAL'])
                st.metric("Critical Metrics", critical_count)

            # Health trends
            st.write("### Health Trends")
            fig = px.line(
                health_data,
                x='timestamp',
                y='value',
                color='metric_name',
                title='System Health Metrics Over Time'
            )
            st.plotly_chart(fig)

            # Detailed metrics
            st.write("### Detailed Metrics")
            for metric in health_data['metric_name'].unique():
                metric_data = health_data[health_data['metric_name'] == metric]
                latest = metric_data.iloc[0]

                st.write(f"#### {metric}")
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Current Value",
                        f"{latest['value']:.2f}",
                        delta=f"{latest['value'] - metric_data.iloc[1]['value']:.2f}"
                    )

                with col2:
                    st.metric("Status", latest['status'])

                st.write(latest['description'])
                st.write("---")

        # System metrics
        st.write("### System Metrics")
        metrics = get_system_metrics()

        if 'db_connections' in metrics:
            st.write("#### Database Connections")
            st.metric(
                "Active Connections",
                metrics['db_connections']['active_connections'],
                f"Last connection: {metrics['db_connections']['last_connection']}"
            )

        if 'pipeline_performance' in metrics:
            st.write("#### Pipeline Performance")
            fig = px.bar(
                metrics['pipeline_performance'],
                x='pipeline_name',
                y='avg_execution_time',
                title='Average Pipeline Execution Time'
            )
            st.plotly_chart(fig)

        if 'storage_usage' in metrics:
            st.write("#### Storage Usage")
            fig = px.pie(
                metrics['storage_usage'],
                values='bytes',
                names='table_name',
                title='Storage Usage by Table'
            )
            st.plotly_chart(fig)

        if 'api_performance' in metrics:
            st.write("#### API Performance")
            fig = px.bar(
                metrics['api_performance'],
                x='endpoint',
                y='avg_response_time',
                title='Average API Response Time'
            )
            st.plotly_chart(fig)

    with tab4:
        st.subheader("Data Management")

        # Data backup controls
        st.write("### Data Backup")
        backup_type = st.selectbox(
            "Select Backup Type",
            ["full", "HERITAGE_SITES", "ART_FORMS", "CULTURAL_EVENTS", "VISITOR_STATS"]
        )
        if st.button("Create Backup"):
            if create_backup(backup_type):
                st.success("Backup created successfully!")
            else:
                st.error("Failed to create backup")

        # Display recent backups
        st.write("### Recent Backups")
        query = """
        SELECT *
        FROM DATA_BACKUP_LOG
        ORDER BY start_time DESC
        LIMIT 5
        """
        backups = execute_query(query)
        if not backups.empty:
            st.dataframe(backups)

        # Data cleanup controls
        st.write("### Data Cleanup")
        cleanup_options = st.multiselect(
            "Select data to clean up",
            ["Old visitor logs", "Expired sessions", "Temporary files"]
        )
        if st.button("Clean Selected Data"):
            if cleanup_data(cleanup_options):
                st.success("Cleanup completed successfully!")
            else:
                st.error("Failed to complete cleanup")

        # Data export controls
        st.write("### Data Export")
        export_options = st.multiselect(
            "Select data to export",
            ["Visitor statistics", "User activity logs", "System metrics"]
        )
        if st.button("Export Selected Data"):
            export_files = export_data(export_options)
            if export_files:
                st.success("Data exported successfully!")
                for file in export_files:
                    with open(file, 'rb') as f:
                        st.download_button(
                            f"Download {os.path.basename(file)}",
                            f,
                            file_name=os.path.basename(file),
                            mime="text/csv"
                        )
            else:
                st.error("Failed to export data")
