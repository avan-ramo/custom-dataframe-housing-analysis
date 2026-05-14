from csv_parser import DataFrame

###############################################################################
# Test read_csv function
###############################################################################
print("=== Loading Orange County Housing Data ===")

# Load the dataset
df = DataFrame.read_csv('OC_Transposed_Zillow.csv')

# Basic info
print(f"\nDataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"\nColumn names ({len(df.columns)} total):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

# Preview data
print("\n=== First 5 rows ===")
print(df)

# Try accessing specific columns
print("\n=== Sample column access ===")
cities = df['City']
print(f"First 5 cities: {cities[:5]}")

prices = df['Price Index']
print(f"First 5 price indices: {prices[:5]}")

# Try projection
print("\n=== Projection test ===")
df_subset = df[['City', 'Price Index', 'Year']]
print(df_subset)

###############################################################################
# Test filter function
###############################################################################

print("\n=== Filter test ===")

# Filter: Only Irvine properties
df_irvine = df.filter(lambda row: row['City'] == 'Irvine')
print(f"Irvine properties: {df_irvine.shape[0]} rows")
print(df_irvine)

# Filter: High price index (> 600000)
df_expensive = df.filter(lambda row: row['Price Index'] > 600000)
print(f"\nExpensive properties (Price Index > 600000): {df_expensive.shape[0]} rows")
print(df_expensive)

# Filter: Complex condition
df_complex = df.filter(lambda row: row['City'] == 'Irvine' and row['Year'] >= 2020)
print(f"\nIrvine properties from 2020+: {df_complex.shape[0]} rows")
print(df_complex)

###############################################################################
# Test groupby and aggregation functions
###############################################################################

print("\n=== GroupBy & Aggregation Test ===")

# Test 1: Average price by city
print("Average Price Index by City:")
grouped_mean = df.groupby('City', agg={'Price Index': 'mean'})
print(grouped_mean)

# Test 2: Multiple aggregations
print("\nMultiple aggregations on Price Index:")
grouped_multi = df.groupby('City', agg={
    'Price Index': 'mean',
    'Year': 'max'
})
print(grouped_multi)

# Test 3: Count properties by city
print("\nCount of properties by City:")
grouped_count = df.groupby('City', agg={'Price Index': 'count'})
print(grouped_count)

# Test 4: Year-based grouping
print("\nAverage Price Index by Year:")
grouped_year = df.groupby('Year', agg={'Price Index': 'mean'})
print(grouped_year.head(10))  # Show first 10 years

###############################################################################
# Test Join Function
###############################################################################

print("\n=== Join Test (Fixed) ===")

# Create demographics DataFrame
demo_data = {
    'City': ['Irvine', 'Anaheim', 'Santa Ana', 'Newport Beach', 'Costa Mesa', 'Aliso Viejo'],
    'Population': [280000, 350000, 310000, 85000, 113000, 52000],
    'Median_Income': [95000, 58000, 55000, 120000, 75000, 98000]
}
df_demo = DataFrame(demo_data)

print("Demographics DataFrame:")
print(df_demo)

# Option 1: Filter for specific cities that are in demographics
print("\n--- Option 1: Filter for cities in demographics ---")
cities_to_join = ['Irvine', 'Anaheim', 'Santa Ana']
df_housing_filtered = df.filter(lambda row: row['City'] in cities_to_join)
df_housing_subset = df_housing_filtered[['City', 'Price Index', 'Year']]

print(f"Housing subset: {df_housing_subset.shape[0]} rows")
print(df_housing_subset.head())

# Now join
joined = df_housing_subset.join(df_demo, on='City')
print(f"\nJoined result: {joined.shape[0]} rows")
print(joined.head(10))

# Option 2: Use groupby to get one row per city, then join
print("\n--- Option 2: Aggregate first, then join ---")
housing_avg = df.groupby('City', agg={'Price Index': 'mean'})
print(f"Average price by city: {housing_avg.shape[0]} cities")
print(housing_avg.head())

joined_agg = housing_avg.join(df_demo, on='City')
print(f"\nJoined aggregated data: {joined_agg.shape[0]} rows")
print(joined_agg)

###############################################################################
# Additional Real Dataset Join Tests
###############################################################################

print("\n" + "="*80)
print("=== Real Dataset Join Tests ===")
print("="*80)

# Test 1: Small Year-based Join (verify correctness)
print("\n--- Test 1: Small Year-based Join ---")
print("Big_3_Annual_Foot_Traffic ⋈ Crime_Data (on Year)")

traffic = DataFrame.read_csv('Big_3_Annual_Foot_Traffic.csv')
crime = DataFrame.read_csv('Crime_Data_City_Level_Arrest_Data.csv')

print(f"Traffic data: {traffic.shape}")
print(f"Crime data: {crime.shape}")
print("\nTraffic DataFrame:")
print(traffic.head())
print("\nCrime DataFrame:")
print(crime.head())

result1 = traffic.join(crime, on='Year')
print(f"\nJoined result: {result1.shape[0]} rows × {result1.shape[1]} columns")
print(result1.head(10))


# Test 2: Large Year-based Join (test performance)
print("\n" + "="*80)
print("--- Test 2: Large Year-based Join (Performance Test) ---")
print("OC_Transposed_Zillow ⋈ Big_3_Annual_Foot_Traffic (on Year)")

print(f"Zillow data: {df.shape}")
print(f"Traffic data: {traffic.shape}")
print("This will match 20,778 housing records to 11 traffic years...")

import time
start_time = time.time()
result2 = df.join(traffic, on='Year')
end_time = time.time()

print(f"\nJoined result: {result2.shape[0]} rows × {result2.shape[1]} columns")
print(f"Join completed in {end_time - start_time:.4f} seconds")
print("\nSample of joined data:")
print(result2.head())

# Show how many housing records matched to each year
print("\nVerifying join - count rows per year:")
year_counts = result2.groupby('Year', agg={'Price Index': 'count'})
print(year_counts.head(10))


# Test 3: Huge Join (stress test)
print("\n" + "="*80)
print("--- Test 3: Huge Join (Stress Test) ---")
print("FHFA_HPI_by_Zip ⋈ Medium_Income (on Year)")

hpi = DataFrame.read_csv('FHFA_HPI_by_Zip.csv')
income = DataFrame.read_csv('Medium_Income.csv')

print(f"HPI data: {hpi.shape}")
print(f"Income data: {income.shape}")
print("\nHPI DataFrame sample:")
print(hpi.head())
print("\nIncome DataFrame sample:")
print(income.head())

print("\nPerforming large join (this may take a moment)...")
start_time = time.time()
result3 = hpi.join(income, on='Year')
end_time = time.time()

print(f"\nJoined result: {result3.shape[0]} rows × {result3.shape[1]} columns")
print(f"Join completed in {end_time - start_time:.4f} seconds")
print("\nSample of joined data:")
print(result3.head())

# Show some statistics
print("\nJoin statistics:")
print(f"Original HPI rows: {hpi.shape[0]}")
print(f"Original Income rows: {income.shape[0]}")
print(f"Joined rows: {result3.shape[0]}")
print(f"Row multiplication factor: {result3.shape[0] / hpi.shape[0]:.2f}x")


###############################################################################
# NEW: Tests demonstrating left_on/right_on functionality
###############################################################################

# Test 4: Join with Different Column Names - Zillow & HPI by Zipcode
print("\n" + "="*80)
print("--- Test 4: Join with Different Column Names (left_on/right_on) ---")
print("OC_Transposed_Zillow ⋈ FHFA_HPI_by_Zip")
print("Left: 'Zipcode' | Right: 'Five-Digit ZIP Code'")

# Filter to 2014 to avoid huge cartesian product
df_2014 = df.filter(lambda row: row['Year'] == 2014)
hpi_2014 = hpi.filter(lambda row: row['Year'] == 2014)

print(f"\nFiltered to Year 2014:")
print(f"  Zillow: {df_2014.shape}")
print(f"  HPI: {hpi_2014.shape}")

print("\nColumn names:")
print(f"  Zillow has: 'Zipcode'")
print(f"  HPI has: 'Five-Digit ZIP Code'")

print("\nPerforming join with left_on='Zipcode', right_on='Five-Digit ZIP Code'...")
start_time = time.time()
result4 = df_2014.join(hpi_2014, left_on='Zipcode', right_on='Five-Digit ZIP Code')
end_time = time.time()

print(f"\nJoined result: {result4.shape[0]} rows × {result4.shape[1]} columns")
print(f"Join completed in {end_time - start_time:.4f} seconds")
print("\nSample of joined data:")
print(result4.head())

# Show unique zipcodes matched
unique_zips = set(result4['Zipcode'])
print(f"\nMatched {len(unique_zips)} unique zipcodes")
print(f"Example zipcodes: {list(unique_zips)[:5]}")


# Test 5: Join Income & HPI - Another Column Name Variation
print("\n" + "="*80)
print("--- Test 5: Another left_on/right_on Example ---")
print("Medium_Income ⋈ FHFA_HPI_by_Zip")
print("Left: 'ZipCode' | Right: 'Five-Digit ZIP Code'")

# Filter to 2013 for manageable size
income_2013 = income.filter(lambda row: row['Year'] == 2013)
hpi_2013 = hpi.filter(lambda row: row['Year'] == 2013)

print(f"\nFiltered to Year 2013:")
print(f"  Income: {income_2013.shape}")
print(f"  HPI: {hpi_2013.shape}")

print("\nColumn names:")
print(f"  Income has: 'ZipCode'")
print(f"  HPI has: 'Five-Digit ZIP Code'")

print("\nPerforming join with left_on='ZipCode', right_on='Five-Digit ZIP Code'...")
start_time = time.time()
result5 = income_2013.join(hpi_2013, left_on='ZipCode', right_on='Five-Digit ZIP Code')
end_time = time.time()

print(f"\nJoined result: {result5.shape[0]} rows × {result5.shape[1]} columns")
print(f"Join completed in {end_time - start_time:.4f} seconds")
print("\nSample of joined data:")
print(result5.head())

# Show some statistics
print("\nJoin statistics:")
print(f"  Income rows (2013): {income_2013.shape[0]}")
print(f"  HPI rows (2013): {hpi_2013.shape[0]}")
print(f"  Joined rows: {result5.shape[0]}")
print(f"  Zipcodes matched: {len(set(result5['ZipCode']))}")


print("\n" + "="*80)
print("=== All Join Tests Completed ===")
print("="*80)
print("\nSummary:")
print("  Tests 1-3: Original join functionality (on='column')")
print("  Tests 4-5: NEW enhanced join (left_on/right_on for different column names)")
print("="*80)
