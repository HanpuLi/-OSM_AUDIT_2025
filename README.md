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

To ensure scientific rigor, this project employs a triangulated approach combining OSM topological tracing, multi-spectral Earth Observation, and local governance dossier reviews. For NDVI, a strict **Difference-in-Differences (DiD)** methodology with **Seasonal Mann-Kendall** testing isolates vegetative degradation from biological autocorrelation. For LST, a **Paired BACI (Before-After-Control-Impact)** design with **Welch's t-test** and **Mann-Whitney U** quantifies the thermal regime shift from land-use conversion. Both pipelines implement **Pixel-Level Uncertainty Quantification (UQ)**.

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
- **`06_gee_thermal_pipeline.js`** / **`07_plot_thermal_chart.py`**: 
  - **Logic**: Implements a **triple-satellite fusion** (Landsat 7,8,9) to maximise temporal observation density. Extracts LST over a precise 5-vertex polygon delineating the newly-constructed parking lot. 
  - **Algorithm Highlight**: Employs a **Paired BACI** design, removing NDBI masking to measure the pure causal effect of greenfield-to-asphalt conversion. Evaluates $\Delta$T significance via Welch's t-test and Mann-Whitney U.

**To fortify the thermal inference against the physical resolution limits of Landsat TIRS (100m), three advanced auxiliary pipelines (The Tri-Pillar Defense) evaluate the thermodynamic regime shift from distinct vantage points:**

- **Option A: Sensitivity Analysis (`06b`, `07b`)**: Expands the spatial pool to the full 1km² VP development polygon (~50 pixels) and evaluates the Warm Season (Apr-Sep) BACI to radically lower spatial variance and boost statistical power.
- **Phase IV: Spatial Transect Decay (`08`, `09`)**: Extracts 3-year summer LST composites in concentric 50m buffers emanating from the Impact Zone up to 800m. Plots a Distance Gradient Thermal Decay Curve to visually prove advective heat spillover.
- **Phase V: Metabolic Proxy / Evapotranspiration (`10`, `11`)**: Extracts MODIS/MOD16A2GF (500m) 8-Day Actual Evapotranspiration (ET). Employs a DiD BACI to test for a terminal collapse in latent heat flux, proving the physical mechanism driving the UHI.

### Inter-Pipeline Automation (`run_pipeline.sh`)
While the Google Earth Engine scripts (`04`, `06`, `06b`, `08`, `10`) must be executed natively in the GEE cloud to leverage Google's server-side computation, the entire local analytical workflow is fully automated.

Executing `./scripts/run_pipeline.sh` automatically daisy-chains the spatial reprojection (`02`), geospatial formatting (`03`), and advanced statistical rendering (`05`, `07`, `07b`, `09`, `11`), selectively executing Python modules if their respective GEE `raw_telemetry` CSVs are present.

### Phase III: Institutional Governance & Discourse Audit

**Objective:** To cross-reference spatial realities with municipal planning compliance (EIA 18/01212/OUT).

A structural analysis of Spelthorne Borough Council's grey literature is documented in `documentation/`. This phase contrasts corporate ESG assertions with physical facts extracted in Phases I and II.

## 3. Key Empirical Findings (Shepperton Case Study)

The execution of this pipeline yielded the following statistically verified metrics:

- **Logistical Sprawl:** A total land conversion of 13.21 hectares (132,123.11 SQM) of the Green Belt into impermeable asphalt parking surfaces (distinct from the 16.4 ha of building floorspace reported in the EIA).
- **Energy Parasitism:** The identification of 17 new high-capacity grid nodes for virtual rendering and HVAC maintenance.
- **Biophysical Erasure (NDVI):** A permanent structural collapse from a baseline NDVI of ~0.635 to ~0.28, isolated via **DiD**. The devastation trend is definitively verified by **Seasonal Mann-Kendall** testing (p < 0.001, statistically significant at 99.9% confidence). The adjacent Control Zone greenbelt remained completely stable over the 8-year continuum.
- **Thermodynamic Escalation (LST) & Metabolic Rift:** A Tri-Pillar methodological defense confirms severe thermodynamic disruption:
  - *I. Inferential Anchor (Paired BACI)*: Triple-satellite fusion detects a thermal regime shift of **+0.56°C** in the Impact–Control differential (Welch p=0.080, MW p=0.065). The marginal p-value honestly reflects the strict 100m native resolution bounds (~3 thermal pixels). However, the Option A Sensitivity Analysis (VP Full Polygon, Apr-Sep) amplifies statistical power, confirming a highly significant **+0.85°C** shift (p < 0.001).
  - *II. Spatial Spillover (Distance Gradient)*: The Spatial Transect thermal decay analysis demonstrates severe point-source heat advection radiating outward up to 200m before returning to background homeostasis.
  - *III. Latent Heat Collapse (Evapotranspiration)*: The MODIS ET proxy reveals a terminal collapse in Actual Evapotranspiration (DiD $\Delta$ET), proving the physical destruction of latent heat flux and documenting the mechanic engine behind the UHI effect.

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
│   ├── 06b_gee_thermal_sensitivity.js
│   ├── 07_plot_thermal_chart.py
│   ├── 07b_plot_thermal_sensitivity.py
│   ├── 08_gee_transect_decay.js
│   ├── 09_plot_transect_decay.py
│   ├── 10_gee_evapotranspiration.js
│   ├── 11_plot_evapotranspiration.py
│   └── run_pipeline.sh         # Shell script to execute all local Python stages
├── data/
│   ├── raw_spatial/            # Raw JSON extracts (WGS84)
│   ├── raw_telemetry/          # Satellite CSVs from GEE
│   └── processed/              # Kepler CSVs and projections
├── visualisations/             # Output NDVI/LST charts
├── documentation/              # Sprawl zone point rationale & OSM accuracy citations
├── requirements.txt            # Python dependencies (incl. pymannkendall, statsmodels)
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
All `.js` scripts (`04`, `06`, `06b`, `08`, `10`) are designed for the [Google Earth Engine Code Editor](https://code.earthengine.google.com/). Users must execute these manually to generate the `.csv` telemetry files in `data/raw_telemetry/` before running the Python charting scripts.

## 6. Licensing

This project is submitted for the PMP ELSS module assessment. 
Copyright (c) 2026 Hanpu Li (Caitlyn Lye). Released under the MIT License.
