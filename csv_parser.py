# csv_parser.py

###############################################################################
# Basic DataFrame class storing column-wise data
###############################################################################
class DataFrame:
    def __init__(self, data=None):
        # Store data as a dictionary of lists
        self.data = data or {}

        # Make sure all columns have same number of rows
        if self.data:
            lengths = {len(v) for v in self.data.values()}
            if len(lengths) != 1:
                raise ValueError("All columns must have the same length")

    @property
    def columns(self):
        return list(self.data.keys())

    @property
    def shape(self):
        if not self.data:
            return (0, 0)
        first_col = next(iter(self.data.values()))
        return (len(first_col), len(self.data))

    ###############################################################################
    # Column access: df["City"] or df[["City","Year"]]
    ###############################################################################
    def __getitem__(self, key):
        # Single column → return list
        if isinstance(key, str):
            if key not in self.data:
                raise KeyError(f"Column '{key}' not found")
            return self.data[key]

        # Projection of multiple columns → new DataFrame
        if isinstance(key, list):
            missing = [c for c in key if c not in self.data]
            if missing:
                raise KeyError(f"Columns not found: {missing}")
            return DataFrame({c: self.data[c] for c in key})

        raise TypeError("Key must be a string or list of strings")

    ###############################################################################
    # Pretty-print representation of the DataFrame
    ###############################################################################
    def __repr__(self):
        if not self.data:
            return "Empty DataFrame"

        cols = self.columns
        nrows = self.shape[0]
        show = min(5, nrows)

        # Compute simple width for printing
        widths = {}
        for c in cols:
            sample = [str(v) for v in self.data[c][:show]]
            widths[c] = max(len(c), *(len(s) for s in sample))

        header = " | ".join(c.ljust(widths[c]) for c in cols)
        lines = [f"DataFrame ({nrows} rows x {len(cols)} columns)", header, "-" * len(header)]

        # First few rows
        for i in range(show):
            row = " | ".join(str(self.data[c][i]).ljust(widths[c]) for c in cols)
            lines.append(row)

        if nrows > show:
            lines.append(f"... ({nrows - show} more rows)")

        return "\n".join(lines)

    ###############################################################################
    # Filtering rows based on a condition
    ###############################################################################
    def filter(self, cond):
        out = {c: [] for c in self.columns}
        total = self.shape[0]

        for i in range(total):
            row = {c: self.data[c][i] for c in self.columns}
            if cond(row):
                for c in self.columns:
                    out[c].append(row[c])

        return DataFrame(out)

    ###############################################################################
    # Head / Tail operations
    ###############################################################################
    def head(self, n=5):
        n = max(0, min(n, self.shape[0]))
        return DataFrame({c: self.data[c][:n] for c in self.columns})

    def tail(self, n=5):
        total = self.shape[0]
        n = max(0, min(n, total))
        return DataFrame({c: self.data[c][total-n:] for c in self.columns})

    ###############################################################################
    # GroupBy operation; supports both:
    # df.groupby("City").agg(...)
    # df.groupby("City", agg={...})
    ###############################################################################
    def groupby(self, col, agg=None):
        if col not in self.data:
            raise KeyError(f"Column '{col}' not found")

        gb = GroupBy(self, col)

        # usage: df.groupby("City", agg={...})
        if agg is not None:
            return gb.agg(agg)

        return gb

    ###############################################################################
    # Join two DataFrames (inner or left join)
    ###############################################################################
    def join(self, other, on=None, left_on=None, right_on=None, how="inner"):
        if not isinstance(other, DataFrame):
            raise TypeError("other must be a DataFrame")

        # Determine join keys
        if on is not None:
            left_key = right_key = on
        else:
            if left_on is None or right_on is None:
                raise ValueError("Specify on= or both left_on= and right_on=")
            left_key, right_key = left_on, right_on

        if left_key not in self.columns:
            raise KeyError(f"Left key '{left_key}' not found")
        if right_key not in other.columns:
            raise KeyError(f"Right key '{right_key}' not found")

        # Build hash table over right side
        right_index = {}
        for j in range(other.shape[0]):
            k = other.data[right_key][j]
            right_index.setdefault(k, []).append(j)

        # Construct output schema
        out_cols = list(self.columns)
        for c in other.columns:
            if c == right_key and left_key == right_key:
                continue
            new = c if c not in out_cols else f"{c}_right"
            out_cols.append(new)

        out = {c: [] for c in out_cols}

        # Probe left side
        for i in range(self.shape[0]):
            key = self.data[left_key][i]
            matches = right_index.get(key, [])

            if matches:
                for j in matches:
                    for c in self.columns:
                        out[c].append(self.data[c][i])
                    for c in other.columns:
                        if c == right_key and left_key == right_key:
                            continue
                        new = c if c not in self.columns else f"{c}_right"
                        out[new].append(other.data[c][j])
            elif how == "left":
                for c in self.columns:
                    out[c].append(self.data[c][i])
                for c in other.columns:
                    if c == right_key and left_key == right_key:
                        continue
                    new = c if c not in self.columns else f"{c}_right"
                    out[new].append(None)

        return DataFrame(out)

    ###############################################################################
    # CSV Loader (Store into DataFrame)
    ###############################################################################
    @classmethod
    def read_csv(cls, filepath, delimiter=",", skip_header=False, has_header=True):
        # skip_header overrides has_header
        if skip_header:
            has_header = False

        with open(filepath, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]

        if not lines:
            return cls()

        first = lines[0].split(delimiter)

        # Detect header row or auto-create column names
        if has_header:
            headers = [h.strip() for h in first]
            start = 1
        else:
            headers = [f"col{i}" for i in range(len(first))]
            start = 0

        data = {h: [] for h in headers}

        # Parse rows
        for ln in lines[start:]:
            parts = ln.split(delimiter)
            for i, h in enumerate(headers):
                val = parts[i].strip() if i < len(parts) else ""
                data[h].append(cls._convert_type(val))

        return cls(data)

    ###############################################################################
    # Type inference helper
    ###############################################################################
    @staticmethod
    def _convert_type(value):
        if value is None:
            return None

        v = value.strip()
        if v == "" or v == "." or v.lower() in {"null", "none", "na", "nan", "n/a"}:
            return None

        lv = v.lower()
        if lv in {"true", "yes"}:
            return True
        if lv in {"false", "no"}:
            return False

        # Try integer
        try:
            return int(v)
        except ValueError:
            pass

        # Try float
        try:
            return float(v)
        except ValueError:
            return v


###############################################################################
# GroupBy helper class
###############################################################################
class GroupBy:
    def __init__(self, df, col):
        self.df = df
        self.col = col
        self.groups = {}

        # Build value → indices map
        for i, key in enumerate(df.data[col]):
            self.groups.setdefault(key, []).append(i)

    ###############################################################################
    # Perform aggregations: {"Price Index": "mean"}
    ###############################################################################
    def agg(self, agg_map):
        funcs = {
            "mean": lambda xs: round(sum(xs) / len(xs), 2) if xs else None,
            "sum":  lambda xs: sum(xs) if xs else None,
            "min":  lambda xs: min(xs) if xs else None,
            "max":  lambda xs: max(xs) if xs else None,
            "count": lambda xs: len(xs),
        }

        out = {self.col: []}

        # Prepare output
        for cname, fn in agg_map.items():
            if fn not in funcs:
                raise ValueError(f"Unsupported aggregation: {fn}")
            if cname not in self.df.columns:
                raise KeyError(f"Column '{cname}' not found")

            out[f"{cname}_{fn}"] = []

        # Compute aggregations
        for key, idxs in self.groups.items():
            out[self.col].append(key)

            for cname, fn in agg_map.items():
                vals = [
                    self.df.data[cname][i]
                    for i in idxs
                    if self.df.data[cname][i] is not None
                ]
                out[f"{cname}_{fn}"].append(funcs[fn](vals))

        return DataFrame(out)