# Cairo Real Estate Intelligence Platform

> 🏗️ **Status:** In Development | **Last Updated:** April 2026

An end-to-end data science application that brings transparency to Cairo's residential real estate market through web scraping, exploratory analysis, interactive visualizations, Overprice detector and machine learning-powered property valuation.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](YOUR_DEPLOYMENT_URL_HERE)
![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [Model Performance](#model-performance)
- [Key Insights](#key-insights)
- [Tech Stack](#tech-stack)
- [Development Roadmap](#development-roadmap)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

The Cairo Real Estate Intelligence Platform addresses the opacity and inconsistency in Egypt's residential property market. This platform provides:

- **Market transparency** through district-level price benchmarking
- **Valuation support** via explainable ML predictions with confidence intervals, Over-price calculator
- **Interactive exploration** of 70k+ Cairo property listings
- **Data-driven insights** into pricing patterns and market dynamics

**This is a portfolio project demonstrating end-to-end data science capabilities from data collection to deployment.**

### Problem Statement

Cairo's real estate market suffers from:
- Inconsistent pricing with similar properties varying wildly
- Information asymmetry where buyers lack objective valuation tools
- Mixed Arabic/English data with inconsistent spelling and formatting
- No centralized platform for market analysis

### Solution

A data-driven platform that collects real-world listings, normalizes messy Arabic text, analyzes structural pricing patterns, and provides explainable ML-powered valuations through an interactive dashboard.

---

## ✨ Key Features

### 📊 Market Explorer
Interactive district comparison with filterable property listings, price per square meter analysis, and distribution visualizations highlighting market structure.

### 🗺️ District Deep Dive
Neighborhood-level statistics, sample listings with contextual pricing benchmarks, and finishing quality breakdowns by district.

### 💰 ML-Powered Price Estimator
Fair market value predictions with confidence intervals, SHAP-based explanations showing feature contributions, and comparable properties for transparent reasoning.

### 📈 Market Insights Dashboard
Key findings from exploratory analysis, identification of overpriced/undervalued segments, and pricing anomaly detection.

### ℹ️ Methodology & Documentation
Complete transparency on data sources, model architecture, validation approach, and known limitations.

---

## 🎬 Demo

### Screenshots

**Market Explorer**
![Market Explorer](docs/images/market_explorer.png)
*Interactive district comparison with real-time filtering*

**Price Estimator**
![Price Estimator](docs/images/price_estimator.png)
*ML predictions with SHAP explainability and confidence intervals*

**Market Insights**
![Market Insights](docs/images/market_insights.png)
*Data-driven findings about Cairo's real estate market*

### Live Demo
**[Try the app live →](YOUR_DEPLOYMENT_URL_HERE)**

### Demo Video
**[Watch 3-minute walkthrough →](YOUR_YOUTUBE_URL_HERE)**

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Quick Start

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/cairo-realestate.git
cd cairo-realestate
```

**2. Install dependencies**
```bash
# Using uv (recommended)
uv sync
```

**3. Run the application**
```bash
# Using uv
uv run streamlit run app/app.py

# Or if environment is activated
streamlit run app/app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📖 Usage

### Running the Streamlit App
Start the interactive dashboard to explore Cairo's real estate market, compare districts, and get property valuations.

### Data Collection
Run the scraping pipeline to collect fresh listings from configured platforms. Includes rate limiting and respectful scraping practices.

### Model Training
Train the machine learning model on collected data with cross-validation and hyperparameter tuning.

### Jupyter Notebooks
Explore the analysis process through documented notebooks covering scraping, cleaning, EDA, and modeling.

For detailed usage instructions, see the [User Guide](docs/USER_GUIDE.md).

---

## Project Structure

```
cairo-realestate/
├── app/                      # Streamlit application
│   ├── pages/               # Multi-page app structure
│   ├── components/          # Reusable UI components
│   └── app.py              # Main entry point
├── data/                    # Data storage (gitignored)
│   ├── raw/                # Raw scraped data
│   ├── processed/          # Cleaned datasets
│   ├── models/             # Trained model artifacts
│   └── external/           # Reference data
├── notebooks/               # Jupyter notebooks
│   ├── 01_scraping.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_eda.ipynb
│   └── 04_modeling.ipynb
├── src/                     # Source code modules
│   ├── scraper/            # Web scraping
│   ├── preprocessing/      # Data cleaning
│   ├── models/             # ML models
│   └── utils/              # Utilities
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
└── README.md              # This file
```

---

## 🔄 Data Pipeline

### Pipeline Overview

1. **Data Collection** - Web scraping from Cairo real estate platforms
2. **Parsing** - Convert raw HTML/JSON to structured format
3. **Cleaning** - Arabic text normalization, missing value handling, data validation
4. **Feature Engineering** - Create derived features for modeling
5. **Model Training** - Train and validate ML models
6. **Deployment** - Serve predictions through Streamlit app

### Data Sources
- **Data is collected from publicly accessible real estate listing websites. All data scraped is publicly visible without authentication.**
- **Collection Period:** [Start date] to [End date]
- **Total Listings:** 70k+ properties across 40 districts
- **Geographic Coverage:** Cairo metropolitan area

### Data Quality
- **Collection Success Rate:** 99.97%
- **Data Retention After Cleaning:** [X]%
- **Districts Covered:** 40 Districts 
- **Duplicate Rate:** [X]%

For detailed pipeline documentation, see [METHODOLOGY.md](docs/METHODOLOGY.md).

---

## 📊 Model Performance

### Metrics (Test Set)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **R² Score** | [0.XX] | Model explains XX% of price variance |
| **RMSE** | [XXX,XXX EGP] | Average prediction error |
| **MAE** | [XXX,XXX EGP] | Typical absolute error |
| **MAPE** | [XX%] | Percentage error |

### Model Details
- **Algorithm:** [XGBoost / Random Forest]
- **Training Set:** [X] listings (80% of data)
- **Features:** Area, District, Bedrooms, Bathrooms, Finishing, Amenities
- **Validation:** 5-fold cross-validation + held-out test set
- **Explainability:** SHAP values for feature importance

### Performance by District
Model performance varies by district due to sample size and market dynamics. See [METHODOLOGY.md](docs/METHODOLOGY.md) for detailed breakdown.

---

## 🔍 Key Insights

### Top Market Findings

**1. District Price Hierarchy**
- [District X] commands highest prices at [XX] EGP/sqm
- [District Y] offers best value with [XX] EGP/sqm
- Premium districts show [X]% price premium over Cairo average

**2. Finishing Quality Impact**
- Luxury finishing adds approximately [X]% to property value
- Semi-finished properties trade at [X]% discount
- Finishing quality matters more in affluent districts

**3. Pricing Anomalies**
- [X]% of listings are overpriced by more than 25% vs district median
- [Y]% are potentially undervalued, representing opportunities
- Outliers are concentrated in [specific property types/areas]

**4. Size vs Value Relationship**
- Price per sqm decreases for properties larger than [X] sqm
- Optimal value range: [XX-XX] sqm in most districts
- Smaller units command premium per sqm

**5. [Additional insight based on your analysis]**

For comprehensive market analysis, see [INSIGHTS.md](docs/INSIGHTS.md).

---

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.9+** - Primary programming language
- **Streamlit** - Interactive web application framework
- **Plotly** - Dynamic visualizations
- **Pandas & NumPy** - Data manipulation

### Machine Learning
- **Scikit-learn** - ML pipeline and preprocessing
- **XGBoost / Random Forest** - Prediction models
- **SHAP** - Model explainability

### Data Collection
- **BeautifulSoup / Selinium** - Web scraping


### Development Tools
- **uv** - Fast Python package management
- **Jupyter** - Interactive analysis
- **Git/GitHub** - Version control

---

## 🗺️ Development Roadmap

### ✅ Version 1.0 (Current)
- [x] Data collection from Cairo real estate platforms
- [x] Exploratory market analysis
- [x] ML-powered price estimation with confidence intervals
- [x] ML-power over-price deteticion and analysis
- [x] Interactive Streamlit dashboard
- [x] SHAP-based model explainability
- [x] Deployment on Streamlit Cloud

### 🚀 Version 2.0 (Future)
- [ ] **Market Chatbot** - AI assistant for real estate questions using RAG
- [ ] **Time Series Forecasting** - Predict district-level price trends
- [ ] **Geospatial Analysis** - Distance to amenities and transport


For detailed NLP enhancement plans, see [NLP_ROADMAP.md](docs/NLP_ROADMAP.md).

---

## ⚠️ Limitations

### Data Limitations
- **Temporal:** Data collected during [time period] may not reflect current market conditions
- **Coverage:** Limited to listings on public platforms, excludes private deals
- **Self-reported:** Assumes listing information is accurate (not independently verified)
- **Survivorship Bias:** The majority of the data is active listings

### Model Limitations
- **Generalization:** Trained on Cairo only, not applicable to other cities
- **Feature Gaps:** Cannot capture view quality, exact location nuances, or building condition
- **Static Model:** Does not predict future price movements or market trends
- **Outlier Performance:** May perform poorly on luxury or highly unique properties

### Technical Limitations
- **Scalability:** Current implementation optimized for ~70K listings
- **Real-time Data:** Manual scraping required for updates (no live API integration)
- **Language:** Interface primarily in English (Arabic support planned)

**Important Disclaimer:** This tool provides informational estimates only, not financial advice. Always consult licensed real estate professionals and conduct physical property inspections before making decisions.

---

## Contributing

Contributions are welcome! This is a portfolio project, but suggestions and improvements are appreciated.

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution
- Additional data sources or scraping improvements
- Arabic NLP enhancements
- New visualization ideas
- Model performance improvements
- Documentation and translation
- Bug fixes and optimizations

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Data Usage
Property listing data was collected from public sources for educational and non-commercial purposes only. This project respects website terms of service and implements rate-limiting to avoid server strain. Data is not redistributed.

---

## 📧 Contact

**Your Name**
- **GitHub:** [@MarwanAshrafMakhlouf](https://github.com/MarwanAshrafMakhlouf)
- **LinkedIn:** [Linkedin Profile](https://www.linkedin.com/in/marwan-ashraf-9846a1202/)
- **Email:** marwanashrafmakhlouf@gmail.com
- **Portfolio:** [mywebsite.com](https://yourwebsite.com)

### Project Links
- **Live Demo:** [App URL](YOUR_APP_URL)
- **Blog Post:** [Medium Article](YOUR_BLOG_URL)
- **Demo Video:** [YouTube](YOUR_VIDEO_URL)

---

##  Acknowledgments
- Inspiration: [Projects or papers that influenced this work]
- Tools: Streamlit, Plotly, SHAP, and the open-source community
- Special thanks: [Mentors, colleagues, or resources]

---

## Additional Documentation

- **[METHODOLOGY.md](docs/METHODOLOGY.md)** - Detailed technical approach and decisions
- **[INSIGHTS.md](docs/INSIGHTS.md)** - Comprehensive market findings and analysis
- **[NLP_ROADMAP.md](docs/NLP_ROADMAP.md)** - Future NLP enhancement plans
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Complete usage instructions
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates

---

##  Learning Outcomes

This project demonstrates:
- **Data Engineering** - Web scraping, ETL pipelines, Arabic text normalization
- **Data Science** - EDA, feature engineering, ML modeling, validation
- **ML Ops** - Model deployment, serving predictions, explainability implementation
- **Data Visualization** - Interactive dashboards, storytelling with data
- **Software Engineering** - Code organization, testing, documentation
- **Domain Expertise** - Real estate market analysis, pricing dynamics

---

**⭐ If you find this project useful or interesting, please consider starring it on GitHub!**



---

*Last updated: April 2026*