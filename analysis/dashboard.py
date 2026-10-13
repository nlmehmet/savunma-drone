"""Streamlit dashboard for data_recorder runs.

Usage:
    streamlit run analysis/dashboard.py
"""
import plotly.express as px
import streamlit as st

from common import list_runs, load_run, summarize

st.set_page_config(page_title='Drone run analysis', layout='wide')
st.title('Drone run analysis')

runs = list_runs()
if not runs:
    st.info('No runs found in data/runs. Run the data_recorder node first.')
    st.stop()

choice = st.sidebar.selectbox('Run', [r.name for r in runs])
df = load_run(next(r for r in runs if r.name == choice))
det = df[df['detected'] == 1]
stats = summarize(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric('Duration', f"{stats['duration_s']:.1f} s")
c2.metric('Detection rate', f"{stats['detection_rate'] * 100:.0f} %")
c3.metric('Mean latency', f"{stats['mean_latency_ms']:.0f} ms")
c4.metric('Target lost events', stats['target_lost_events'])

left, right = st.columns(2)
left.plotly_chart(px.line(df, x='t', y='confidence', title='Detection confidence'),
                  width='stretch')
right.plotly_chart(px.histogram(det, x='latency_ms', nbins=25, title='Inference latency'),
                   width='stretch')

left, right = st.columns(2)
left.plotly_chart(px.line(df, x='t', y='detected', line_shape='hv',
                          title='Target visible (1) / lost (0)'),
                  width='stretch')
if df['x'].notna().any():
    right.plotly_chart(px.line(df, x='x', y='y', title='Drone trajectory'),
                       width='stretch')
else:
    right.plotly_chart(px.line(df, x='t', y='cmd_ang_z', title='Angular velocity command'),
                       width='stretch')

with st.expander('Raw data'):
    st.dataframe(df)
