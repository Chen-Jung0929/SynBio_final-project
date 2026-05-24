import os
import pandas as pd

tables_dir = "results/tables"
csv_files = [f for f in os.listdir(tables_dir) if f.endswith(".csv")]

print("Available tables:")
for f in sorted(csv_files):
    path = os.path.join(tables_dir, f)
    df = pd.read_csv(path)
    print(f"\n=== {f} (shape: {df.shape}) ===")
    print(df.head(10))
