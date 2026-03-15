import json
import csv
import os
from shapely.geometry import shape
from shapely.ops import transform
import pyproj

# Project root: one level up from scripts/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Coordinate projection for accurate area calculation
WGS84 = "epsg:4326"
BNG = "epsg:27700"
projector = pyproj.Transformer.from_crs(WGS84, BNG, always_xy=True).transform

def extract_features_for_kepler(file_path, sector_name):
    """
    Extracts geographical features from GeoJSON and formats them for Kepler.gl.
    Identifies Power Nodes and centroids of Logistical Sprawl (Parking).
    """
    features_list = []
    
    if not os.path.exists(file_path):
        print(f"[WARNING] File not found: {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to decode JSON from {file_path}")
            return []
        
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        
        if not geom:
            continue

        # 1. Extract Power Infrastructure Nodes (Point data)
        if 'power' in props and geom['type'] == 'Point':
            lon, lat = geom['coordinates']
            features_list.append({
                'sector': sector_name,
                'audit_type': 'Energy_Displacement',
                'category': props.get('power', 'infrastructure'),
                'latitude': lat,
                'longitude': lon,
                'intensity': 50.0  # Fixed weight for heatmap visibility
            })
            
        # 2. Extract Logistical Sprawl (Polygon Centroids for Heatmap weighting)
        if props.get('amenity') == 'parking' and geom['type'] in ['Polygon', 'MultiPolygon']:
            s = shape(geom)
            centroid = s.centroid
            # Project to BNG (EPSG:27700) for accurate area in square metres
            s_projected = transform(projector, s)
            features_list.append({
                'sector': sector_name,
                'audit_type': 'Logistical_Sprawl',
                'category': 'asphalt_surface',
                'latitude': centroid.y,
                'longitude': centroid.x,
                'intensity': s_projected.area  # Area in square metres
            })
            
    return features_list

if __name__ == "__main__":
    # Ensure the output directory exists
    output_dir = os.path.join(PROJECT_ROOT, 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)

    # Process both studio sectors
    shepperton_data = extract_features_for_kepler(
        os.path.join(PROJECT_ROOT, 'data', 'raw_spatial', 'export_shepperton.geojson'), 'Shepperton')
    longcross_data = extract_features_for_kepler(
        os.path.join(PROJECT_ROOT, 'data', 'raw_spatial', 'export_longcross.geojson'), 'Longcross')

    all_data = shepperton_data + longcross_data

    # Define output path
    output_file = os.path.join(output_dir, 'kepler_gl_visualisation.csv')

    # Write to CSV with clear headers for Kepler.gl auto-detection
    fieldnames = ['sector', 'audit_type', 'category', 'latitude', 'longitude', 'intensity']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"--- KEPLER DATA GENERATION COMPLETE ---")
    print(f"Total entries processed: {len(all_data)}")
    print(f"File saved to: {output_file}")
    print("ACTION: Drag this file into kepler.gl/demo and use 'audit_type' for colour filtering.")