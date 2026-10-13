"""Summarize a run and save plots to docs/.

Usage:
    python3 analysis/analyze_run.py [path/to/run.csv]   (default: newest run)
"""
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from common import list_runs, load_run, summarize  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / 'docs'


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        runs = list_runs()
        if not runs:
            sys.exit('No runs found in data/runs. Run the data_recorder first.')
        path = runs[0]

    df = load_run(path)
    print(f'Run: {path.name}')
    for key, value in summarize(df).items():
        print(f'  {key}: {value:.3f}' if isinstance(value, float) else f'  {key}: {value}')

    # Plain numpy arrays: older matplotlib versions fail on pandas Series indexing.
    def col(name):
        return df[name].to_numpy(dtype=float)

    t, detected = col('t'), col('detected')
    latency = col('latency_ms')[detected == 1]
    latency = latency[~np.isnan(latency)]

    OUT_DIR.mkdir(exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))

    axes[0, 0].plot(t, col('confidence'), '.-', ms=3)
    axes[0, 0].set(title='Detection confidence', xlabel='time (s)', ylabel='confidence',
                   ylim=(0, 1))

    axes[0, 1].hist(latency, bins=20, color='tab:orange')
    axes[0, 1].set(title='Inference latency', xlabel='latency (ms)', ylabel='frames')

    axes[1, 0].step(t, detected, where='post', color='tab:green')
    axes[1, 0].set(title='Target visible (1) / lost (0)', xlabel='time (s)',
                   ylim=(-0.1, 1.1))

    if df['x'].notna().any():
        axes[1, 1].plot(col('x'), col('y'), '-', lw=1)
        axes[1, 1].set(title='Drone trajectory', xlabel='x (m)', ylabel='y (m)',
                       aspect='equal')
    else:
        axes[1, 1].plot(t, col('cmd_ang_z'), color='tab:red')
        axes[1, 1].set(title='Angular velocity command', xlabel='time (s)',
                       ylabel='rad/s')

    fig.suptitle(path.name)
    fig.tight_layout()
    out = OUT_DIR / f'{path.stem}_summary.png'
    fig.savefig(out, dpi=130)
    print(f'Saved plot: {out}')


if __name__ == '__main__':
    main()
