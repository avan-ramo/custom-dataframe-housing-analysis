# Custom DataFrame Housing Analysis

## Overview

This project is a custom-built data processing and housing analysis application developed in Python using Streamlit. The primary goal of the project was to recreate core functionality commonly found in libraries such as Pandas while applying the implementation to real-world Orange County housing and economic datasets.

The project includes a fully custom DataFrame library built from scratch, supporting SQL-like operations such as filtering, grouping, aggregation, projection, and joins without relying on Pandas or NumPy for the underlying data manipulation.

The application provides an interactive interface for exploring housing trends, demographic data, and regional economic indicators across Orange County zip codes.

---

## Features

### Custom CSV Parser
- Built a custom CSV parser with automatic type conversion
- Supports:
  - integers
  - floats
  - booleans
  - strings
  - null values
- Efficiently handles datasets with over 20,000 rows

### Custom DataFrame Library
Implemented a custom DataFrame class with:
- Column-oriented storage
- Efficient column access
- Projection operations
- Validation and error handling

### SQL-Like Data Operations
The custom library supports:

#### Filtering
- Lambda-based row filtering
- Complex conditional filtering

#### Projection
- Select and display specific columns

#### GroupBy & Aggregation
- Group rows by categorical variables
- Aggregate numeric values using:
  - mean
  - sum
  - min
  - max
  - count

#### Join Operations
- Optimized hash-based inner joins
- Support for joining on different column names using:
  - `left_on`
  - `right_on`

---

## Technical Implementation

### Column-Oriented Storage
Data is stored internally using dictionaries of lists for efficient access and manipulation.

### Hash-Based Join Optimization
Implemented joins using a hash map approach with:
- O(n + m) complexity
- significantly faster performance than naive O(n × m) joins

### Interactive Streamlit Interface
The application includes:
- interactive filtering
- aggregation controls
- multi-dataset exploration
- expandable “Under the Hood” sections showing implementation details and executed code

---

## Datasets

### Zillow Housing Data
Primary housing dataset containing:
- 20,777 rows
- 33 columns
- median home values by zip code
- time series data from 2014–2023

### FHFA House Price Index (HPI)
Dataset containing:
- housing appreciation indices
- relative price changes over time
- zip-code level comparisons

### Median Income Data
Dataset containing:
- household income by zip code
- demographic and economic indicators
- socioeconomic comparisons across Orange County

---

## Technologies Used
- Python
- Streamlit
- Custom DataFrame Library
- CSV Parsing
- Object-Oriented Programming

---

## Project Structure

```text
custom-dataframe-housing-analysis/
├── app.py
├── csv_parser.py
├── About.txt
├── README.md
├── Coordinates.csv
├── Distance_to_Attractions.csv
├── FHFA_HPI_by_Zip.csv
├── Medium_Income.csv
├── OC_Transposed_Zillow.csv
├── Zillow_Housing_Price_Index.csv
├── real_data_test.py
├── test_parser.py
└── .gitignore
```

---

## Installation

Install required dependencies:

```bash
pip install streamlit
```

If needed:

```bash
python -m pip install streamlit
```

---

## Running the Application

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will open locally at:

```text
http://localhost:8501
```

---

## Key Learning Outcomes
This project strengthened understanding of:
- DataFrame internals
- efficient data storage strategies
- hash map optimization
- join algorithms
- custom parsing logic
- object-oriented Python design
- interactive data application development

---

## Future Improvements
Potential future improvements include:
- additional join types (left/right/full outer joins)
- sorting operations
- indexing optimization
- larger-scale dataset support
- visualization enhancements
- SQL query interface integration

---

## Author
Omar Nava  
Master’s Student in Applied Data Science  
University of Southern California