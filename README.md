# Project Overview: Spatial BI - Restaurant Void Analysis Platform (SaaS MVP)

![Spatial BI Demo](reversed_output.gif)
## 1. Project Goal
This project is a B2B Big Data monetization platform designed for cloud kitchen operators and commercial real estate developers. It performs "Void Analysis" by ingesting Yelp business data and Zillow rent data, applying spatial gridding (Uber H3), and calculating a "Void Score" (Supply vs. Cost) to identify highly profitable, under-served neighborhoods.

**MVP / POC Note:** To optimize data processing for this Proof of Concept, the system utilizes the Yelp Open Dataset, which focuses on specific metropolitan areas (e.g., Philadelphia, New Orleans). The PySpark pipeline architecture is designed to be fully scalable to a national level once commercial data licenses are acquired.

## 2. Tech Stack
* **Data Processing Pipeline:** Python, PySpark
* **Geospatial Library:** `h3-py` (Uber H3)
* **3D Map Visualization:** `pydeck` (Deck.gl) / `keplergl`
* **Frontend SaaS Web App:** `Streamlit` (with `plotly` for charts)

---

## 3. Backend Pipeline Architecture (Phase 1 ~ 4)
*(Agent Note: Ensure the core data engineering pipeline output is clean and structured for the frontend.)*

* **Phase 1 (Ingestion):** Download Zillow ZORI CSV and extract `yelp_academic_dataset_business.json`.
* **Phase 2 (Processing):** Use PySpark to clean data and map all coordinates to H3 hex bins (resolution=8).
* **Phase 3 (Aggregation):** Group by H3 index and cuisine type. Calculate `Competitor_Count`, `Avg_Rent`, and final `Void_Score`. Export to `data/processed/h3_void_scores.csv`.
* **Phase 4 (Map Generation):** Generate a 3D hexagonal map HTML file where height = Rent, and color = Void Score.

---

## 4. Frontend SaaS Application (Phase 5 - NEW)
Please build a multi-page Streamlit application (using a `pages/` directory structure or sidebar navigation) to serve as the customer-facing SaaS platform. The app must read the processed data from `data/processed/h3_void_scores.csv`.

### Task 5.1: Landing Page (Home)
* **Goal:** Hook the customer and explain the value proposition.
* **Content:** * A catchy headline (e.g., "Stop Burning Money on the Wrong Location").
  * A brief summary of how we help cloud kitchens and developers find "Blue Ocean" neighborhoods.
  * Embed a static preview or GIF of the 3D Void Map to show the product's capability.

### Task 5.2: Executive Dashboard (Interactive Data Insights)
* **Goal:** Provide high-level, actionable insights for decision-makers.
* **Visualizations to build (using Plotly/Streamlit native charts):**
  * **Saturated Market Alert:** A Bar or Pie chart showing the "Top 10 Most Saturated Cuisines" (e.g., Pizza, Sandwiches).
  * **Opportunity Matrix (Scatter Plot):** X-axis = `Rent Cost`, Y-axis = `Competitor Count`. Highlight the "Sweet Spot" (Bottom-Left quadrant: Low Rent + Low Competition).
  * **Top 5 Investment Zones:** A clean data dataframe/table displaying the top 5 areas sorted descending by `Void_Score`.

### Task 5.3: Methodology & Trust (Building Credibility)
* **Goal:** Overcome customer skepticism about data accuracy.
* **Content:** Write a professional explanation of the Void Score formula. Explicitly mention the use of **Uber H3 Spatial Indexing**, **Yelp Data**, and **Zillow Rent Indexes**. Explain how the platform ensures privacy and data robustness.

### Task 5.4: Pricing & Subscription Tiers
* **Goal:** Demonstrate the Data Monetization strategy.
* **Content:** Display three subscription tiers using a card-like layout (using Streamlit columns):
  * **Starter (Free):** 2D Map preview for a single test city.
  * **Pro ($199/month):** Full 3D Map access, Void Score evaluation, and CSV export for Top 50 zones.
  * **Enterprise (Custom Pricing):** API access for internal real estate system integration and live data streams.

---

## 5. Coding Guidelines for Agent
* **Theme:** Build the Streamlit app with a modern, clean B2B SaaS theme (e.g., Dark Mode or minimal corporate style).
* **Performance:** You MUST use `@st.cache_data` when loading the `h3_void_scores.csv` file to ensure the dashboard filters and charts render instantly without reloading the CSV.
* **Integration:** Ensure the 3D map from Phase 4 is smoothly embedded into the Streamlit interface using `st.components.v1.html` or native `st.pydeck_chart`.