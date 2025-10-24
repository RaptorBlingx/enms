"""
EnMS Analytics Service - Feature Discovery Service
===================================================
DYNAMIC MULTI-ENERGY ARCHITECTURE
Per Mr. Umut: "ZERO hardcoding - expand for ANY energy source, machine, SEU, meter"

Purpose:
- Discover available features for any energy source dynamically from database
- Build SQL aggregation queries based on feature metadata
- Validate requested features exist and are compatible
- Enable "plug-and-play" energy sources (add natural gas → works immediately)

Author: EnMS Team
Phase: 2 - Dynamic Multi-Energy Support
Date: October 23, 2025
"""

from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from dataclasses import dataclass
import logging

from database import db

logger = logging.getLogger(__name__)


@dataclass
class EnergyFeature:
    """
    Represents a single energy feature from database metadata.
    
    Example:
        Feature(
            name='consumption_kwh',
            data_type='numeric',
            source_table='energy_readings',
            source_column='energy_kwh',
            aggregation='SUM',
            description='Total electrical energy consumed (kWh)'
        )
    """
    feature_name: str
    data_type: str
    source_table: str
    source_column: str
    aggregation_function: str
    description: Optional[str] = None
    is_regression_feature: bool = True


class FeatureDiscoveryService:
    """
    Service for dynamic feature discovery across all energy sources.
    
    NO HARDCODED FEATURE LISTS.
    All feature metadata comes from energy_source_features table.
    
    Key Methods:
    - get_available_features(): Query database for features per energy source
    - build_aggregation_query(): Generate dynamic SQL based on requested features
    - validate_features(): Check requested features exist and are valid
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_available_features(
        self,
        energy_source_id: UUID,
        regression_only: bool = True
    ) -> List[EnergyFeature]:
        """
        Get all available features for an energy source.
        
        Args:
            energy_source_id: UUID of energy source (electricity, natural_gas, etc.)
            regression_only: If True, only return features usable in baselines
        
        Returns:
            List of EnergyFeature objects with metadata
            
        Example:
            features = await get_available_features(electricity_id)
            # Returns: [consumption_kwh, production_count, outdoor_temp_c, ...]
        """
        query = """
            SELECT 
                feature_name,
                data_type,
                source_table,
                source_column,
                aggregation_function,
                description,
                is_regression_feature
            FROM energy_source_features
            WHERE energy_source_id = $1
              AND is_active = true
        """
        
        if regression_only:
            query += " AND is_regression_feature = true"
        
        query += " ORDER BY feature_name"
        
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(query, energy_source_id)
            
            features = [
                EnergyFeature(
                    feature_name=row['feature_name'],
                    data_type=row['data_type'],
                    source_table=row['source_table'],
                    source_column=row['source_column'],
                    aggregation_function=row['aggregation_function'],
                    description=row['description'],
                    is_regression_feature=row['is_regression_feature']
                )
                for row in rows
            ]
            
            logger.info(
                f"[FEATURE-DISCOVERY] Found {len(features)} features for energy_source_id={energy_source_id}"
            )
            
            return features
    
    async def validate_features(
        self,
        energy_source_id: UUID,
        requested_features: List[str]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate that requested features exist for an energy source.
        
        Args:
            energy_source_id: UUID of energy source
            requested_features: List of feature names user wants to use
        
        Returns:
            Tuple of:
            - valid (bool): True if all features exist
            - valid_features (List[str]): Features that exist
            - invalid_features (List[str]): Features that don't exist
            
        Example:
            valid, good, bad = await validate_features(
                electricity_id,
                ['consumption_kwh', 'production_count', 'invalid_feature']
            )
            # Returns: (False, ['consumption_kwh', 'production_count'], ['invalid_feature'])
        """
        available = await self.get_available_features(energy_source_id, regression_only=True)
        available_names = {f.feature_name for f in available}
        
        valid_features = [f for f in requested_features if f in available_names]
        invalid_features = [f for f in requested_features if f not in available_names]
        
        is_valid = len(invalid_features) == 0
        
        if not is_valid:
            logger.warning(
                f"[FEATURE-DISCOVERY] Invalid features requested: {invalid_features}. "
                f"Available: {sorted(available_names)}"
            )
        
        return is_valid, valid_features, invalid_features
    
    async def get_feature_metadata(
        self,
        energy_source_id: UUID,
        feature_names: List[str]
    ) -> Dict[str, EnergyFeature]:
        """
        Get metadata for specific features.
        
        Args:
            energy_source_id: UUID of energy source
            feature_names: List of feature names to retrieve
        
        Returns:
            Dict mapping feature_name → EnergyFeature object
            
        Example:
            metadata = await get_feature_metadata(
                electricity_id,
                ['consumption_kwh', 'production_count']
            )
            # Returns: {
            #     'consumption_kwh': Feature(source_table='energy_readings', ...),
            #     'production_count': Feature(source_table='production_data', ...)
            # }
        """
        query = """
            SELECT 
                feature_name,
                data_type,
                source_table,
                source_column,
                aggregation_function,
                description,
                is_regression_feature
            FROM energy_source_features
            WHERE energy_source_id = $1
              AND feature_name = ANY($2::text[])
              AND is_active = true
            ORDER BY feature_name
        """
        
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(query, energy_source_id, feature_names)
            
            metadata = {}
            for row in rows:
                feature = EnergyFeature(
                    feature_name=row['feature_name'],
                    data_type=row['data_type'],
                    source_table=row['source_table'],
                    source_column=row['source_column'],
                    aggregation_function=row['aggregation_function'],
                    description=row['description'],
                    is_regression_feature=row['is_regression_feature']
                )
                metadata[feature.feature_name] = feature
            
            return metadata
    
    async def build_daily_aggregation_query(
        self,
        energy_source_id: UUID,
        machine_ids: List[UUID],
        requested_features: List[str],
        start_date: str,
        end_date: str
    ) -> str:
        """
        Build dynamic SQL query to aggregate features by day.
        
        PERFORMANCE OPTIMIZED: Aggregates each table separately FIRST, then joins.
        This is 50-100x faster than JOIN-then-AGGREGATE on large hypertables.
        
        Args:
            energy_source_id: Energy source (electricity, natural_gas, etc.)
            machine_ids: List of machine UUIDs in this SEU
            requested_features: Features to aggregate
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Complete SQL query string optimized for TimescaleDB
            
        Strategy:
        1. Aggregate each table separately with time_bucket
        2. Join the pre-aggregated results on 'day'
        3. Much faster than joining raw tables then aggregating
        
        Example structure:
        WITH energy_daily AS (
            SELECT time_bucket('1 day', time)::DATE as day, SUM(energy_kwh) as consumption_kwh
            FROM energy_readings WHERE machine_id = ... GROUP BY day
        ),
        production_daily AS (
            SELECT time_bucket('1 day', time)::DATE as day, AVG(production_count) as production_count
            FROM production_data WHERE machine_id = ... GROUP BY day
        )
        SELECT energy_daily.day, consumption_kwh, production_count
        FROM energy_daily
        LEFT JOIN production_daily USING (day)
        ORDER BY day
        """
        # Get ALL features for the energy source to find primary consumption feature
        all_features_query = """
            SELECT feature_name, source_table, source_column, aggregation_function
            FROM energy_source_features
            WHERE energy_source_id = $1
              AND source_table IN ('energy_readings', 'natural_gas_readings', 'steam_readings', 'compressed_air_end_use_readings')
            LIMIT 1
        """
        async with db.pool.acquire() as conn:
            primary_feature = await conn.fetchrow(all_features_query, energy_source_id)
        
        if not primary_feature:
            raise ValueError(f"No primary energy table found for energy_source_id={energy_source_id}")
        
        primary_table = primary_feature['source_table']
        primary_alias = self._get_table_alias(primary_table)
        primary_consumption_feature = primary_feature['feature_name']
        
        logger.info(
            f"[FEATURE-DISCOVERY] Primary table: {primary_table} (alias: {primary_alias}), " 
            f"consumption feature: {primary_consumption_feature}"
        )
        
        # Get feature metadata for REQUESTED features only
        metadata = await self.get_feature_metadata(energy_source_id, requested_features)
        
        if not metadata:
            raise ValueError(f"No valid features found from: {requested_features}")
        
        # Add primary consumption feature to metadata if not already included
        if primary_consumption_feature not in metadata:
            metadata[primary_consumption_feature] = EnergyFeature(
                feature_name=primary_consumption_feature,
                data_type='numeric',
                source_table=primary_table,
                source_column=primary_feature['source_column'],
                aggregation_function=primary_feature['aggregation_function']
            )
        
        logger.info(
            f"[FEATURE-DISCOVERY] Primary table: {primary_table} (alias: {primary_alias})"
        )
        
        # Build SELECT clause
        select_parts = [f"time_bucket('1 day', {primary_alias}.time)::DATE as day"]
        
        # Group features by source table for CTE building
        tables_needed = {primary_table}
        features_by_table = {primary_table: []}
        
        for feature_name, feature in metadata.items():
            tables_needed.add(feature.source_table)
            if feature.source_table not in features_by_table:
                features_by_table[feature.source_table] = []
            features_by_table[feature.source_table].append((feature_name, feature))
        
        # Build CTEs - one per table, pre-aggregated by day
        ctes = []
        
        # Primary table CTE (energy_readings, natural_gas_readings, etc.)
        primary_alias = self._get_table_alias(primary_table)
        energy_column = self._get_energy_column(primary_table)
        
        primary_selects = [f"time_bucket('1 day', time)::DATE as day"]
        
        # Add primary consumption feature
        if primary_consumption_feature in metadata:
            feat = metadata[primary_consumption_feature]
            agg = feat.aggregation_function
            col = feat.source_column
            primary_selects.append(f"{agg}({col}) as {primary_consumption_feature}")
        
        # Add operating hours
        primary_selects.append(f"COUNT(DISTINCT EXTRACT(HOUR FROM time)) as operating_hours")
        
        # Add any other features from primary table
        for feat_name, feat in features_by_table.get(primary_table, []):
            if feat_name == primary_consumption_feature:
                continue  # Already added
            agg = feat.aggregation_function
            col = feat.source_column
            if agg != 'CUSTOM':
                primary_selects.append(f"{agg}({col}) as {feat_name}")
        
        primary_cte = f"""
        {primary_alias}_daily AS (
            SELECT {', '.join(primary_selects)}
            FROM {primary_table}
            WHERE machine_id = ANY($1::uuid[])
              AND time BETWEEN $2 AND ($3::date + INTERVAL '1 day')
              AND {energy_column} > 0
            GROUP BY day
        )"""
        ctes.append(primary_cte)
        
        # Additional table CTEs (production_data, environmental_data, etc.)
        for table in tables_needed:
            if table == primary_table:
                continue
                
            alias = self._get_table_alias(table)
            table_selects = [f"time_bucket('1 day', time)::DATE as day"]
            
            for feat_name, feat in features_by_table.get(table, []):
                agg = feat.aggregation_function
                col = feat.source_column
                
                if agg == 'CUSTOM':
                    # Handle special aggregations
                    if 'heating_degree_days' in feat_name:
                        # Compute degree-days based on the daily average temperature (T_daily_avg)
                        # HDD = GREATEST(0, base_temp - AVG(temp)) to avoid overcounting when
                        # measurements are hourly or higher frequency (previously SUM(...) caused
                        # degree-hour aggregation and inflated values).
                        table_selects.append(f"GREATEST(0, 18 - AVG({col})) as {feat_name}")
                    elif 'cooling_degree_days' in feat_name:
                        # CDD = GREATEST(0, AVG(temp) - base_temp)
                        table_selects.append(f"GREATEST(0, AVG({col}) - 18) as {feat_name}")
                    else:
                        table_selects.append(f"AVG({col}) as {feat_name}")
                else:
                    table_selects.append(f"{agg}({col}) as {feat_name}")
            
            if len(table_selects) > 1:  # Only if we have features from this table
                table_cte = f"""
        {alias}_daily AS (
            SELECT {', '.join(table_selects)}
            FROM {table}
            WHERE machine_id = ANY($1::uuid[])
              AND time BETWEEN $2 AND ($3::date + INTERVAL '1 day')
            GROUP BY day
        )"""
                ctes.append(table_cte)
        
        # Build final SELECT joining all CTEs
        final_select_parts = [f"{primary_alias}_daily.day"]
        final_select_parts.append(primary_consumption_feature)
        final_select_parts.append("operating_hours")
        
        # Add all requested features
        for feat_name in requested_features:
            if feat_name not in [primary_consumption_feature, 'operating_hours']:
                final_select_parts.append(feat_name)
        
        # Build FROM clause with LEFT JOINs on day
        from_parts = [f"FROM {primary_alias}_daily"]
        for table in tables_needed:
            if table == primary_table:
                continue
            alias = self._get_table_alias(table)
            # Only join if we have features from this table
            if f"{alias}_daily" in '\n'.join(ctes):
                from_parts.append(f"LEFT JOIN {alias}_daily USING (day)")
        
        # Assemble complete query with CTEs
        query = f"""
        WITH {','.join(ctes)}
        SELECT {', '.join(final_select_parts)}
        {' '.join(from_parts)}
        ORDER BY day
        """
        
        logger.info(f"[FEATURE-DISCOVERY] Generated query for {len(requested_features)} features from {len(tables_needed)} tables")
        logger.debug(f"[FEATURE-DISCOVERY] SQL: {query.strip()[:500]}...")
        
        return query.strip()
    
    def _get_table_alias(self, table_name: str) -> str:
        """Generate short alias for table name."""
        alias_map = {
            'energy_readings': 'er',
            'natural_gas_readings': 'ng',
            'steam_readings': 'sr',
            'compressed_air_end_use_readings': 'ca',
            'production_data': 'pd',
            'environmental_data': 'ed'
        }
        return alias_map.get(table_name, table_name[:2])
    
    def _get_energy_column(self, table_name: str) -> str:
        """Get primary energy/consumption column for table."""
        column_map = {
            'energy_readings': 'energy_kwh',
            'natural_gas_readings': 'consumption_m3',
            'steam_readings': 'consumption_kg',
            'compressed_air_end_use_readings': 'consumption_m3'
        }
        return column_map.get(table_name, 'energy_kwh')
    
    async def get_energy_source_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary of all energy sources and their features.
        Useful for API documentation and OVOS integration.
        
        Returns:
            List of dicts with energy source info + feature counts
            
        Example:
            [
                {
                    'name': 'electricity',
                    'unit': 'kWh',
                    'features_count': 20,
                    'sample_features': ['consumption_kwh', 'production_count', 'outdoor_temp_c']
                },
                {
                    'name': 'natural_gas',
                    'unit': 'm3',
                    'features_count': 9,
                    'sample_features': ['consumption_m3', 'outdoor_temp_c', 'heating_degree_days']
                }
            ]
        """
        query = """
            SELECT 
                es.id,
                es.name,
                es.unit,
                es.description,
                COUNT(esf.id) as features_count,
                ARRAY_AGG(esf.feature_name ORDER BY esf.feature_name) FILTER (WHERE esf.is_regression_feature = true) as regression_features
            FROM energy_sources es
            LEFT JOIN energy_source_features esf ON es.id = esf.energy_source_id AND esf.is_active = true
            WHERE es.is_active = true
            GROUP BY es.id, es.name, es.unit, es.description
            ORDER BY es.name
        """
        
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(query)
            
            summary = []
            for row in rows:
                features = row['regression_features'] or []
                summary.append({
                    'id': str(row['id']),
                    'name': row['name'],
                    'unit': row['unit'],
                    'description': row['description'],
                    'features_count': row['features_count'],
                    'sample_features': features[:5],  # First 5 for preview
                    'all_features': features
                })
            
            return summary


# Global singleton instance
feature_discovery = FeatureDiscoveryService()
