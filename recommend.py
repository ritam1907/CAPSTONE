import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

print("--> Loading 1.2M track dataset into memory...")
try:
    # Read the CSV normally first to check its structure
    df_raw = pd.read_csv("dataset.csv", low_memory=False)
except Exception as e:
    raise RuntimeError(f"Failed to read dataset.csv: {e}")

# If the CSV doesn't have a header row, pandas would have taken the first row of data 
# as column names. We check and re-read with header=None if necessary.
if any(str(col).replace('.', '', 1).isdigit() for col in df_raw.columns[:5]):
    df_raw = pd.read_csv("dataset.csv", header=None, low_memory=False)

# Map the 20 exact columns based on your dataset format layout:
if len(df_raw.columns) >= 20:
    df_raw.columns = [
        "csv_index", "artists", "track_name", "track_id", "popularity", 
        "year", "genre", "danceability", "energy", "key", "loudness", 
        "mode", "speechiness", "acousticness", "instrumentalness", 
        "liveness", "valence", "tempo", "duration_ms", "time_signature"
    ]

FEATURE_COLS = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "loudness"]
META_COLS = ["track_id", "artists", "track_name", "genre", "popularity", "year"]

# Ensure all feature columns are forced to numeric (coercing any stray text headers to NaN)
for col in FEATURE_COLS:
    df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')

# Clean data: drop missing values and remove duplicate tracks
df_clean = df_raw[META_COLS + FEATURE_COLS].dropna().drop_duplicates(
    subset=["track_name", "artists"]
).reset_index(drop=True)

print(f"--> Fitting MinMaxScaler across {len(df_clean):,} unique tracks...")
scaler = MinMaxScaler()
scaled_features = scaler.fit_transform(df_clean[FEATURE_COLS])
df_scaled = pd.DataFrame(scaled_features, columns=FEATURE_COLS)

print(f"--> 1.2M Vector Engine ready!")

def recommend_tracks(target_vector: dict, top_n: int = 100):
    """
    Computes Euclidean distance across normalized feature vectors 
    for the 1.2M dataset and returns top matching results.
    """
    target_df = pd.DataFrame([target_vector])
    
    for col in FEATURE_COLS:
        if col not in target_df.columns:
            target_df[col] = 0.5
            
    target_scaled = scaler.transform(target_df[FEATURE_COLS])[0]
    
    diffs = df_scaled.values - target_scaled
    distances = np.linalg.norm(diffs, axis=1)
    
    results = df_clean.copy()
    results["similarity_distance"] = distances
    top_matches = results.sort_values(by="similarity_distance").head(top_n)
    
    return top_matches[META_COLS + ["similarity_distance"]]