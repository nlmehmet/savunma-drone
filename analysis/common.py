"""Shared helpers for loading and summarizing data_recorder CSV files."""
from pathlib import Path

import pandas as pd

RUNS_DIR = Path(__file__).resolve().parent.parent / 'data' / 'runs'
NUMERIC = [
    't', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'cmd_lin_x', 'cmd_ang_z',
    'detected', 'confidence', 'cx', 'cy', 'w', 'h', 'track_id', 'latency_ms',
]


def list_runs(runs_dir=RUNS_DIR):
    """Return run CSV files, newest first."""
    return sorted(Path(runs_dir).glob('run_*.csv'), reverse=True)


def load_run(path):
    """Load one run and make sure every column is numeric (empty cells -> NaN)."""
    df = pd.read_csv(path)
    for col in NUMERIC:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def summarize(df):
    """Compute headline metrics for a run."""
    det = df[df['detected'] == 1]
    lost_events = int(((df['detected'].diff() == -1)).sum())
    return {
        'duration_s': float(df['t'].max() - df['t'].min()) if len(df) else 0.0,
        'samples': int(len(df)),
        'detection_rate': float(df['detected'].mean()) if len(df) else 0.0,
        'mean_confidence': float(det['confidence'].mean()) if len(det) else float('nan'),
        'mean_latency_ms': float(det['latency_ms'].mean()) if len(det) else float('nan'),
        'p95_latency_ms': float(det['latency_ms'].quantile(0.95)) if len(det) else float('nan'),
        'unique_tracks': int(det['track_id'].nunique()) if len(det) else 0,
        'target_lost_events': lost_events,
    }
