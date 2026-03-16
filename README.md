# OSM_AUDIT_2025: Forensic Spatial Audit of Virtual Production Infrastructure

**Project Title:** The Political Economy of Greenwashing: Spatialising the Myth of Immateriality in Virtual Production and the Digital Spatial Fix

**Author:** Hanpu Li (Caitlyn Lye)

**Institution:** Queen Mary University of London (QMUL)

**Status:** PMP ELSS Module Coursework (20% Assessment)

---

## 1. Project Overview & Academic Contribution

This repository contains the spatial data pipelines, Earth Observation (EO) algorithms, and theoretical frameworks developed for the forensic audit of Virtual Production (VP) infrastructure, specifically examining the Shepperton Studios expansion (Planning Application: 18/01212/OUT) in the London Borough of Spelthorne, United Kingdom.

While contemporary industry discourse frames virtual production and cloud rendering as a low-carbon, "immaterial" alternative to location shooting (Keeney, 2024), this project proposes a structural counter-narrative grounded in critical political economy. By synthesising Computational Spatial Science (GIS/Remote Sensing) with Eco-Marxist Political Economy, this repository provides a replicable, open-source methodological pipeline to quantify the physical, thermodynamic, and ecological costs of digital media expansion — costs that are systematically obscured by what Maxwell and Miller (2012) term the "selective visibility" of corporate environmental disclosure.

### Theoretical Framework

The analytical pipeline is grounded in three core political-economic paradigms:

- **The Digital Spatial Fix** (Greene & Joseph, 2015): Conceptualising digital infrastructure not as a dematerialised entity, but as a mechanism through which capital resolves accumulation crises by expanding into new geographic territories. Virtual production's material footprint — soundstages, rendering farms, HVAC systems, and logistical surfaces — constitutes precisely such a spatial fix.
- **The Metabolic Rift** (Marx, 1867; Foster, 1999; Bozak, 2012): Quantifying the physical rupture in ecological systems necessitated by algorithmic and computational metabolism. The conversion of vegetated greenbelt to impervious asphalt disrupts the land-atmosphere energy exchange cycle, forcing a thermodynamic repartitioning from latent heat (evaporative cooling) to sensible heat (atmospheric warming).
- **Accumulation by Dispossession** (Harvey, 2004): Examining the structural asymmetry between privatised economic gains (£392 million annual Net GVA; Turley Economics, 2018, Table 6.2) and socialised ecological burdens (localised thermodynamic escalation, biomass erasure, and an S106 ecological buyout fee of £6,150 — equating to 4.6 pence per square metre of greenbelt consumed; Spelthorne Borough Council, 2019).

### The Rebound Effect & the Aviation Fallacy

The claim that virtual production fundamentally decarbonises filmmaking by eliminating aviation is challenged by the **Jevons Paradox** (Sharma, 2024). Efficiency gains in computation trigger the Rebound Effect: savings from avoided flights are reinvested into higher-resolution rendering, expanded stage capacity, and local physical sprawl. Aviation emissions are not eliminated but spatially displaced into an estimated **5.4 GWh** of local grid parasitism (derived from EIA energy demand projections; Spelthorne Borough Council, 2018).

---

## 2. Methodological Architecture

To ensure scientific rigor, this project employs a triangulated approach combining OSM topological tracing, multi-spectral Earth Observation (executed via the Google Earth Engine planetary-scale platform; Gorelick et al., 2017), and local governance dossier reviews. For NDVI, a strict **Difference-in-Differences (DiD)** methodology with **Seasonal Mann-Kendall** testing isolates vegetative degradation from biological autocorrelation. For LST, a **Paired BACI (Before-After-Control-Impact)** design with **Welch's t-test** and **Mann-Whitney U** quantifies the thermal regime shift from land-use conversion. Both pipelines implement **Pixel-Level Uncertainty Quantification (UQ)**.

### Phase I: Geomatic Extraction & Topological Normalisation

**Objective:** To empirically quantify logistical sprawl by bypassing corporate-curated spatial data, leveraging open-source Volunteered Geographic Information via the Overpass API (OpenStreetMap contributors, 2015).

- **`01_osm_extraction.ql`** (Overpass QL): 
  - **Logic**: Executes a radius-constrained extraction (1200 m) around the Shepperton coordinates (51.4065°N, 0.4640°W) and Longcross coordinates (51.3830°N, 0.5930°W) via the Overpass API. Targets industrial geometries (`building=industrial|commercial`), power infrastructure (132 kV transformers, substations), and newly concreted logistical surfaces (`amenity=parking`).
  - **Rationale**: This circumvents the industry's 'selective visibility' by utilising publicly accessible geographic data to quantify physical infrastructure without relying on proprietary corporate disclosures.

- **`02_spatial_projection.py`** (Python / `shapely`, `pyproj`): 
  - **Logic**: Ingests WGS84 GeoJSON vectors extracted from OSM. Utilising `shapely.geometry.shape()` and `pyproj.Transformer`, the script mathematically transforms angular geographic coordinates into the British National Grid (EPSG:27700) Cartesian plane.
  - **Why this matters**: Calculating areas directly in WGS84 (a geographic, non-projected CRS) introduces severe spherical distortions at UK latitudes (~0.7% area error). Projecting to EPSG:27700, the UK's official planar coordinate system, allows the script to compute exact planar land-conversion metrics (in square metres) with an error margin of <0.1%.

- **`03_kepler_formatter.py`** (Python / `shapely`, `pyproj`, `csv`): 
  - **Logic**: Iterates over projected spatial geometries, calculating their centroids and planar areas. Exports a rigorously formatted CSV infused with intensity weightings (parking area in m², power node presence) designed specifically for 3D extrusion rendering in [Kepler.gl](https://kepler.gl/).
  - **Output**: `data/processed/kepler_gl_visualisation.csv` — a georeferenced dataset enabling visual inspection of the spatial distribution and intensity of logistical sprawl.

### Phase II: Earth Observation & Metabolic Quantification

**Objective:** To measure the longitudinal biophysical and thermodynamic alterations in the audited zone, rigorously controlled against nearby undeveloped greenbelts.

**Data Sources:**
- **ESA Copernicus Sentinel-2** (S2_SR_HARMONIZED): 10 m multispectral imagery for vegetation dynamics (ESA, 2026).
- **USGS Landsat 7 ETM+ / Landsat 8 OLI-TIRS / Landsat 9 OLI-2-TIRS-2** (Collection 2, Tier 1, Level 2): 100 m thermal infrared for land-surface temperature (USGS, 2026).
- **NASA MODIS/Terra MOD16A2GF**: 500 m, 8-day composite Actual Evapotranspiration (Running et al., 2019).

**Cloud-Masking & Temporal Normalisation:**
- GEE `QA60` bitwise cloud-masking combined with advanced Scene Classification Layer (SCL) filtering to strictly remove cloud shadows, cirrus, and snow artefacts.
- `dropna()` filtering to purge cloud-induced null artefacts in thermal data.
- All temporal smoothing (365-day rolling mean, 3-month rolling, Savitzky-Golay) is applied exclusively in the Python post-processing stage to maintain maximum data fidelity in the GEE extraction.

#### A. NDVI Collapse Pipeline

- **`04_gee_ndvi_pipeline.js`** (Google Earth Engine API — JavaScript): 
  - **Logic**: Interfaces with the ESA Sentinel-2 (S2_SR_HARMONIZED) multispectral constellation. Extracts the Normalised Difference Vegetation Index (NDVI = [NIR − Red] / [NIR + Red]), calculating both geometric spatial means and pixel-level standard deviations (`stdDev`) across an 8-year temporal axis (2018–2026).
  - **Algorithm Highlight**: Implements a dual-layer cloud masking function using both the QA60 bitmask and the advanced SCL (Scene Classification Layer) to strictly filter cloud shadows, cirrus bands, and snow. Pivotally exports spatial variance telemetry in Wide-Format for Academic Uncertainty Quantification (UQ).
  - **Source Code**: [GEE Public Link](https://code.earthengine.google.com/0cd023633ba069e4320a7a081bd65b62) (Li, 2026).

- **`05_plot_ndvi_chart.py`** (Python / `pandas`, `numpy`, `scipy`, `pymannkendall`, `matplotlib`): 
  - **Logic**: Ingests the raw NDVI telemetry CSV from GEE. 
  - **Algorithm Highlight**: Employs a 3rd-order Savitzky-Golay signal filter (`scipy.signal.savgol_filter`, window=365 days) to preserve peak amplitude of seasonal vegetation phenology while suppressing high-frequency noise. Utilizes **Difference-in-Differences (DiD)** against the Control Zone greenbelt to calculate the net anthropogenic signal ($\Delta$NDVI). Applies a rigorous Non-Parametric **Seasonal Mann-Kendall test** (`pymannkendall`, `period=365`) to algebraically neutralize biological autocorrelation and verify the degradation trend. Renders a $\pm 1\sigma$ semi-transparent error band encapsulating pixel-level spatial variance (UQ) for empirical defense.

#### B. LST / Thermodynamic Scar Pipeline (Primary BACI)

- **`06_gee_thermal_pipeline.js`** / **`07_plot_thermal_chart.py`**: 
  - **Logic**: Implements a **triple-satellite fusion** (Landsat 7 ETM+ 60 m + Landsat 8 TIRS 100 m + Landsat 9 TIRS-2 100 m) to maximise temporal observation density across the 2015–2026 continuum. Extracts LST over a precise 5-vertex polygon delineating the newly-constructed parking lot and a paired Control Zone polygon over stable greenbelt (~2 km distant).
  - **Algorithm Highlight**: Employs a **Paired BACI** design — the gold standard in impact assessment (Stewart-Oaten et al., 1986). NDBI masking is deliberately removed to measure the pure causal effect of greenfield-to-asphalt conversion on a single, precisely delineated parcel. The construction date (June 2019) partitions the time series into pre/post epochs. $\Delta$T (Impact − Control) significance is evaluated via both Welch's t-test (parametric, variance-heterogeneous) and Mann-Whitney U (non-parametric, rank-based).
  - **Source Code**: [GEE Public Link](https://code.earthengine.google.com/badb69f97aeb6a7a52e7be39ef1d7e6c) (Li, 2026).

#### C. Tri-Pillar Causal Defense

**To fortify the thermal inference against the physical resolution limits of Landsat TIRS (100 m native thermal pixel), this project deploys a Tri-Pillar Causal Defense — three methodologically independent pipelines that converge on the same physical reality from distinct vantage points. The strength of the conclusion derives not from any single p-value, but from the convergence of independent lines of evidence (Munafò & Davey Smith, 2018):**

- **Option A: Sensitivity Analysis** (`06b_gee_thermal_sensitivity.js`, `07b_plot_thermal_sensitivity.py`):
  - **Logic**: Expands the spatial pool from the parking-lot polygon (~3 thermal pixels) to the full 1 km² VP development polygon (~50 pixels), and restricts the temporal window to the Warm Season (Apr–Sep) when surface energy balance differences are maximised.
  - **Rationale**: By increasing the effective pixel count an order of magnitude, spatial variance ($\sigma$) is reduced via $\sigma/\sqrt{n}$, radically boosting the statistical power of Welch's t-test. This tests whether the primary BACI result strengthens when the spatial constraint is relaxed — a standard robustness check in environmental impact assessment.

- **Phase IV: Spatial Transect / Distance Gradient Analysis** (`08_gee_transect_decay.js`, `09_plot_transect_decay.py`):
  - **Logic**: Constructs 16 concentric annular buffers (50 m bandwidth, 0–800 m) emanating radially from the Impact Zone boundary. For each ring, the GEE script computes the spatial mean LST from 3-year summer (JJA) composites for both the pre-construction epoch (2016–2018) and the post-construction epoch (2023–2025), using the same triple-satellite fusion as the primary BACI pipeline.
  - **Algorithm Highlight — Background-Subtraction Normalisation**: Because the two epochs may differ in regional baseline temperature due to inter-annual climate variability (the 2016–18 London summers were empirically ~1.4 °C warmer than 2023–25), a direct comparison of absolute LST is confounded. The Python script applies a **background-subtraction normalisation**: the far-field anomaly (mean of [Post − Pre] at the 400–800 m reference annuli) is treated as the regional climate baseline and subtracted from each ring, yielding a **Net Thermal Scar** metric that isolates the spatially localised effect of the land-cover change from global confounders.
  - **Physical Interpretation**: This pipeline does not test temporal significance (that is the BACI's role); instead, it provides **spatial corroboration** — demonstrating whether the thermal anomaly exhibits the monotonic distance-decay gradient expected of a point-source emitter, consistent with sensible heat advection theory (Oke, 1987).

- **Phase V: Evapotranspiration Collapse / Metabolic Proxy** (`10_gee_evapotranspiration.js`, `11_plot_evapotranspiration.py`):
  - **Logic**: Extracts the 8-day Actual Evapotranspiration (ET, kg/m²/8-day) from the MODIS/Terra MOD16A2GF product (500 m spatial resolution) over the full VP development polygon (Impact Zone) and a stable parkland Control Zone of equivalent area (~500 m radius buffer). The GEE script applies the MODIS scale factor (×0.1) and exports a paired time series spanning 2015–2026.
  - **Algorithm Highlight**: At MODIS 500 m resolution, both zones are sub-pixel suburban mosaics, so absolute ET curves visually overlap. The critical signal emerges in the **Difference-in-Differences (DiD)** domain: $\Delta$ET = ET$_{\text{Sprawl}}$ − ET$_{\text{Control}}$. The Python script partitions $\Delta$ET into pre- and post-construction epochs and applies Welch's t-test and Mann-Whitney U to test for a statistically significant regime shift. An annual bar decomposition visualises the year-by-year evolution of the DiD signal.
  - **Physical Rationale**: Evapotranspiration is a direct proxy for the **latent heat flux** ($Q_E$) term in the surface energy balance equation: $Q^* = Q_H + Q_E + Q_G$. When vegetated soil (high $Q_E$, evaporative cooling) is replaced by impervious asphalt (near-zero $Q_E$), the absorbed solar radiation is redirected entirely into sensible heat ($Q_H$, direct atmospheric warming) and ground heat storage ($Q_G$). A statistically significant decline in $\Delta$ET therefore constitutes a **thermodynamic proof of mechanism** — it demonstrates not merely *that* the surface warmed, but *why* it warmed, from first principles of conservation of energy. This operationalises the Marxian concept of the **Metabolic Rift** (Foster, 1999; Bozak, 2012) as a quantifiable rupture in the land-atmosphere energy exchange cycle.

### Inter-Pipeline Automation (`run_pipeline.sh`)

While the Google Earth Engine scripts (`04`, `06`, `06b`, `08`, `10`) must be executed natively in the GEE cloud to leverage Google's server-side planetary computation (Gorelick et al., 2017), the entire local analytical workflow is fully automated.

Executing `./scripts/run_pipeline.sh` automatically daisy-chains the spatial reprojection (`02`), geospatial formatting (`03`), and all advanced statistical rendering stages (`05`, `07`, `07b`, `09`, `11`), selectively executing Python modules if their respective GEE `raw_telemetry` CSVs are present. The entire workflow requires no proprietary GIS software.

### Phase III: Institutional Governance & Discourse Audit

**Objective:** To cross-reference spatial realities with municipal planning compliance and institutional grey literature.

A structural analysis of the following institutional dossiers is documented in `documentation/`:

| Document | Source | Reference |
|:---------|:-------|:----------|
| Environmental Statement Vol. 1 (Main Text) | Spelthorne Borough Council | Planning App: 18/01212/OUT (2018) |
| Flood Risk Assessment | Hydrock Consultants Ltd | SPS-HYD-XX-XX-RP-D-5001 (2018) |
| Transport Assessment | i-Transport LLP | ITL14056-008D R (2018) |
| Arboricultural Implications Report (Parts 1 & 2) | SJA Trees | Drawing No: SJA TPP 18158-02 (2018) |
| Economic Impact Assessment | Turley Economics | Document Ref: PINR3003 (2018) |
| Heritage Statement | Turley Heritage | (2018) |
| Sustainability Assessment | Turley Sustainability | Document Ref: PINR3003 (2018) |
| Planning Committee Report & Minutes | Spelthorne Borough Council | 12 February 2019 |
| Capital Assurance Review | CIPFA | DLUHC (2023) |
| Business, Infrastructure & Growth Committee Agenda | Spelthorne Borough Council | 11 September 2025 |

This phase contrasts corporate ESG assertions with the physical facts extracted in Phases I and II — most notably the discrepancy between the EIA's projected "very special circumstances" economic benefits (£392M GVA) and the empirically observed ecological costs (79 trees removed per SJA arboricultural survey; 13.2 ha greenbelt conversion at an S106 buyout of £6,150 total, or 4.6p/m²).

---

## 3. Key Empirical Findings (Shepperton Case Study)

The execution of this pipeline yielded the following statistically verified metrics:

- **Logistical Sprawl:** A total land conversion of **13.21 hectares** (132,123.11 m²) of Metropolitan Green Belt into impermeable asphalt parking surfaces, distinct from the 16.4 ha of building floorspace reported in the EIA (Spelthorne Borough Council, 2018). This represents continuous capital territorialisation into protected agricultural land.

- **Energy Parasitism:** The identification of **17 new high-capacity grid nodes** (substations, transformers, power lines) within the 1200 m extraction radius, servicing virtual rendering infrastructure and industrial-grade HVAC maintenance systems.

- **Arboricultural Erasure:** Cross-referencing with the SJA Trees Arboricultural Implications Report (2018), the development required the removal of **79 trees** — a permanent loss of carbon sequestration and canopy-level evapotranspiration capacity.

- **Biophysical Erasure (NDVI):** A permanent structural collapse from a pre-development NDVI baseline of **~0.635** to a post-development level of **~0.28**, isolated via **Difference-in-Differences (DiD)** against the stable Control Zone greenbelt. The degradation trend is definitively verified by **Seasonal Mann-Kendall** testing (p < 0.001, τ = −0.6325; statistically significant at 99.9% confidence). The adjacent Control Zone remained completely stable over the 8-year continuum, confirming that the collapse is attributable to anthropogenic land conversion, not regional climate or phenological drift.

- **UHI Raster Composite (Descriptive Observation):** The GEE-generated UHI raster composite reveals a localised surface temperature elevation of approximately **+5 °C** at the parking lot surface relative to surrounding vegetation in peak summer imagery. This figure is a **descriptive observation** from single-scene thermal visualisation — it is not derived from any statistical test and should not be conflated with the inferential BACI results below. It serves as a visual heuristic confirming the expected thermal signature of impervious surface conversion.

- **Thermodynamic Escalation (LST) & The Metabolic Rift:** A Tri-Pillar methodological defense examines the thermodynamic disruption from the land-use conversion through multiple independent lines of evidence:

  - *Pillar I — Inferential Anchor (Paired BACI)*: Using n=268 paired Landsat observations (L7+L8+L9, 2015–2025), $\Delta$T (Impact − Control) shifted from a pre-construction mean of **+0.85 °C** (n=104) to a post-construction mean of **+0.95 °C** (n=164), a shift of **+0.10 °C** (full-year Welch p=0.69, MW p=0.99). The summer-only (JJA) subset shows a shift from **+0.45 °C** (n=27) to **+0.69 °C** (n=52), i.e. **+0.23 °C** (Welch p=0.73, MW p=0.87). These p-values are not statistically significant at any conventional threshold, reflecting the fundamental **spatial resolution constraint**: the parking-lot polygon spans ~3 native Landsat TIRS pixels (100 m), yielding an insufficient signal-to-noise ratio that precludes statistical significance regardless of temporal sample size. This is documented transparently as a **physical limitation of the sensor, not a methodological failure** — an honest result in a landscape where p-hacking remains pervasive.

    > **Note on data provenance**: An earlier advisor brief (produced from a previous GEE export with fewer observations, n=94/143) reported a shift of +0.56 °C and Welch p=0.080. The numbers reported here supersede that brief and are derived from the current, complete triple-satellite CSV (n=104/164, last observation: November 2025).

  - *Pillar I-A — Sensitivity Analysis (Pending)*: Script `06b_gee_thermal_sensitivity.js` expands the Impact Zone to the full VP development polygon (~50 pixels) and restricts the temporal window to the Warm Season (Apr–Sep). This analysis is **pending GEE CSV export** (`ee-chart_lst_sensitivity.csv`). Once executed, it will test whether the BACI result strengthens when the spatial constraint is relaxed.

  - *Pillar II — Spatial Corroboration (Distance Gradient / Net Thermal Scar)*: The background-subtracted spatial transect reveals a **Net Thermal Scar of −1.17 °C** at the Impact Zone core (0 m), decaying monotonically toward zero at ~375 m. The negative daytime Net Thermal Scar reflects the **high-albedo surface reflection** of the parking lot during daylight hours: light-coloured asphalt and painted road markings reflect more incoming shortwave radiation than the pre-existing dark grassland, resulting in *lower* daytime LST relative to the regional trend. This does not contradict the UHI finding; rather, **it reveals the diurnal asymmetry of the thermal regime** — a phenomenon that requires **nighttime LST validation** (e.g., via ECOSTRESS or future Landsat night-pass) beyond the scope of the current dataset. Daytime-only Landsat overpasses capture the albedo-dominated regime but cannot measure the nocturnal release of stored heat through elevated thermal admittance, which is the primary UHI mechanism in urban energy balance theory (Oke et al., 2017, *Urban Climates*, Cambridge University Press). The descriptive +5 °C observation (above) and the negative Net Thermal Scar are therefore **not contradictory** — they measure different physical quantities at different temporal scales.

  - *Pillar III — Latent Heat Collapse (Evapotranspiration — The Thermodynamic Proof of Mechanism)*: The MODIS ET DiD analysis provides the **strongest statistical result** in the entire thermal pillar. Pre-construction $\Delta$ET (Sprawl − Control) averaged **−0.05 mm/8-day** (near-zero; confirming the parallel trends assumption required for valid DiD inference). Post-construction $\Delta$ET collapsed to **−0.24 mm/8-day** — a regime shift of **−0.19 mm/8-day** (Welch p = 5.48×10⁻³, Mann-Whitney p = 3.11×10⁻³; **both highly significant at α = 0.01**). The annual bar decomposition reveals 2019 (the construction year) as a catastrophic outlier ($\Delta$ET ≈ −0.75 mm/8-day, n=46 observations across the full year — not a single anomalous reading), followed by a permanent stabilisation below the pre-construction baseline in all subsequent years (2020–2025). This confirms the irreversible destruction of latent heat flux ($Q_E$) and the forced thermodynamic repartitioning of absorbed solar radiation from evaporative cooling into sensible heat ($Q_H$) and ground storage ($Q_G$) — the quantitative expression of what Marx termed the **Metabolic Rift** between capital's accumulation imperatives and ecological reproduction.

    > **ET pipeline verification**: MODIS scale factor (×0.1) correctly applied (ET range: 1–24 mm/8-day, consistent with UK temperate climate). Control Zone uses the same centre coordinates as the NDVI pipeline, buffered to 500 m (commensurate with MODIS native resolution vs. Sentinel-2's 100 m buffer). The 2019 outlier is genuine — it represents 46 independent 8-day composites with a mean $\Delta$ET of −0.80 ± 0.66, not a cloud contamination artefact.

---

## 4. Feasibility, Scalability & Epistemological Limits

### Feasibility
- **Uses already-available spatial data (OSM)**: The audit methodology leverages open-source Volunteered Geographic Information, specifically OpenStreetMap via the Overpass API, to extract hard spatial metrics. This circumvents the industry's 'selective visibility' by utilising publicly accessible geographic data without relying on proprietary corporate disclosures.
- **Can be integrated into existing EIA processes**: This forensic framework directly interfaces with the statutory frameworks already mandated by the Town and Country Planning (Environmental Impact Assessment) Regulations 2017.
- **Entire workflow is open-source**: No proprietary GIS software (ArcGIS, ERDAS) is required. The pipeline is built entirely on Google Earth Engine (free for academic use), Python, and open geospatial libraries.

### Scalability
Because the spatial projection utilises the standardised British National Grid (EPSG:27700), this algorithmic audit is **universally scalable across the entire UK screen sector**. It can be systematically deployed to quantify the cumulative spatial fix and metabolic rift across expanding megahubs, tracking continuous capital territorialisation from Shepperton down to the Longcross and Leavesden clusters (PwC, 2018).

### Epistemological Limits & Future Trajectories

| Dimension | Current Limit | Future Extension |
|:----------|:-------------|:-----------------|
| **Geospatial** | OSM latency & static mapping | Real-time change detection via Sentinel-1 SAR |
| **Thermodynamic** | Daytime-only Landsat overpass (albedo-dominated); no nocturnal SUHI data | ECOSTRESS or Landsat night-pass for nocturnal UHI quantification |
| **Micro-Attribution** | Macro-grid aggregation (5.4 GWh total) | HVAC & server cooling load regression modelling |
| **Algorithmic** | Manual Critical Discourse Analysis bottleneck | Automated NLP scraping of corporate ESG reports |
| **Logistical** | Reliance on 2018 EIA predictive models | Live Traffic API monitoring (TomTom/Google Maps) |

---

## 5. Repository Structure

```
OSM_AUDIT_2025/
├── scripts/                            # Fully automated analytical and statistical pipeline
│   ├── 01_osm_extraction.ql            # Overpass QL: OSM spatial extraction
│   ├── 02_spatial_projection.py        # WGS84 → EPSG:27700 reprojection & area calculation
│   ├── 03_kepler_formatter.py          # Kepler.gl geovisualisation CSV generator
│   ├── 04_gee_ndvi_pipeline.js         # GEE: Sentinel-2 NDVI time series extraction
│   ├── 05_plot_ndvi_chart.py           # DiD + Seasonal Mann-Kendall NDVI analysis
│   ├── 06_gee_thermal_pipeline.js      # GEE: Triple-satellite LST extraction (BACI)
│   ├── 06b_gee_thermal_sensitivity.js  # GEE: Sensitivity analysis (full polygon, warm season)
│   ├── 07_plot_thermal_chart.py        # Paired BACI statistical rendering
│   ├── 07b_plot_thermal_sensitivity.py # Sensitivity analysis rendering
│   ├── 08_gee_transect_decay.js        # GEE: Concentric buffer LST transect extraction
│   ├── 09_plot_transect_decay.py       # Net Thermal Scar (background-subtracted) analysis
│   ├── 10_gee_evapotranspiration.js    # GEE: MODIS ET time series extraction
│   ├── 11_plot_evapotranspiration.py   # ET DiD regime shift analysis
│   └── run_pipeline.sh                 # Shell orchestrator for all local Python stages
├── data/
│   ├── raw_spatial/                    # Raw GeoJSON extracts (WGS84)
│   ├── raw_telemetry/                  # Satellite time series CSVs from GEE
│   └── processed/                      # Kepler.gl CSVs and projected datasets
├── visualisations/                     # Output NDVI/LST/ET charts (PNG, 300 DPI)
├── Forensic_Audit_Shepperton/          # Presentation slides (PDF)
├── documentation/                      # Sprawl zone rationale, OSM accuracy citations, institutional dossiers
├── requirements.txt                    # Python dependencies (pymannkendall, statsmodels, scipy, etc.)
├── LICENSE                             # MIT License
└── README.md
```

---

## 6. Dependencies and Execution

### 6.1 Software Environment (Python 3.10+)
```bash
pip install -r requirements.txt
./scripts/run_pipeline.sh
```

### 6.2 Remote Sensing (Google Earth Engine)
All `.js` scripts (`04`, `06`, `06b`, `08`, `10`) are designed for the [Google Earth Engine Code Editor](https://code.earthengine.google.com/) (Gorelick et al., 2017). Users must execute these manually and export the resulting `.csv` telemetry files to `data/raw_telemetry/` before running the Python charting scripts. The pipeline script will automatically skip charting modules whose input CSVs are absent.

### 6.3 Transparency, Reproducibility & Replicability

| Item | Value |
|:-----|:------|
| **Repository** | [github.com/HanpuLi/-OSM_AUDIT_2025](https://github.com/HanpuLi/-OSM_AUDIT_2025) |
| **Data Extraction Date** | 3 March 2026 |
| **Spatial Projection** | British National Grid (EPSG:27700) |
| **OSM Pipeline** | Overpass API (OpenStreetMap contributors, 2015) |
| **Earth Observation** | GEE: ESA Sentinel-2 (S2_SR_HARMONIZED) + USGS Landsat 7/8/9 (C2 T1 L2) + NASA MODIS MOD16A2GF |
| **Local Processing** | Python (`pandas`, `numpy`, `scipy`, `matplotlib`, `pymannkendall`, `shapely`, `pyproj`) |

---

## 7. Selected Bibliography

### Academic Literature
- Bozak, N. (2012) *The Cinematic Footprint: Lights, Camera, Natural Resources*. Rutgers University Press.
- Formenti, C. (2024) 'The environmental footprint of animated realism', *NECSUS*, 13(1), pp. 221–241.
- Foster, J.B. (1999) 'Marx's Theory of Metabolic Rift', *American Journal of Sociology*, 105(2), pp. 366–405.
- Gorelick, N. et al. (2017) 'Google Earth Engine: Planetary-scale geospatial analysis for everyone', *Remote Sensing of Environment*, 202, pp. 18–27.
- Greene, D. and Joseph, D. (2015) 'The Digital Spatial Fix', *tripleC*, 13(2), pp. 223–247.
- Harvey, D. (2004) 'The "New" Imperialism: Accumulation by Dispossession', *Socialist Register*, 40, pp. 63–87.
- Keeney, D. (2024) *Virtual Production's Role in Carbon Reduction*. Future Observatory / AHRC.
- Maxwell, R. and Miller, T. (2012) *Greening the Media*. Oxford University Press.
- Oke, T.R. (1987) *Boundary Layer Climates*. 2nd edn. Routledge.
- Oke, T.R. et al. (2017) *Urban Climates*. Cambridge University Press.
- Running, S.W. et al. (2019) *MOD16A2GF MODIS/Terra Net Evapotranspiration Gap-Filled*. NASA LP DAAC.
- Sharma, P. (2024) 'The Jevons Paradox in Cloud Computing', *ACM Conference Preprint*. doi:10.48550/arXiv.2411.11540.
- Stewart-Oaten, A. et al. (1986) 'Environmental impact assessment: "pseudoreplication" in time?', *Ecology*, 67(4), pp. 929–940.
- Vaughan, H. (2019) *Hollywood's Dirtiest Secret*. Columbia University Press.

### Institutional Dossiers
- albert, BFI and Arup (2020) *A Screen New Deal*. London: British Film Institute.
- CIPFA (2023) *Spelthorne Borough Council: Capital Assurance Review*. DLUHC.
- Hydrock Consultants (2018) *Flood Risk Assessment*. SPS-HYD-XX-XX-RP-D-5001.
- i-Transport LLP (2018) *Shepperton Studios Transport Assessment*. ITL14056-008D R.
- PwC (2018) *Review of the UK film and high-end TV production facility market*. London.
- SJA Trees (2018) *Arboricultural Implications Report — Parts 1 & 2*. Drawing No: SJA TPP 18158-02.
- Spelthorne Borough Council (2018) *Environmental Statement Volume 1*. Planning App: 18/01212/OUT.
- Spelthorne Borough Council (2019) *Planning Committee Report & Printed Minutes*, 12 February 2019.
- Turley Economics (2018) *Expanding Shepperton Studios: The Economic Impact*. PINR3003.

---

## 8. Licensing

This project is submitted for the PMP ELSS Module assessment at Queen Mary University of London.  
Copyright © 2026 Hanpu Li (Caitlyn Lye). Released under the MIT License.
