import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

class HeritageAIAnalysis:
    def __init__(self, db_connection):
        self.db = db_connection

    def calculate_health_score(self, site_id: int) -> Dict:
        """
        Calculate the Cultural Heritage Health Score for a site
        """
        # Get site data
        site_data = self._get_site_data(site_id)

        # Calculate individual scores
        physical_score = self._calculate_physical_condition(site_data)
        cultural_score = self._calculate_cultural_significance(site_data)
        tourism_score = self._calculate_tourism_impact(site_data)
        community_score = self._calculate_community_engagement(site_data)

        # Calculate overall score with weighted average
        weights = {
            'physical': 0.3,
            'cultural': 0.3,
            'tourism': 0.2,
            'community': 0.2
        }

        overall_score = (
            physical_score * weights['physical'] +
            cultural_score * weights['cultural'] +
            tourism_score * weights['tourism'] +
            community_score * weights['community']
        )

        return {
            'physical_condition_score': physical_score,
            'cultural_significance_score': cultural_score,
            'tourism_impact_score': tourism_score,
            'community_engagement_score': community_score,
            'overall_health_score': overall_score,
            'assessment_date': datetime.now().date()
        }

    def calculate_tourism_potential(self, site_id: int) -> Dict:
        """
        Calculate the Tourism Potential Index for a site
        """
        # Get site data
        site_data = self._get_site_data(site_id)

        # Calculate individual scores
        visitor_score = self._calculate_visitor_potential(site_data)
        significance_score = self._calculate_site_significance(site_data)
        infrastructure_score = self._calculate_infrastructure_readiness(site_data)
        community_score = self._calculate_community_capacity(site_data)
        preservation_score = self._calculate_preservation_needs(site_data)

        # Calculate overall score with weighted average
        weights = {
            'visitor': 0.25,
            'significance': 0.25,
            'infrastructure': 0.2,
            'community': 0.15,
            'preservation': 0.15
        }

        overall_score = (
            visitor_score * weights['visitor'] +
            significance_score * weights['significance'] +
            infrastructure_score * weights['infrastructure'] +
            community_score * weights['community'] +
            preservation_score * weights['preservation']
        )

        return {
            'current_visitor_score': visitor_score,
            'site_significance_score': significance_score,
            'infrastructure_readiness': infrastructure_score,
            'community_capacity': community_score,
            'preservation_needs': preservation_score,
            'overall_potential_score': overall_score,
            'assessment_date': datetime.now().date()
        }

    def analyze_seasonality(self, site_id: int) -> Dict:
        """
        Analyze tourism seasonality patterns for a site
        """
        # Get visitor statistics
        visitor_stats = self._get_visitor_stats(site_id)

        # Calculate seasonal patterns
        seasonal_patterns = self._calculate_seasonal_patterns(visitor_stats)

        # Identify peak and off-peak seasons
        peak_seasons = self._identify_peak_seasons(seasonal_patterns)

        # Calculate revenue optimization opportunities
        revenue_opportunities = self._calculate_revenue_opportunities(seasonal_patterns)

        return {
            'seasonal_patterns': seasonal_patterns,
            'peak_seasons': peak_seasons,
            'revenue_opportunities': revenue_opportunities
        }

    def generate_preservation_priorities(self, site_id: int) -> Dict:
        """
        Generate preservation priorities for a site
        """
        # Get site data
        site_data = self._get_site_data(site_id)

        # Calculate risk assessment
        risk_score = self._calculate_risk_assessment(site_data)

        # Determine resource allocation priority
        priority_level = self._determine_priority_level(risk_score, site_data)

        # Generate implementation timeline
        timeline = self._generate_implementation_timeline(risk_score, site_data)

        return {
            'risk_assessment_score': risk_score,
            'resource_allocation_priority': priority_level,
            'implementation_timeline': timeline
        }

    def _get_site_data(self, site_id: int) -> Dict:
        """Helper method to get site data from database"""
        cursor = self.db.cursor()
        try:
            # First, let's check what tables exist
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
            """)
            tables = cursor.fetchall()
            available_tables = [table[0].upper() for table in tables]
            print("Available tables:", available_tables)

            # Check if required tables exist
            has_user_interactions = 'USER_INTERACTIONS' in available_tables
            has_visitor_stats = 'VISITOR_STATS' in available_tables

            # Get the actual column names from HERITAGE_SITES
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                AND table_name = 'HERITAGE_SITES'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print("HERITAGE_SITES columns:", columns)

            if not columns:
                print("No columns found in HERITAGE_SITES table")
                return {}

            heritage_columns = [col[0] for col in columns]

            # Find the ID column (it might be named differently)
            id_column = next((col for col in heritage_columns if col.upper() in ['ID', 'SITE_ID', 'HERITAGE_ID']), None)
            if not id_column:
                print("Could not find ID column in HERITAGE_SITES table")
                return {}

            # First, get the basic site data
            basic_query = f"""
                SELECT {', '.join(f'"{col}"' for col in heritage_columns)}
                FROM "HERITAGE_SITES"
                WHERE "{id_column}" = {site_id}
            """

            # Debug output
            print("Executing basic query:", basic_query)

            cursor.execute(basic_query)
            site_data = cursor.fetchone()

            if not site_data:
                return {}

            # Map the basic site data
            result = {}
            for i, col in enumerate(heritage_columns):
                # Convert Snowflake numeric types to Python float
                if isinstance(site_data[i], (int, float)):
                    result[col.lower()] = float(site_data[i])
                else:
                    result[col.lower()] = site_data[i]

            # Now get the additional metrics if tables exist
            if has_user_interactions:
                # Get column names from USER_INTERACTIONS
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = current_schema()
                    AND table_name = 'USER_INTERACTIONS'
                    ORDER BY ordinal_position
                """)
                ui_columns = [col[0] for col in cursor.fetchall()]
                print("USER_INTERACTIONS columns:", ui_columns)

                # Find the ID and SITE_ID columns
                ui_id_column = next((col for col in ui_columns if col.upper() in ['ID', 'INTERACTION_ID']), None)
                ui_site_id_column = next((col for col in ui_columns if col.upper() in ['SITE_ID', 'HERITAGE_ID']), None)
                ui_rating_column = next((col for col in ui_columns if col.upper() in ['RATING', 'SCORE']), None)

                if all([ui_id_column, ui_site_id_column, ui_rating_column]):
                    ui_query = f"""
                        SELECT
                            COUNT(DISTINCT "{ui_id_column}") as review_count,
                            AVG("{ui_rating_column}") as avg_rating
                        FROM "USER_INTERACTIONS"
                        WHERE "{ui_site_id_column}" = {site_id}
                    """
                    print("Executing UI query:", ui_query)
                    cursor.execute(ui_query)
                    ui_data = cursor.fetchone()
                    result['review_count'] = float(ui_data[0] or 0)
                    result['avg_rating'] = float(ui_data[1] or 0)
                else:
                    print("Missing required columns in USER_INTERACTIONS")
                    result['review_count'] = 0.0
                    result['avg_rating'] = 0.0
            else:
                result['review_count'] = 0.0
                result['avg_rating'] = 0.0

            if has_visitor_stats:
                # Get column names from VISITOR_STATS
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = current_schema()
                    AND table_name = 'VISITOR_STATS'
                    ORDER BY ordinal_position
                """)
                vs_columns = [col[0] for col in cursor.fetchall()]
                print("VISITOR_STATS columns:", vs_columns)

                # Find the ID and SITE_ID columns
                vs_id_column = next((col for col in vs_columns if col.upper() in ['ID', 'STAT_ID']), None)
                vs_site_id_column = next((col for col in vs_columns if col.upper() in ['SITE_ID', 'HERITAGE_ID']), None)
                vs_count_column = next((col for col in vs_columns if col.upper() in ['VISITOR_COUNT', 'COUNT', 'TOTAL_VISITORS']), None)

                if all([vs_id_column, vs_site_id_column, vs_count_column]):
                    vs_query = f"""
                        SELECT
                            COUNT(DISTINCT "{vs_id_column}") as visitor_count,
                            AVG("{vs_count_column}") as avg_visitors
                        FROM "VISITOR_STATS"
                        WHERE "{vs_site_id_column}" = {site_id}
                    """
                    print("Executing VS query:", vs_query)
                    cursor.execute(vs_query)
                    vs_data = cursor.fetchone()
                    result['visitor_count'] = float(vs_data[0] or 0)
                    result['avg_visitors'] = float(vs_data[1] or 0)
                else:
                    print("Missing required columns in VISITOR_STATS")
                    result['visitor_count'] = 0.0
                    result['avg_visitors'] = 0.0
            else:
                result['visitor_count'] = 0.0
                result['avg_visitors'] = 0.0

            return result

        finally:
            cursor.close()

    def _get_visitor_stats(self, site_id: int) -> pd.DataFrame:
        """Helper method to get visitor statistics from database"""
        cursor = self.db.cursor()
        try:
            # First check if VISITOR_STATS table exists
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                AND table_name = 'VISITOR_STATS'
            """)
            if not cursor.fetchone():
                print("VISITOR_STATS table not found")
                return pd.DataFrame(columns=['visit_date', 'visitor_count', 'revenue', 'season'])

            # Get column names from VISITOR_STATS
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                AND table_name = 'VISITOR_STATS'
                ORDER BY ordinal_position
            """)
            columns = [col[0] for col in cursor.fetchall()]
            print("VISITOR_STATS columns:", columns)

            # Find required columns
            date_col = next((col for col in columns if col.upper() in ['VISIT_DATE', 'DATE', 'VISIT_TIME']), None)
            count_col = next((col for col in columns if col.upper() in ['VISITOR_COUNT', 'COUNT', 'TOTAL_VISITORS']), None)
            revenue_col = next((col for col in columns if col.upper() in ['REVENUE', 'INCOME', 'TOTAL_REVENUE']), None)
            season_col = next((col for col in columns if col.upper() in ['SEASON', 'VISIT_SEASON']), None)
            site_id_col = next((col for col in columns if col.upper() in ['SITE_ID', 'HERITAGE_ID']), None)

            if not all([date_col, count_col, site_id_col]):
                print("Missing required columns in VISITOR_STATS")
                return pd.DataFrame(columns=['visit_date', 'visitor_count', 'revenue', 'season'])

            # Build the query
            select_cols = [f'"{date_col}" as visit_date', f'"{count_col}" as visitor_count']
            if revenue_col:
                select_cols.append(f'"{revenue_col}" as revenue')
            else:
                select_cols.append('NULL as revenue')
            if season_col:
                select_cols.append(f'"{season_col}" as season')
            else:
                select_cols.append('NULL as season')

            query = f"""
                SELECT {', '.join(select_cols)}
                FROM "VISITOR_STATS"
                WHERE "{site_id_col}" = {site_id}
                ORDER BY "{date_col}"
            """
            print("Executing visitor stats query:", query)

            cursor.execute(query)
            stats = cursor.fetchall()

            # Convert to DataFrame
            df = pd.DataFrame(stats, columns=['visit_date', 'visitor_count', 'revenue', 'season'])

            # Convert numeric columns to float
            df['visitor_count'] = pd.to_numeric(df['visitor_count'], errors='coerce').fillna(0)
            if 'revenue' in df.columns:
                df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)

            return df

        finally:
            cursor.close()

    def _calculate_physical_condition(self, site_data: Dict) -> float:
        """Calculate physical condition score"""
        if not site_data:
            return 0.0

        # Base score from health_index
        base_score = float(site_data['health_index'] or 0)

        # Adjust based on risk_level
        risk_multiplier = {
            'Low': 1.0,
            'Medium': 0.8,
            'High': 0.6
        }.get(site_data['risk_level'], 1.0)

        return min(1.0, float(base_score * risk_multiplier))

    def _calculate_cultural_significance(self, site_data: Dict) -> float:
        """Calculate cultural significance score"""
        if not site_data:
            return 0.0

        # Base score from UNESCO status
        base_score = 0.8 if site_data['unesco_status'] else 0.5

        # Adjust based on review count and average rating
        review_score = min(1.0, float(site_data['review_count'] or 0) / 100)
        rating_score = float(site_data['avg_rating'] or 0) / 5

        return float(base_score * 0.5 + review_score * 0.25 + rating_score * 0.25)

    def _calculate_tourism_impact(self, site_data: Dict) -> float:
        """Calculate tourism impact score"""
        if not site_data:
            return 0.0

        # Calculate based on visitor statistics
        visitor_score = min(1.0, float(site_data['avg_visitors'] or 0) / 1000)

        # Adjust based on revenue (if available)
        revenue_score = 0.5  # Default if no revenue data

        return float(visitor_score * 0.7 + revenue_score * 0.3)

    def _calculate_community_engagement(self, site_data: Dict) -> float:
        """Calculate community engagement score"""
        if not site_data:
            return 0.0

        # Base score from review count
        review_score = min(1.0, float(site_data['review_count'] or 0) / 50)

        # Adjust based on average rating
        rating_score = float(site_data['avg_rating'] or 0) / 5

        return float(review_score * 0.6 + rating_score * 0.4)

    def _calculate_seasonal_patterns(self, visitor_stats: pd.DataFrame) -> Dict:
        """Calculate seasonal patterns from visitor statistics"""
        if visitor_stats.empty:
            return {}

        # Convert visitor_count to float
        visitor_stats['visitor_count'] = visitor_stats['visitor_count'].astype(float)

        # Group by season and calculate average visitors
        seasonal_avg = visitor_stats.groupby('season')['visitor_count'].mean()

        # Normalize to 0-1 range
        max_visitors = seasonal_avg.max()
        if max_visitors > 0:
            seasonal_avg = seasonal_avg / max_visitors

        return seasonal_avg.to_dict()

    def _identify_peak_seasons(self, seasonal_patterns: Dict) -> List[str]:
        """Identify peak seasons from seasonal patterns"""
        if not seasonal_patterns:
            return []

        # Calculate mean and standard deviation
        values = list(seasonal_patterns.values())
        mean = np.mean(values)
        std = np.std(values)

        # Identify seasons above mean + 0.5*std as peak
        threshold = mean + 0.5 * std
        return [season for season, value in seasonal_patterns.items()
                if value >= threshold]

    def _calculate_revenue_opportunities(self, seasonal_patterns: Dict) -> List[str]:
        """Calculate revenue optimization opportunities"""
        if not seasonal_patterns:
            return ["Insufficient data for revenue analysis"]

        opportunities = []

        # Identify off-peak seasons
        mean = np.mean(list(seasonal_patterns.values()))
        off_peak = [season for season, value in seasonal_patterns.items()
                   if value < mean]

        if off_peak:
            opportunities.append(
                f"Consider promotional activities during {', '.join(off_peak)}"
            )

        # Suggest dynamic pricing
        if len(seasonal_patterns) > 1:
            opportunities.append(
                "Implement dynamic pricing based on seasonal demand"
            )

        return opportunities

    def _calculate_risk_assessment(self, site_data: Dict) -> float:
        """Calculate risk assessment score"""
        if not site_data:
            return 0.0

        # Base risk from risk_level
        risk_scores = {
            'Low': 0.3,
            'Medium': 0.6,
            'High': 0.9
        }
        base_risk = risk_scores.get(site_data['risk_level'], 0.5)

        # Adjust based on health_index
        health_factor = 1 - float(site_data['health_index'] or 0)

        return min(1.0, float(base_risk * 0.7 + health_factor * 0.3))

    def _determine_priority_level(self, risk_score: float, site_data: Dict) -> int:
        """Determine resource allocation priority level"""
        if not site_data:
            return 3

        # UNESCO sites get higher priority
        unesco_bonus = 1 if site_data['unesco_status'] else 0

        # Calculate base priority
        if risk_score >= 0.8:
            base_priority = 1
        elif risk_score >= 0.5:
            base_priority = 2
        else:
            base_priority = 3

        return max(1, base_priority - unesco_bonus)

    def _generate_implementation_timeline(self, risk_score: float, site_data: Dict) -> List[str]:
        """Generate implementation timeline for preservation"""
        if not site_data:
            return ["Insufficient data for timeline generation"]

        timeline = []

        # Immediate actions for high-risk sites
        if risk_score >= 0.8:
            timeline.extend([
                "Immediate structural assessment",
                "Emergency preservation measures",
                "Visitor management plan implementation"
            ])
        elif risk_score >= 0.5:
            timeline.extend([
                "Detailed condition assessment",
                "Preservation planning",
                "Community engagement program"
            ])
        else:
            timeline.extend([
                "Regular maintenance schedule",
                "Tourism development planning",
                "Long-term preservation strategy"
            ])

        return timeline

    def _calculate_visitor_potential(self, site_data: Dict) -> float:
        """Calculate visitor potential score"""
        if not site_data:
            return 0.0

        # Base score from current visitor count
        visitor_score = min(1.0, float(site_data['visitor_count'] or 0) / 1000)

        # Adjust based on average rating
        rating_score = float(site_data['avg_rating'] or 0) / 5

        # Adjust based on review count
        review_score = min(1.0, float(site_data['review_count'] or 0) / 100)

        return float(visitor_score * 0.5 + rating_score * 0.3 + review_score * 0.2)

    def _calculate_site_significance(self, site_data: Dict) -> float:
        """Calculate site significance score"""
        if not site_data:
            return 0.0

        # Base score from UNESCO status
        base_score = 0.8 if site_data['unesco_status'] else 0.5

        # Adjust based on heritage type
        heritage_type_score = {
            'Cultural': 0.9,
            'Natural': 0.8,
            'Mixed': 0.85,
            'Historical': 0.75
        }.get(site_data['heritage_type'], 0.6)

        # Adjust based on established year (older is more significant)
        year_score = 0.5  # Default if no year data
        if site_data['established_year']:
            current_year = datetime.now().year
            age = current_year - int(site_data['established_year'])
            year_score = min(1.0, float(age) / 1000)  # Cap at 1000 years

        return float(base_score * 0.4 + heritage_type_score * 0.3 + year_score * 0.3)

    def _calculate_infrastructure_readiness(self, site_data: Dict) -> float:
        """Calculate infrastructure readiness score"""
        if not site_data:
            return 0.0

        # Base score from health index
        base_score = float(site_data['health_index'] or 0)

        # Adjust based on risk level
        risk_multiplier = {
            'Low': 1.0,
            'Medium': 0.8,
            'High': 0.6
        }.get(site_data['risk_level'], 1.0)

        return float(base_score * risk_multiplier)

    def _calculate_community_capacity(self, site_data: Dict) -> float:
        """Calculate community capacity score"""
        if not site_data:
            return 0.0

        # Base score from review count
        review_score = min(1.0, float(site_data['review_count'] or 0) / 50)

        # Adjust based on average rating
        rating_score = float(site_data['avg_rating'] or 0) / 5

        # Adjust based on visitor count
        visitor_score = min(1.0, float(site_data['visitor_count'] or 0) / 500)

        return float(review_score * 0.4 + rating_score * 0.4 + visitor_score * 0.2)

    def _calculate_preservation_needs(self, site_data: Dict) -> float:
        """Calculate preservation needs score"""
        if not site_data:
            return 0.0

        # Base score from risk level
        risk_scores = {
            'Low': 0.3,
            'Medium': 0.6,
            'High': 0.9
        }
        base_score = risk_scores.get(site_data['risk_level'], 0.5)

        # Adjust based on health index
        health_factor = 1 - float(site_data['health_index'] or 0)

        # Adjust based on UNESCO status (UNESCO sites need more preservation)
        unesco_factor = 1.2 if site_data['unesco_status'] else 1.0

        return float(min(1.0, base_score * 0.6 + health_factor * 0.4) * unesco_factor)
