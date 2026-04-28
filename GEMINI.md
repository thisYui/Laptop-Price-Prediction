# Laptop Price Prediction Project

This project is a data engineering and machine learning pipeline designed to predict laptop prices. It currently focuses on automated data collection (scraping) from `websosanh.vn` and rigorous data cleaning to prepare a dataset for predictive modeling.

## Project Architecture

- **`config/`**: Contains YAML configuration files (e.g., `websosanh_collection.yml`) for scraping parameters like page ranges, API endpoints, and request headers.
- **`data/raw/`**: Stores the output of the pipelines.
    - `laptop_features.csv`: Raw data collected from the source.
    - `clean_laptop_features.csv`: Processed and structured data ready for analysis.
- **`pipeline/`**: Orchestration logic for the project's workflows.
    - `collection_data_pipeline.py`: Manages the multi-step scraping process (URL extraction -> Data extraction).
    - `clean_data_pipeline.py`: Coordinates various cleaning functions into a single transformation flow.
- **`scripts/`**: CLI entry points for developers to execute pipelines.
- **`src/data/`**: Low-level utility modules for web scraping (`collect.py`) and data transformation (`data_cleaning.py`).

## Getting Started

### Prerequisites
- Python 3.8+
- Recommended: Virtual environment (`venv`)

### Installation
```bash
pip install -r requirements.txt
```

### Running the Pipelines

#### 1. Data Collection
Scrape laptop data from the web using the collection script:
```bash
# Run the full pipeline (links + data)
python scripts/collection_data_run.py

# Run only the link extraction step
python scripts/collection_data_run.py --step links

# Run with custom page range
python scripts/collection_data_run.py --start-page 1 --end-page 5
```

#### 2. Data Cleaning
Transform the raw CSV into a cleaned format:
```bash
python scripts/data_cleaning.py
```

## Development Conventions

- **Modular Logic**: Keep scraping and cleaning utilities in `src/data/`. These should be pure functions or well-defined helpers.
- **Orchestration**: Use the `pipeline/` directory to define high-level workflows that use the source utilities.
- **Configuration**: Avoid hardcoding parameters (URLs, selectors, limits). Use the `config/*.yml` files.
- **Data Integrity**: Always validate the shape and null-counts of data after cleaning steps.
- **Encoding**: Use `utf-8` for all file operations to support Vietnamese characters.

## TODO / Roadmap
- [ ] Implement exploratory data analysis (EDA) notebooks.
- [ ] Develop the price prediction model (e.g., Random Forest, XGBoost).
- [ ] Add unit tests for cleaning functions in `src/data/data_cleaning.py`.
