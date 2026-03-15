# -*- coding: utf-8 -*-
"""
OSM_AUDIT_2025: Spatial Projection and Quantification Utility
Converts raw WGS84 GeoJSON data into physical metrics using the British National Grid.
"""

import json
import os
import logging
from shapely.geometry import shape
import pyproj
from shapely.ops import transform

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Project root: one level up from scripts/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define Coordinate Reference Systems
# WGS84 (Global Degrees) -> EPSG:27700 (British National Grid in Metres)
WGS84 = "epsg:4326"
BNG = "epsg:27700"
projector = pyproj.Transformer.from_crs(WGS84, BNG, always_xy=True).transform

def run_spatial_audit(file_path):
    """
    Executes a quantitative audit of spatial data.
    Returns: (total_parking_area, power_node_count)
    """
    if not os.path.exists(file_path):
        logger.error("Source file missing: %s", file_path)
        return 0.0, 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in %s", file_path)
            return 0.0, 0
            
    parking_area = 0.0
    power_nodes = 0
    
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        
        if not geom:
            continue
            
        # 1. Audit Power Infrastructure Nodes
        if 'power' in props and props['power'] is not None:
            power_nodes += 1
            
        # 2. Quantify Logistical Sprawl (Parking Polygons)
        if props.get('amenity') == 'parking' and geom.get('type') in ['Polygon', 'MultiPolygon']:
            # Project geometry to BNG for accurate area calculation
            s = shape(geom)
            s_projected = transform(projector, s)
            parking_area += s_projected.area
            
    return parking_area, power_nodes

if __name__ == "__main__":
    logger.info("--- INITIATING EMPIRICAL SPATIAL AUDIT (OSM_AUDIT_2025) ---")
    
    # Audit Paths (relative to project root)
    shep_path = os.path.join(PROJECT_ROOT, 'data', 'raw_spatial', 'export_shepperton.geojson')
    long_path = os.path.join(PROJECT_ROOT, 'data', 'raw_spatial', 'export_longcross.geojson')
    
    # Execute calculations
    shep_area, shep_pwr = run_spatial_audit(shep_path)
    long_area, long_pwr = run_spatial_audit(long_path)
    
    total_area = shep_area + long_area
    total_hectares = total_area / 10000
    
    # Detailed Console Output
    logger.info("SHEPPERTON_SECTOR: %,.2f SQM | Nodes: %d", shep_area, shep_pwr)
    logger.info("LONGCROSS_SECTOR:  %,.2f SQM | Nodes: %d", long_area, long_pwr)
    logger.info("-" * 50)
    logger.info("AGGREGATE LOGISTICAL SPRAWL: %,.2f SQM", total_area)
    logger.info("TOTAL LAND CONVERSION:      %,.4f Hectares", total_hectares)
    logger.info("TOTAL POWER ANCHORS:        %d", shep_pwr + long_pwr)
    logger.info("--- AUDIT COMPLETE: DATA READY FOR VISUALISATION ---")