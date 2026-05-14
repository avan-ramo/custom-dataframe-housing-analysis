from csv_parser import DataFrame

###############################################################################
# initialize test method
###############################################################################
print("=== DataFrame initialization tests ===")

# Test 1: Create empty DataFrame
df_empty = DataFrame()
print("Empty DataFrame:", df_empty.data)

# Test 2: Create DataFrame with data
data = {
    'City': ['Irvine', 'Anaheim', 'Santa Ana'],
    'Price': [850000, 650000, 550000],
    'Zip':   ['92602', '92805', '92701']
}
df = DataFrame(data)
print("DataFrame created:", df.data)

# Test 3: Try mismatched lengths (should raise error)
try:
    bad_data = {
        'City': ['Irvine', 'Anaheim', 'Santa Ana'],
        'Price': [850000, 650000]  # Only 2 prices!
    }
    df_bad = DataFrame(bad_data)
except ValueError as err:
    print("Caught error:", err)

###############################################################################
# Test __getitem__ method
###############################################################################
print("\n=== __getitem__ tests ===")

# 1) Single column access (success)
price = df['Price']
assert price == [850000, 650000, 550000], "__getitem__ single column failed"
print("Single column ok ->", price)

# 2) Single column missing (KeyError)
try:
    _ = df['Population']
    raise AssertionError("Expected KeyError for missing single column")
except KeyError as err:
    print("Single missing column raises KeyError ->", err)

# 3) Multiple columns projection (success)
proj = df[['City', 'Zip']]
assert isinstance(proj, DataFrame), "Projection should return a DataFrame"
assert proj.columns == ['City', 'Zip'], "Projection columns mismatch"
assert proj.data['City'] == ['Irvine', 'Anaheim', 'Santa Ana'], "Projected City data mismatch"
assert proj.data['Zip'] == ['92602', '92805', '92701'], "Projected Zip data mismatch"
print("Projection ok ->", proj.data)

# 4) Multiple columns with one missing (KeyError)
try:
    _ = df[['City', 'Population']]
    raise AssertionError("Expected KeyError for missing column in projection")
except KeyError as e:
    print("Projection with missing column raises KeyError ->", e)

# 5) Type errors (non-str/list keys)
for bad_key in [None, 123, 3.14, ('City',), {'City'}, {'City': True}]:
    try:
        _ = df[bad_key]
        raise AssertionError(f"Expected TypeError for key={bad_key!r}")
    except TypeError as e:
        print(f"Type check ok for key={bad_key!r} ->", e)

# 6) Empty DataFrame behavior
empty = DataFrame()
try:
    _ = empty['Any']
    raise AssertionError("Expected KeyError on empty DataFrame for any column")
except KeyError as e:
    print("Empty DataFrame single column raises KeyError ->", e)

try:
    _ = empty[['A', 'B']]
    raise AssertionError("Expected KeyError on empty DataFrame for projection")
except KeyError as e:
    print("Empty DataFrame projection raises KeyError ->", e)

# 7) Order preservation in projection
proj_order = df[['Zip', 'City']]
assert proj_order.columns == ['Zip', 'City'], "Projection should preserve requested column order"
print("Projection preserves order ->", proj_order.columns)

print("All __getitem__ tests passed!")

###############################################################################
# Test __repr__ method
###############################################################################
print("\n=== __repr__ tests ===")

# 1) Non-empty DataFrame
print("Non-empty DataFrame repr:")
print(df)  # should invoke __repr__ automatically

# 2) Empty DataFrame
print("\nEmpty DataFrame repr:")
print(df_empty)

# 3) Larger DataFrame (check truncation)
data_large = {
    "ID": list(range(10)),
    "Value": [v * 2 for v in range(10)]
}
df_large = DataFrame(data_large)
print("\nLarge DataFrame repr (should truncate to 5 rows):")
print(df_large)

###############################################################################
# Test _convert_type helper
###############################################################################
print("\n=== _convert_type tests ===")

test_values = ['42', '3.14', 'True', 'false', 'YES', 'no', '', 'None', 'null', 'hello', '1e-3']
converted = [DataFrame._convert_type(v) for v in test_values]
print("Converted:", converted)



###############################################################################
# Test read_csv function
###############################################################################
print("\n=== read_csv tests ===")

# Create small CSV file for testing
csv_content = """City,Price,Zip
Irvine,850000,92602
Anaheim,650000,92805
Santa Ana,550000,92701
"""

with open("test_housing.csv", "w", encoding="utf-8") as file:
    file.write(csv_content)

# Read CSV into DataFrame
df_csv = DataFrame.read_csv("test_housing.csv")
print(df_csv)

assert df_csv.data['City'][0] == 'Irvine'
assert df_csv.data['Price'][1] == 650000
assert len(df_csv.data['Zip']) == 3

# No-header variant
csv_text_nohdr = """Irvine,850000,92602
Anaheim,650000,92805
"""
with open("test_nohdr.csv", "w", encoding="utf-8") as f:
    f.write(csv_text_nohdr)

df_nohdr = DataFrame.read_csv("test_nohdr.csv", header=False)
print(df_nohdr)
assert df_nohdr.columns == ['col1', 'col2', 'col3']
assert df_nohdr['col2'][0] == 850000

print("read_csv tests passed!")

