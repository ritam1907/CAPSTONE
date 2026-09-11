import pandas as pd
import numpy as np

# Load dataset
df_raw = pd.read_csv("dataset.csv")

# (strip whitespace and lowercase)
df_raw.columns = df_raw.columns.str.strip().str.lower()

# Map common dataset variations for title, artist, ID, and features
rename_map = {}
for col in df_raw.columns:
    if 'name' in col and 'track' in col:
        rename_map[col] = 'track_name'
    elif 'artist' in col:
        rename_map[col] = 'artists'
    elif 'id' in col and 'track' in col:
        rename_map[col] = 'track_id'
    elif 'genre' in col:
        rename_map[col] = 'genre'

df_raw = df_raw.rename(columns=rename_map)

# Feature columns to check
feature_cols = ['danceability', 'energy', 'valence', 'tempo']

for col in feature_cols:
    if col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')
    else:
        df_raw[col] = 0.5

# Drop rows where identifiers are missing
df_raw = df_raw.dropna(subset=['track_id', 'track_name', 'artists'] + feature_cols).reset_index(drop=True)

def recommend_tracks(target_vector, top_n=100):
    features = df_raw[feature_cols].values
    
    # Extract target values
    target = np.array([
        target_vector.get('danceability', 0.5),
        target_vector.get('energy', 0.5),
        target_vector.get('valence', 0.5),
        target_vector.get('tempo', 120) / 200.0
    ])
    
    # Euclidean distance calculation
    distances = np.linalg.norm(features - target, axis=1)
    df_raw['distance'] = distances
    
    # Return top matches
    recommended = df_raw.sort_values('distance').head(top_n)
    return recommended