import duckdb
from pathlib import Path

parquet_input = r"C:\\Work\\github\\POC_AV\\data\\fixpunkte-lfp1_2056_5728.gdb\\FIDA.parquet"
query_OUT = Path(r"C:\\Work\\github\\POC_AV\\data\\fixpunkte-lfp1_2056_5728.gdb") / "query.json"
query_OUT.parent.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()

df = con.execute(f"SELECT * FROM read_parquet('{parquet_input}')").df()
print(df.columns.tolist())

NBINDNENT = con.execute(f"""
    SELECT DISTINCT NBIDENT 
    FROM read_parquet('{parquet_input}')
    ORDER BY NBIDENT
""").df()
print(f"NBINDNENT: {NBINDNENT}")

result = con.execute(f"""
    SELECT *
    FROM read_parquet('{parquet_input}')
    WHERE NBIDENT IN ('CH0300001174', 'CH0300001173')
""").df()

print(result.to_string())
