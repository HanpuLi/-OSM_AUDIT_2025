"""
03_kepler_formatter.py
从 GeoJSON 提取 Power Nodes + Parking Centroids，输出 Kepler.gl CSV
"""

import json
import csv
import os
from shapely.geometry import shape
from shapely.ops import transform
import pyproj

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WGS84 = "epsg:4326"
BNG = "epsg:27700"
projector = pyproj.Transformer.from_crs(WGS84, BNG, always_xy=True).transform

def extract_features_for_kepler(file_path, sector_name):
    """提取电力节点 (Point) 和停车场质心 (Polygon centroid)，返回 dict 列表"""
    features_list = []
    
    if not os.path.exists(file_path):
        print(f"[WARNING] File not found: {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON: {file_path}")
            return []
        
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        
        if not geom:
            continue

        if 'power' in props:
            lon, lat = None, None
            if geom['type'] == 'Point':
                lon, lat = geom['coordinates']
            elif geom['type'] in ['Polygon', 'MultiPolygon']:
                s = shape(geom)
                lon, lat = s.centroid.x, s.centroid.y
                
            if lon is not None and lat is not None:
                features_list.append({
                    'sector': sector_name,
                    'audit_type': 'Energy_Displacement',
                    'category': props.get('power', 'infrastructure'),
                    'latitude': lat,
                    'longitude': lon,
                    'intensity': 50.0
                })

        if props.get('amenity') == 'parking' and geom['type'] in ['Polygon', 'MultiPolygon']:
            s = shape(geom)
            centroid = s.centroid
            s_projected = transform(projector, s)  # BNG 投影后算面积
            features_list.append({
                'sector': sector_name,
                'audit_type': 'Logistical_Sprawl',
                'category': 'asphalt_surface',
                'latitude': centroid.y,
                'longitude': centroid.x,
                'intensity': s_projected.area  # sqm
            })
            
    return features_list

if __name__ == "__main__":
    output_dir = os.path.join(PROJECT_ROOT, 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)

    shepperton_data = extract_features_for_kepler(
        os.path.join(PROJECT_ROOT, 'data', 'raw_spatial', 'export_shepperton.geojson'), 'Shepperton')
    longcross_data = extract_features_for_kepler(
        os.path.join(PROJECT_ROOT, 'data', 'raw_spatial', 'export_longcross.geojson'), 'Longcross')

    all_data = shepperton_data + longcross_data
    output_file = os.path.join(output_dir, 'kepler_gl_visualisation.csv')

    fieldnames = ['sector', 'audit_type', 'category', 'latitude', 'longitude', 'intensity']
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"Done. {len(all_data)} entries -> {output_file}")