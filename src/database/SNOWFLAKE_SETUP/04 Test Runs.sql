-- 1. Test Connection:

-- Test database access
USE DATABASE ROOTS_ROUTES;
USE SCHEMA PUBLIC;
USE WAREHOUSE COMPUTE_WH;

-- Test table creation
SELECT CURRENT_TIMESTAMP();
SELECT COUNT(*) FROM HERITAGE_SITES;

-- get_trending_heritage_sites(limit: int = 5)
SELECT * FROM HERITAGE_SITES;
SELECT COUNT(*) FROM HERITAGE_SITES;

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
    LIMIT 5
