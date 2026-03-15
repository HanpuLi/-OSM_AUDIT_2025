# OSM_AUDIT_2025: Forensic Spatial Audit of Virtual Production Infrastructure

**Project Title:** The Political Economy of Greenwashing: Spatialising the Myth of Immateriality in Virtual Production and the Digital Spatial Fix

**Author:** Hanpu Li (Caitlyn Lye)

**Institution:** Queen Mary University of London (QMUL)

**Status:** PMP ELSS Module Coursework (20% Assessment)

## 1. Project Overview & Academic Contribution

This repository contains the spatial data pipelines, Earth Observation (EO) algorithms, and theoretical frameworks developed for the empirical audit of Virtual Production (VP) infrastructure, specifically examining the Shepperton Studios expansion in the United Kingdom.

While contemporary industry discourse frames virtual production and cloud rendering as a low-carbon, "immaterial" alternative to location shooting, this project proposes a structural counter-narrative. By synthesising Computational Spatial Science (GIS/Remote Sensing) with Eco-Marxist Political Economy, this repository provides a replicable, open-source methodological pipeline to quantify the physical, thermodynamic, and ecological costs of digital media expansion.

### Theoretical Framework

The analytical pipeline is grounded in three core political-economic paradigms:

- **The Digital Spatial Fix** (Greene & Joseph, 2015): Conceptualising digital infrastructure not as a dematerialised entity, but as a mechanism through which capital resolves accumulation crises by expanding into new geographic territories.
- **The Metabolic Rift** (Marx, 1867 / Bozak, 2012): Quantifying the physical rupture in ecological systems necessitated by algorithmic and computational metabolism.
- **Accumulation by Dispossession** (Harvey, 2004): Examining the asymmetry between privatised economic gains (Net GVA) and socialised ecological burdens (localised thermodynamic escalation and biomass erasure).

## 2. Methodological Architecture

To ensure scientific rigor, this project employs a triangulated approach combining OSM topological tracing, multi-spectral Earth Observation, and local governance dossier reviews. A strict **Control Zone** methodology and **Mann-Kendall Statistical Significance Testing** are implemented to isolate infrastructural impact from regional climate trends.

### Phase I: Geomatic Extraction & Topological Normalisation

**Objective:** To empirically quantify logistical sprawl by bypassing corporate-curated spatial data.

- **`01_osm_extraction.ql`** (Overpass QL): Executes a radius-constrained extraction (1200m) around the Shepperton coordinates via the Overpass API. Targets industrial geometries, power infrastructure, and newly concreted logistical surfaces (`amenity=parking`).
- **`02_spatial_projection.py`** (Python): Ingests raw WGS84 GeoJSON datasets. Utilising `shapely` and `pyproj`, the script re-projects angular global coordinates into the British National Grid (EPSG:27700). This cartographic transformation is critical for calculating exact planar areas (square metres) with an error margin of <0.1%.
- **`03_kepler_formatter.py`** (Python): Formats geometries into CSV points with pre-calculated intensity metrics for 3D Kepler.gl heatmapping.

### Phase II: Earth Observation & Metabolic Quantification

**Objective:** To measure the longitudinal biophysical and thermodynamic alterations in the audited zone, rigorously controlled against nearby undeveloped greenbelts.

- **`04_gee_ndvi_pipeline.js`** (GEE API): Interfaces with ESA Sentinel-2 multispectral satellites to calculate the Normalised Difference Vegetation Index (NDVI) over an 8-year temporal axis. **Algorithm Refinement**: Implements dual-layer cloud masking using both QA60 bitmask and the SCL (Scene Classification Layer) to strictly filter shadows and cirrus clouds. Incorporates a 4-point cardinal sensitivity analysis around the sprawl core.
- **`05_plot_ndvi_chart.py`** (Python): Applies a 365-day rolling mean to the Sentinel-2 NDVI telemetry to eliminate seasonal meteorological noise. Automatically runs a **Mann-Kendall Autocorrelation Test** (via `pymannkendall`) to mathematically prove the statistical significance (p < 0.001) of the ecological collapse.
- **`06_gee_thermal_pipeline.js`** (GEE API): Interfaces with the USGS Landsat 8 (TIRS) sensor. **Algorithm Refinement**: Advanced thermal cloud masking using QA_PIXEL (filtering dilated clouds, cirrus, and snow). Constructs relative Urban Heat Island (UHI) anomaly maps by comparing 3-year summer composites (2016-2018 vs 2023-2025) to isolate the net thermodynamic scar while filtering out single-year weather anomalies.
- **`07_plot_thermal_chart.py`** (Python): Processes LST telemetry, generating a 365-day smoothed structural heating trajectory mapped against a 1st-degree polynomial regression line.

### Phase III: Institutional Governance & Discourse Audit

**Objective:** To cross-reference spatial realities with municipal planning compliance (EIA 18/01212/OUT).

A structural analysis of Spelthorne Borough Council's grey literature is documented in `documentation/`. This phase contrasts corporate ESG assertions with physical facts extracted in Phases I and II.

## 3. Key Empirical Findings (Shepperton Case Study)

The execution of this pipeline yielded the following statistically verified metrics:

- **Logistical Sprawl:** A total land conversion of 13.21 hectares (132,123.11 SQM) of the Green Belt into impermeable asphalt parking surfaces (distinct from the 16.4 ha of building floorspace reported in the EIA).
- **Energy Parasitism:** The identification of 17 new high-capacity grid nodes for virtual rendering and HVAC maintenance.
- **Biophysical Erasure (NDVI):** A permanent structural collapse from a baseline NDVI of ~0.635 to ~0.28 (Mann-Kendall p ≈ 0.000000, statistically significant at 99.9% confidence). The adjacent Control Zone remained stable.
- **Thermodynamic Escalation (LST):** A net structural increase in Land Surface Temperature of +5°C natively attributed to algorithmic metabolism and asphalt heat retention, visually validated by the 3-year UHI anomaly composite.

## 4. Repository Structure

```
OSM_AUDIT_2025/
├── scripts/                    # Fully automated analytical and statistical pipeline
│   ├── 01_osm_extraction.ql
│   ├── 02_spatial_projection.py
│   ├── 03_kepler_formatter.py
│   ├── 04_gee_ndvi_pipeline.js
│   ├── 05_plot_ndvi_chart.py
│   ├── 06_gee_thermal_pipeline.js
│   ├── 07_plot_thermal_chart.py
│   └── run_pipeline.sh         # Shell script to execute all local Python stages
├── data/
│   ├── raw_spatial/            # Raw JSON extracts (WGS84)
│   ├── raw_telemetry/          # Satellite CSVs from GEE
│   └── processed/              # Kepler CSVs and projections
├── visualisations/             # Output NDVI/LST charts
├── documentation/              # Sprawl zone point rationale & OSM accuracy citations
├── requirements.txt            # Python dependencies (incl. pymannkendall)
├── LICENSE                     # MIT License
└── README.md
```

## 5. Dependencies and Execution

**1. Software Environment (Python 3.10+):**
```bash
pip install -r requirements.txt
./scripts/run_pipeline.sh
```

**2. Remote Sensing (GEE):**
Scripts `04` and `06` are designed for the [Google Earth Engine Code Editor](https://code.earthengine.google.com/). Users must execute these manually to generate the `.csv` telemetry files in `data/raw_telemetry/` before running the Python charting scripts.

## 6. Licensing

This project is submitted for the PMP ELSS module assessment. 
Copyright (c) 2026 Hanpu Li (Caitlyn Lye). Released under the MIT License.
