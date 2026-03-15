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

To ensure scientific rigor, this project employs a triangulated approach combining OSM topological tracing, multi-spectral Earth Observation, and local governance dossier reviews. A strict **Difference-in-Differences (DiD)** methodology, **Seasonal Mann-Kendall Statistical Significance Testing**, and **Pixel-Level Uncertainty Quantification (UQ)** are meticulously implemented to mathematically isolate localized infrastructural impact from global climate trends and biological autocorrelation.

### Phase I: Geomatic Extraction & Topological Normalisation

**Objective:** To empirically quantify logistical sprawl by bypassing corporate-curated spatial data.

- **`01_osm_extraction.ql`** (Overpass QL): 
  - **Logic**: Executes a radius-constrained extraction (1200m) around the Shepperton coordinates via the Overpass API. Targets industrial geometries, power infrastructure (132kV transformers), and newly concreted logistical surfaces (`amenity=parking`).
- **`02_spatial_projection.py`** (Python): 
  - **Logic**: Ingests WGS84 GeoJSON satellite vectors. Utilising `shapely.geometry` and `pyproj.Transformer`, the script mathematically transforms angular geographic coordinates into the British National Grid (EPSG:27700) Cartesian plane.
  - **Why this matters**: Calculating areas directly in WGS84 introduces severe spherical distortions. Projecting to EPSG:27700 allows the script to compute exact planar land-conversion metrics (in square metres) with an error margin of <0.1%.
- **`03_kepler_formatter.py`** (Python): 
  - **Logic**: Iterates over projected spatial geometries, calculating their centroids and planar areas. Exports a rigorously formatted CSV infused with intensity weightings designed specifically for 3D extrusion rendering in Kepler.gl.

### Phase II: Earth Observation & Metabolic Quantification

**Objective:** To measure the longitudinal biophysical and thermodynamic alterations in the audited zone, rigorously controlled against nearby undeveloped greenbelts.

- **`04_gee_ndvi_pipeline.js`** (Google Earth Engine API - JavaScript): 
  - **Logic**: Interfaces with the ESA Sentinel-2 (S2_SR_HARMONIZED) multispectral constellation. Extracts the Normalised Difference Vegetation Index (NDVI), calculating both geometric spatial means and pixel-level standard deviations (`stdDev`) across an 8-year temporal axis.
  - **Algorithm Highlight**: Implements a dual-layer cloud masking function using both the QA60 bitmask and the advanced SCL (Scene Classification Layer) to strictly filter cloud shadows, cirrus bands, and snow. Pivotally exports spatial variance telemetry in Wide-Format for Academic Uncertainty Quantification (UQ).
- **`05_plot_ndvi_chart.py`** (Python): 
  - **Logic**: Ingests the raw NDVI telemetry CSV from GEE. 
  - **Algorithm Highlight**: Employs a 3rd-order Savitzky-Golay signal filter (`scipy.signal.savgol_filter`, window=365 days) to preserve peak amplitude of seasonal vegetation phenology. Utilizes **Difference-in-Differences (DiD)** against the Control Zone greenbelt to calculate the net anthropogenic signal ($\Delta$ NDVI). Applies a rigorous Non-Parametric **Seasonal Mann-Kendall test** (`pymannkendall`, `period=365`) to algebraically neutralize biological autocorrelation and verify the degradation core. Renders a $\pm 1 \sigma$ semi-transparent error band encapsulating spatial variance (UQ) for ultimate empirical defense.
- **`06_gee_thermal_pipeline.js`** (Google Earth Engine API - JavaScript): 
  - **Logic**: Interfaces with the USGS Landsat 8 (TIRS) thermal sensor. 
  - **Algorithm Highlight**: Performs deep bitwise QA_PIXEL masking (filtering dilated clouds, cirrus, and snow) and converts raw Digital Numbers (DN) to Land Surface Temperature (LST). Explicitly extracts pixel-level spatial standard deviation to power downstream UQ, alongside calculating robust Urban Heat Island (UHI) anomaly composites by averaging 3 entire summers (2016-2018 vs. 2023-2025).
- **`07_plot_thermal_chart.py`** (Python): 
  - **Algorithm Highlight**: Mirrors the NDVI pipeline's rigorous statistical architecture. Utilizes **Difference-in-Differences (DiD)** against the Control Zone greenbelt to isolate anthropogenic thermal forcing from regional climate drift. Applies a **Seasonal Mann-Kendall test** (`pymannkendall`, `period=365`) on the $\Delta$ LST signal to verify significance. A Savitzky-Golay filter (`window=181 days`, tuned for Landsat 8's sparser 16-day revisit cadence) smooths the seasonal sinusoidal oscillation while preserving amplitude. Renders a $\pm 1 \sigma$ Spatial Variance UQ error band.

### Inter-Pipeline Automation (`run_pipeline.sh`)
While the Google Earth Engine scripts (`04`, `06`) must be executed natively in the GEE cloud to leverage Google's server-side computation (downloading terabytes of raw satellite imagery locally is computationally unfeasible), the entire local analytical workflow is fully automated.

Executing `./scripts/run_pipeline.sh` automatically daisy-chains the spatial reprojection (`02`), geospatial formatting (`03`), and advanced statistical rendering (`05`, `07`), producing presentation-ready analytics instantly once the raw CSV telemetry is placed in the required folder.

### Phase III: Institutional Governance & Discourse Audit

**Objective:** To cross-reference spatial realities with municipal planning compliance (EIA 18/01212/OUT).

A structural analysis of Spelthorne Borough Council's grey literature is documented in `documentation/`. This phase contrasts corporate ESG assertions with physical facts extracted in Phases I and II.

## 3. Key Empirical Findings (Shepperton Case Study)

The execution of this pipeline yielded the following statistically verified metrics:

- **Logistical Sprawl:** A total land conversion of 13.21 hectares (132,123.11 SQM) of the Green Belt into impermeable asphalt parking surfaces (distinct from the 16.4 ha of building floorspace reported in the EIA).
- **Energy Parasitism:** The identification of 17 new high-capacity grid nodes for virtual rendering and HVAC maintenance.
- **Biophysical Erasure (NDVI):** A permanent structural collapse from a baseline NDVI of ~0.635 to ~0.28, isolated via **DiD**. The devastation trend is definitively verified by **Seasonal Mann-Kendall** testing (p < 0.001, statistically significant at 99.9% confidence). The adjacent Control Zone greenbelt remained completely stable over the 8-year continuum.
- **Thermodynamic Escalation (LST):** A net structural increase in Land Surface Temperature of +3°C in the Sprawl Zone, isolated via **DiD** against the Control Zone and verified by **Seasonal Mann-Kendall** testing (p = 1.524e-02, statistically significant at 95% confidence). The adjacent Control Zone greenbelt exhibited no comparable escalation. The thermodynamic scar is further corroborated by the 3-year UHI anomaly composite and rigorously bounded by Pixel-Level UQ error bars.

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
