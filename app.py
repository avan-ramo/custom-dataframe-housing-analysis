import streamlit as st
from csv_parser import DataFrame

###############################################################################
# Set up the page - wide layout looks better for data tables
###############################################################################
st.set_page_config(
    page_title="Orange County Housing Data Explorer",
    layout="wide"
)

###############################################################################
# Main title and description
###############################################################################
st.title("Orange County Housing Data Explorer")

###############################################################################
# DATA LOADING - Using caching so files only load once
###############################################################################
st.sidebar.header("Data Loading")

# Cache these functions so Streamlit doesn't reload data on every interaction
@st.cache_data
def load_zillow():
    # Main housing dataset - 20k+ rows of Orange County home prices
    return DataFrame.read_csv("OC_Transposed_Zillow.csv")

@st.cache_data
def load_hpi():
    # House Price Index from FHFA - tracks price changes over time
    return DataFrame.read_csv("FHFA_HPI_by_Zip.csv")

@st.cache_data
def load_income():
    # Median household income by zipcode and year
    return DataFrame.read_csv("Medium_Income.csv")


###############################################################################
# Load all datasets - keep going even if some files are missing
###############################################################################
with st.spinner("Loading datasets..."):
    # Zillow is the main dataset, always load it
    df = load_zillow()
    
    # Store all successfully loaded datasets in a dictionary
    datasets_available = {"Zillow (Main)": df}
    
    # Try to load HPI data - it's optional for join demos
    try:
        hpi = load_hpi()
        datasets_available["HPI"] = hpi
    except Exception:
        hpi = None
        st.sidebar.error("FHFA_HPI_by_Zip.csv not found. Join operations with HPI will be unavailable.")
    
    # Try to load Income data - also optional for join demos
    try:
        income = load_income()
        datasets_available["Income"] = income
    except Exception:
        income = None
        st.sidebar.error("Medium_Income.csv not found. Income joins will be unavailable.")

st.sidebar.success(f"Loaded {len(datasets_available)} dataset(s)")

###############################################################################
# Show details about each dataset in the sidebar
###############################################################################
with st.sidebar.expander("Dataset Details", expanded=False):
    for name, dataset in datasets_available.items():
        if dataset is not None:
            st.write(f"**{name}**")
            st.write(f"- {dataset.shape[0]:,} rows x {dataset.shape[1]} columns")
            # Show first 3 column names as a preview
            st.write(f"- Columns: {', '.join(dataset.columns[:3])} ...")
            st.divider()

###############################################################################
# Let user pick which dataset to explore
###############################################################################
st.sidebar.subheader("Dataset Explorer")
selected_dataset = st.sidebar.selectbox(
    "Choose dataset to explore:",
    options=list(datasets_available.keys()),
    index=0
)

# Store the currently selected dataset for easy access
current_df = datasets_available[selected_dataset]
st.sidebar.info(f"Currently viewing: {selected_dataset}")

###############################################################################
# Create tabs for different operations
###############################################################################
tab1, tab2, tab3, tab4 = st.tabs([
    "Data Overview",
    "Filter Data",
    "Filter and Aggregate",
    "Join Data"
])

###############################################################################
# TAB 1: DATA OVERVIEW
# Shows basic info, column names, and sample data with pagination
###############################################################################
with tab1:
    st.header(f"Data Overview - {selected_dataset}")
    st.markdown("View basic information, column names, and sample data.")
    
    display_df = current_df
    
    # Show code example of how to access DataFrame properties
    with st.expander("Under the Hood: DataFrame Properties", expanded=False):
        st.code("""
# Getting DataFrame dimensions
rows, cols = df.shape

# Accessing columns
columns = df.columns
""", language="python")
        
        st.info("SQL Equivalent: DESCRIBE table or SELECT * FROM table LIMIT 10")
    
    # Display basic metrics about the dataset
    st.subheader("Dataset Information")
    colA, colB = st.columns(2)
    with colA:
        st.metric("Total Rows", f"{display_df.shape[0]:,}")
    with colB:
        st.metric("Total Columns", display_df.shape[1])
    
    # Show all column names
    st.subheader("Column Names")
    with st.expander("Code: Getting Columns", expanded=False):
        st.code("""
# Getting column names
columns = df.columns
""", language="python")
    
    # Display columns in a nice format (3 per row)
    cols_per_row = 3
    for i in range(0, len(display_df.columns), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(display_df.columns[i:i+cols_per_row]):
            with cols[j]:
                st.write(f"{i+j+1}. {col}")
    
    # Sample data section with projection (column selection)
    st.subheader("Sample Data")
    
    with st.expander("Under the Hood: Column Projection", expanded=False):
        st.code("""
# Selecting specific columns (projection)
projected_df = df[["City", "Year", "Price Index"]]
""", language="python")
        
        st.info("SQL Equivalent: SELECT City, Year, Price_Index FROM data")
    
    # Let user select which columns to view
    st.write("Select columns to display:")
    selected_cols = st.multiselect(
        "Choose columns",
        options=display_df.columns,
        default=display_df.columns[:5],  # Show first 5 columns by default
        key="proj_cols"
    )
    
    if not selected_cols:
        st.warning("Please select at least one column to display.")
    else:
        # Create projected DataFrame with only selected columns
        projected_df = display_df[selected_cols]
        
        ###################################################################
        # PAGINATION - Show data 50 rows at a time
        ###################################################################
        ROWS_PER_PAGE = 50
        total_rows = projected_df.shape[0]
        total_pages = (total_rows + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE
        
        # Use session state to remember current page
        # Each dataset gets its own page tracker
        page_key = f"current_page_{selected_dataset}"
        if page_key not in st.session_state:
            st.session_state[page_key] = 1
        
        # Reset to page 1 if user changes column selection
        cols_key = f"last_selected_cols_{selected_dataset}"
        if cols_key not in st.session_state:
            st.session_state[cols_key] = selected_cols
        elif st.session_state[cols_key] != selected_cols:
            st.session_state[page_key] = 1
            st.session_state[cols_key] = selected_cols
        
        st.write(f"Total: {projected_df.shape[0]:,} rows x {len(selected_cols)} columns")
        
        # Pagination controls
        colA, colB = st.columns([2, 1])
        
        with colA:
            # Show current page number
            st.markdown(
                f"<div style='text-align:center; padding:12px; font-size:18px; font-weight:bold;'>"
                f"Page {st.session_state[page_key]} of {total_pages:,}</div>",
                unsafe_allow_html=True
            )
        
        with colB:
            # Let user jump to a specific page
            page_input = st.number_input(
                "Jump to page:",
                min_value=1,
                max_value=total_pages,
                value=st.session_state[page_key],
                key=f"page_jump_{selected_dataset}"
            )
            # Always sync the page number
            st.session_state[page_key] = page_input
        
        # Calculate which rows to show on current page
        start_idx = (st.session_state[page_key] - 1) * ROWS_PER_PAGE
        end_idx = min(start_idx + ROWS_PER_PAGE, total_rows)
        
        st.caption(f"Showing rows {start_idx + 1:,} to {end_idx:,} of {total_rows:,}")
        
        # Display the data for current page
        display_data = {}
        for col in selected_cols:
            display_data[col] = projected_df[col][start_idx:end_idx]
        st.dataframe(display_data, use_container_width=True)

###############################################################################
# TAB 2: FILTER DATA
# Apply filters to narrow down the data (like WHERE clause in SQL)
###############################################################################
with tab2:
    st.header(f"Filter Data - {selected_dataset}")
    st.markdown("Apply filters based on available columns.")
    filter_df = current_df
    
    # Show code example of filtering
    with st.expander("Under the Hood: Filter Operation", expanded=False):
        st.code("""
# Filtering with lambda functions
filtered_df = df.filter(lambda row: row['Year'] >= 2020)

# Multiple conditions
filtered_df = df.filter(
    lambda row: row['Year'] >= 2020 and row['City'] == 'Irvine'
)
""", language="python")
        
        st.info("SQL Equivalent: SELECT * FROM data WHERE conditions...")
    
    # Detect what types of columns we have for filtering
    has_city = "City" in filter_df.columns
    has_year = "Year" in filter_df.columns
    has_zipcode = any(c in filter_df.columns for c in ["Zipcode", "ZipCode", "Five-Digit ZIP Code"])
    
    # Find numeric columns - check first 100 rows
    numeric_cols = []
    for col in filter_df.columns:
        sample_vals = [v for v in filter_df[col][:100] if v is not None]
        if sample_vals and all(isinstance(v, (int, float)) for v in sample_vals):
            numeric_cols.append(col)
    
    # Exclude Year and Zipcode from generic numeric filters
    # (they get their own special filter sections)
    numeric_cols = [c for c in numeric_cols if c not in ["Year", "Zipcode", "ZipCode", "Five-Digit ZIP Code"]]
    
    # Find categorical columns - things with less than 50 unique values
    categorical_cols = []
    for col in filter_df.columns:
        unique_vals = set(filter_df[col])
        if len(unique_vals) < 50 and col not in numeric_cols:
            categorical_cols.append(col)
    
    st.subheader("Available Filters")
    filters_applied = []  # Track which filters user has applied
    
    # CITY FILTER
    if has_city:
        with st.expander("Filter by City", expanded=False):
            all_cities = sorted(set(filter_df["City"]))
            selected_cities = st.multiselect("Select Cities", options=all_cities, default=[], key="city_filter")
            if selected_cities:
                filters_applied.append(("City", selected_cities))
    
    # YEAR FILTER - Use a range slider
    if has_year:
        with st.expander("Filter by Year", expanded=False):
            years = [y for y in filter_df["Year"] if y is not None]
            if years:
                min_year, max_year = int(min(years)), int(max(years))
                year_range = st.slider("Year Range", min_year, max_year, (min_year, max_year), key="year_filter")
                # Only add filter if user changed from default range
                if year_range != (min_year, max_year):
                    filters_applied.append(("Year", year_range))
    
    # ZIPCODE FILTER
    zipcode_col = None
    if has_zipcode:
        # Find which zipcode column name this dataset uses
        for c in ["Zipcode", "ZipCode", "Five-Digit ZIP Code"]:
            if c in filter_df.columns:
                zipcode_col = c
                break
        
        with st.expander("Filter by Zipcode", expanded=False):
            unique_zips = sorted(set(z for z in filter_df[zipcode_col] if z is not None))
            if len(unique_zips) <= 100:
                # If not too many zipcodes, show multiselect
                selected_zips = st.multiselect(f"Select {zipcode_col} values", unique_zips, default=[], key="zip_filter")
                if selected_zips:
                    filters_applied.append((zipcode_col, selected_zips))
            else:
                # Too many to show in dropdown
                st.info(f"Too many unique zipcodes ({len(unique_zips)}). Use numeric filters instead.")
    
    # OTHER NUMERIC COLUMNS - Price Index, HPI, etc.
    if numeric_cols:
        with st.expander("Filter by Other Numeric Columns", expanded=False):
            st.caption("Year and Zipcode have dedicated filters above")
            selected_numeric_col = st.selectbox("Choose numeric column", ["None"] + numeric_cols, key="numeric_col_select")
            if selected_numeric_col != "None":
                values = [v for v in filter_df[selected_numeric_col] if v is not None]
                unique_values = sorted(set(values))
                
                # Smart filter type based on number of unique values
                if len(unique_values) <= 20:
                    # Few unique values - use multiselect (like Month: 1-12)
                    st.info(f"{len(unique_values)} unique values - select specific values")
                    selected_values = st.multiselect(
                        f"Select {selected_numeric_col} values",
                        unique_values,
                        default=[],
                        key="numeric_multiselect"
                    )
                    if selected_values:
                        filters_applied.append((selected_numeric_col, selected_values))
                else:
                    # Many unique values - use range filter
                    st.info(f"{len(unique_values)} unique values - filter by range")
                    min_val, max_val = float(min(values)), float(max(values))
                    colA, colB = st.columns(2)
                    with colA:
                        min_input = st.number_input(f"Min {selected_numeric_col}", value=min_val, format="%.2f", key="numeric_min")
                    with colB:
                        max_input = st.number_input(f"Max {selected_numeric_col}", value=max_val, format="%.2f", key="numeric_max")
                    
                    # Only add filter if user changed from defaults
                    if min_input != min_val or max_input != max_val:
                        filters_applied.append((selected_numeric_col, (min_input, max_input)))
    
    # OTHER CATEGORICAL COLUMNS
    other_categorical = [c for c in categorical_cols if c not in ["City", "Year", zipcode_col]]
    if other_categorical:
        with st.expander("Filter by Other Columns", expanded=False):
            selected_cat_col = st.selectbox("Choose column", ["None"] + other_categorical, key="cat_col_select")
            if selected_cat_col != "None":
                unique_vals = sorted(set(v for v in filter_df[selected_cat_col] if v is not None))
                selected_vals = st.multiselect(
                    f"Select {selected_cat_col} values",
                    unique_vals,
                    default=[],
                    key="cat_filter"
                )
                if selected_vals:
                    filters_applied.append((selected_cat_col, selected_vals))
    
    # Show count of active filters
    if filters_applied:
        st.info(f"{len(filters_applied)} filter(s) active")
    
    # APPLY FILTERS button
    if st.button("Apply Filters", type="primary"):
        filtered_df = filter_df
        
        # Apply each filter one by one
        for name, val in filters_applied:
            if name == "City":
                filtered_df = filtered_df.filter(lambda row: row["City"] in val)
            elif name == "Year":
                y0, y1 = val
                # Check for None to avoid comparison errors
                filtered_df = filtered_df.filter(lambda row: row["Year"] is not None and y0 <= row["Year"] <= y1)
            elif name in ["Zipcode", "ZipCode", "Five-Digit ZIP Code"]:
                filtered_df = filtered_df.filter(lambda row: row[name] in val)
            elif isinstance(val, tuple):
                # Numeric range filter
                lo, hi = val
                filtered_df = filtered_df.filter(lambda row: row[name] is not None and lo <= row[name] <= hi)
            else:
                # Categorical multiselect filter
                filtered_df = filtered_df.filter(lambda row: row[name] in val)
        
        # Store filtered results in session state so they persist across pagination
        key_base = f"filtered_results_{selected_dataset}"
        st.session_state[key_base] = filtered_df
        st.session_state[f"{key_base}_total"] = filter_df.shape[0]
    
    # Display filtered results from session state
    key_base = f"filtered_results_{selected_dataset}"
    if key_base in st.session_state:
        filtered_df = st.session_state[key_base]
        original_total = st.session_state[f"{key_base}_total"]
        
        st.success(f"Found {filtered_df.shape[0]:,} matching rows (from {original_total:,} total)")
        
        if filtered_df.shape[0] > 0:
            st.subheader("Filtered Results")
            
            # Show first 6 columns if there are many columns
            display_cols = filter_df.columns[:6] if len(filter_df.columns) > 6 else filter_df.columns
            
            ###############################################################
            # PAGINATION for filtered results
            ###############################################################
            ROWS_PER_PAGE = 50
            total_rows = filtered_df.shape[0]
            total_pages = (total_rows + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE
            
            # Track page per dataset
            page_key = f"filter_page_{selected_dataset}"
            if page_key not in st.session_state:
                st.session_state[page_key] = 1
            
            # Reset to page 1 when filters change
            filter_state_key = f"last_filters_{selected_dataset}"
            current_filter_state = str(filters_applied)
            if filter_state_key not in st.session_state:
                st.session_state[filter_state_key] = current_filter_state
                st.session_state[page_key] = 1
            elif st.session_state[filter_state_key] != current_filter_state:
                st.session_state[page_key] = 1
                st.session_state[filter_state_key] = current_filter_state
            
            st.write(f"Total: {filtered_df.shape[0]:,} rows x {len(display_cols)} columns")
            
            # Pagination controls
            colA, colB = st.columns([2, 1])
            with colA:
                st.markdown(
                    f"<div style='text-align:center; padding:12px; font-size:18px; font-weight:bold;'>"
                    f"Page {st.session_state[page_key]} of {total_pages:,}</div>",
                    unsafe_allow_html=True
                )
            with colB:
                page_input = st.number_input(
                    "Jump to page:",
                    min_value=1,
                    max_value=total_pages,
                    value=st.session_state[page_key],
                    key=f"filter_page_jump_{selected_dataset}"
                )
                # Keep page number synced
                st.session_state[page_key] = page_input
            
            # Calculate which rows to show
            start_idx = (st.session_state[page_key] - 1) * ROWS_PER_PAGE
            end_idx = min(start_idx + ROWS_PER_PAGE, total_rows)
            st.caption(f"Showing rows {start_idx + 1:,} to {end_idx:,} of {total_rows:,}")
            
            # Display the data
            display_data = {c: filtered_df[c][start_idx:end_idx] for c in display_cols}
            st.dataframe(display_data, use_container_width=True)
        else:
            st.warning("No rows match your filters. Try adjusting the criteria.")

###############################################################################
# TAB 3: FILTER AND AGGREGATE
# First filter data, then group it and compute statistics
###############################################################################
with tab3:
    st.header(f"Filter and Aggregate - {selected_dataset}")
    st.markdown("Filter data, then group it and compute stats.")
    analysis_df = current_df
    
    # Show example code
    with st.expander("Under the Hood: GroupBy and Aggregation", expanded=False):
        st.code("""
# Group by a column and compute aggregation
grouped_df = df.groupby("City", agg={"Price Index": "mean"})
""", language="python")
        st.info("SQL Equivalent: SELECT City, AVG(Price_Index) FROM data GROUP BY City")
    
    ###########################################################################
    # STEP 1: Optional filtering before aggregation
    ###########################################################################
    st.subheader("Step 1: Filter Data (Optional)")
    
    with st.expander("Apply Filters", expanded=False):
        filters_to_apply = []
        
        # Year filter - range slider
        if "Year" in analysis_df.columns:
            years = [y for y in analysis_df["Year"] if y is not None]
            if years:
                min_year, max_year = int(min(years)), int(max(years))
                enable_year = st.checkbox("Filter by Year Range", value=False, key="agg_year_filter")
                if enable_year:
                    year_range = st.slider(
                        "Year Range",
                        min_year,
                        max_year,
                        (min_year, max_year),
                        key="agg_year_range"
                    )
                    filters_to_apply.append(("Year", year_range))
        
        # City filter - multiselect
        if "City" in analysis_df.columns:
            all_cities = sorted(set(c for c in analysis_df["City"] if c is not None))
            if all_cities and len(all_cities) < 100:
                colA, colB = st.columns(2)
                with colA:
                    enable_city = st.checkbox("Filter by City", value=False, key="agg_city_filter")
                with colB:
                    if enable_city:
                        selected_cities = st.multiselect("Select Cities", all_cities, default=[], key="agg_city_select")
                        if selected_cities:
                            filters_to_apply.append(("City", selected_cities))
        
        # Apply the filters to the data
        if filters_to_apply:
            for name, val in filters_to_apply:
                if name == "Year":
                    y0, y1 = val
                    analysis_df = analysis_df.filter(lambda row: row["Year"] is not None and y0 <= row["Year"] <= y1)
                elif name == "City":
                    analysis_df = analysis_df.filter(lambda row: row["City"] in val)
            
            st.info(f"{len(filters_to_apply)} filter(s) applied. Rows left: {analysis_df.shape[0]:,}")
        else:
            st.info(f"No filters applied. Using all {analysis_df.shape[0]:,} rows.")
    
    ###########################################################################
    # STEP 2: Group and aggregate
    ###########################################################################
    st.subheader("Step 2: Group and Aggregate")
    
    # Find columns suitable for grouping (not too many unique values)
    groupable_cols = []
    for col in analysis_df.columns:
        unique_vals = set(analysis_df[col])
        # Allow up to 2500 unique values (e.g., zipcodes)
        if 1 < len(unique_vals) < 2500:
            groupable_cols.append(col)
    
    # Find numeric columns for aggregation, excluding identifiers
    numeric_cols = []
    exclude_keywords = ["zip", "year", "id", "code", "name", "beach"]
    for col in analysis_df.columns:
        col_lower = col.lower()
        # Skip if column name suggests it's an identifier
        if any(k in col_lower for k in exclude_keywords):
            continue
        
        # Check if at least 80% of values are numeric
        # This handles columns with some missing data (like ".")
        sample_vals = analysis_df[col][:100]
        numeric_count = sum(1 for v in sample_vals if v is not None and isinstance(v, (int, float)))
        total_count = len([v for v in sample_vals if v is not None])
        if total_count > 0 and (numeric_count / total_count) >= 0.8:
            numeric_cols.append(col)
    
    # Check if we have columns to work with
    if not groupable_cols:
        st.warning("No suitable columns for grouping in this dataset.")
    elif not numeric_cols:
        st.warning("No numeric columns for aggregation in this dataset.")
    else:
        # Let user choose grouping column and aggregation
        colA, colB = st.columns(2)
        with colA:
            group_by_col = st.selectbox("Group By Column", groupable_cols, index=0)
        with colB:
            agg_func = st.selectbox("Aggregation Function", ["mean", "sum", "min", "max", "count"], index=0)
        
        agg_col = st.selectbox("Column to Aggregate", numeric_cols, index=0)
        
        # Perform the aggregation
        if st.button("Compute Aggregation", type="primary"):
            grouped_df = analysis_df.groupby(group_by_col, agg={agg_col: agg_func})
            
            st.success(f"Grouped by {group_by_col}, computed {agg_func} of {agg_col}.")
            st.write(f"Results: {grouped_df.shape[0]} groups")
            
            # Display first 50 groups
            display_data = {c: grouped_df[c][:50] for c in grouped_df.columns}
            st.dataframe(display_data, use_container_width=True)
            
            if grouped_df.shape[0] > 50:
                st.caption(f"Showing first 50 of {grouped_df.shape[0]} groups.")

###############################################################################
# TAB 4: JOIN DATA
# Combine two datasets based on matching values in a column
###############################################################################
with tab4:
    st.header("Join Operations")
    st.markdown("Combine datasets using an inner join with a hash-based approach.")
    
    # Show example code
    with st.expander("Under the Hood: Join Algorithm", expanded=False):
        st.code("""
# Join on same column name
result = df1.join(df2, on="City")

# Join when column names differ
result = df1.join(df2, left_on="Zipcode", right_on="Five-Digit ZIP Code")
""", language="python")
    
    # Let user choose which type of join demo to see
    join_type = st.radio(
        "Select Join Demonstration:",
        ["Simple Join (Same Column Name)", "Advanced Join (Different Column Names)"],
        horizontal=True
    )
    
    ###########################################################################
    # DEMO 1: Simple join where both datasets have the same column name
    ###########################################################################
    if join_type == "Simple Join (Same Column Name)":
        st.subheader("Demo 1: Join Housing Data with Demographics")
        
        # Step 1: Create a small demo dataset
        st.write("**Step 1: Create Demographics DataFrame**")
        demo_data = {
            "City": ["Irvine", "Anaheim", "Santa Ana", "Newport Beach",
                     "Costa Mesa", "Aliso Viejo", "Huntington Beach"],
            "Population": [280000, 350000, 310000, 85000, 113000, 52000, 200000],
            "Median_Income": [95000, 58000, 55000, 120000, 75000, 98000, 88000]
        }
        df_demo = DataFrame(demo_data)
        st.dataframe(demo_data)
        
        # Step 2: Aggregate housing data by city
        st.write("**Step 2: Aggregate Housing Data by City**")
        st.code("""
housing_agg = df.groupby("City", agg={"Price Index": "mean"})
""", language="python")
        
        housing_agg = df.groupby("City", agg={"Price Index": "mean"})
        
        st.write(f"Aggregated housing data: {housing_agg.shape[0]} cities")
        st.dataframe({c: housing_agg[c][:10] for c in housing_agg.columns})
        
        # Step 3: Join the two datasets
        st.write("**Step 3: Perform Inner Join**")
        st.code("""
joined_df = housing_agg.join(df_demo, on="City")
""", language="python")
        
        if st.button("Join Datasets", type="primary", key="simple_join"):
            import time
            start = time.time()
            # Perform the join on the City column
            joined_df = housing_agg.join(df_demo, on="City")
            end = time.time()
            
            st.success(f"Join completed in {end - start:.4f} seconds.")
            st.metric("Joined Cities", joined_df.shape[0])
            st.dataframe({c: joined_df[c] for c in joined_df.columns})
            
            # Show some insights about the joined data
            st.subheader("Insights")
            if joined_df.shape[0] > 0:
                prices = joined_df["Price Index_mean"]
                cities = joined_df["City"]
                max_idx = prices.index(max(prices))
                min_idx = prices.index(min(prices))
                
                colA, colB = st.columns(2)
                with colA:
                    st.metric("Most Expensive City", cities[max_idx], f"${prices[max_idx]:,.2f}")
                with colB:
                    st.metric("Most Affordable City", cities[min_idx], f"${prices[min_idx]:,.2f}")
    
    ###########################################################################
    # DEMO 2: Advanced join with different column names
    ###########################################################################
    else:
        st.subheader("Demo 2: Join with Different Column Names")
        st.markdown("Demonstrates left_on / right_on join support.")
        
        # Let user pick which datasets to join
        join_option = st.selectbox(
            "Select Datasets to Join:",
            ["Zillow JOIN HPI (by Zipcode)", "Income JOIN HPI (by Zipcode)"]
        )
        
        #######################################################################
        # Option A: Zillow JOIN HPI
        #######################################################################
        if join_option == "Zillow JOIN HPI (by Zipcode)":
            if hpi is None:
                st.error("HPI dataset not loaded. Make sure FHFA_HPI_by_Zip.csv is in the directory.")
            else:
                st.write(f"HPI Dataset: {hpi.shape[0]:,} rows x {hpi.shape[1]} columns")
                
                # Show the different column names
                colA, colB = st.columns(2)
                with colA:
                    st.write("Zillow column:")
                    st.code("Zipcode")
                with colB:
                    st.write("HPI column:")
                    st.code("Five-Digit ZIP Code")
                
                # Let user select year range to filter data before join
                # This prevents huge cartesian products
                colA, colB = st.columns(2)
                with colA:
                    year_start = st.number_input("Start Year", 2014, 2023, 2020, step=1, key="join_year_start")
                with colB:
                    year_end = st.number_input("End Year", 2014, 2023, 2023, step=1, key="join_year_end")
                
                if year_start > year_end:
                    st.error("Start year must be less than or equal to end year.")
                else:
                    if st.button("Join with left_on/right_on", type="primary", key="advanced_join_1"):
                        with st.spinner("Performing join..."):
                            # Filter both datasets to year range first
                            df_year = df.filter(lambda row: row["Year"] is not None and year_start <= row["Year"] <= year_end)
                            hpi_year = hpi.filter(lambda row: row["Year"] is not None and year_start <= row["Year"] <= year_end)
                            
                            import time
                            start = time.time()
                            # Use left_on and right_on since column names differ
                            result = df_year.join(hpi_year, left_on="Zipcode", right_on="Five-Digit ZIP Code")
                            end = time.time()
                            
                            st.success(f"Join completed in {end - start:.2f} seconds.")
                            st.metric("Joined Rows", f"{result.shape[0]:,}")
                            st.metric("Joined Columns", result.shape[1])
                            
                            # Show sample of joined data
                            st.subheader("Sample of Joined Data (First 100 rows)")
                            st.caption(f"Showing 100 of {result.shape[0]:,} total rows. Full dataset available for download/export.")
                            
                            # Display key columns
                            display_cols = ["Zipcode", "City", "Price Index", "HPI", "Annual Change (%)"]
                            display_data = {c: result[c][:100] for c in display_cols if c in result.columns}
                            st.dataframe(display_data, use_container_width=True)
        
        #######################################################################
        # Option B: Income JOIN HPI
        #######################################################################
        else:
            if income is None or hpi is None:
                st.error("Income and/or HPI dataset missing. Put Medium_Income.csv and FHFA_HPI_by_Zip.csv in the directory.")
            else:
                st.write(f"Income Dataset: {income.shape[0]:,} rows x {income.shape[1]} columns")
                st.write(f"HPI Dataset: {hpi.shape[0]:,} rows x {hpi.shape[1]} columns")
                
                # Show the different column names
                colA, colB = st.columns(2)
                with colA:
                    st.write("Income column:")
                    st.code("ZipCode")
                with colB:
                    st.write("HPI column:")
                    st.code("Five-Digit ZIP Code")
                
                # Let user select year range
                colA, colB = st.columns(2)
                with colA:
                    year_start = st.number_input("Start Year", 2011, 2022, 2020, step=1, key="income_join_year_start")
                with colB:
                    year_end = st.number_input("End Year", 2011, 2022, 2022, step=1, key="income_join_year_end")
                
                if year_start > year_end:
                    st.error("Start year must be less than or equal to end year.")
                else:
                    if st.button("Join with left_on/right_on", type="primary", key="advanced_join_2"):
                        with st.spinner("Performing join..."):
                            # Filter to year range
                            income_years = income.filter(lambda row: row["Year"] is not None and year_start <= row["Year"] <= year_end)
                            hpi_years = hpi.filter(lambda row: row["Year"] is not None and year_start <= row["Year"] <= year_end)
                            
                            import time
                            start = time.time()
                            # Join with different column names
                            result = income_years.join(hpi_years, left_on="ZipCode", right_on="Five-Digit ZIP Code")
                            end = time.time()
                            
                            st.success(f"Join completed in {end - start:.2f} seconds.")
                            st.metric("Joined Rows", f"{result.shape[0]:,}")
                            
                            # Show sample of results
                            st.subheader("Sample of Joined Data (First 100 rows)")
                            st.caption(f"Showing 100 of {result.shape[0]:,} total rows. Full dataset available for download/export.")
                            st.dataframe({c: result[c][:100] for c in result.columns}, use_container_width=True)