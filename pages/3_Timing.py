import calendar

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="LUMEN | Timing", page_icon="📅", layout="wide")

st.markdown("""<style>
.stApp { background: linear-gradient(180deg, #f4f8fb 0%, #ffffff 28%); }
h1 { color: #163A5F; }
div[data-testid="stMetric"] { background: #ffffff; border: 1px solid #dbe7ef; padding: 0.8rem; border-radius: 12px; box-shadow: 0 3px 10px rgba(22,58,95,.08); }
</style>""", unsafe_allow_html=True)

st.markdown(
    """<div style="background:linear-gradient(120deg,#163A5F,#287C83);color:white;padding:1.35rem 1.6rem;border-radius:18px;margin-bottom:1.25rem;box-shadow:0 8px 22px rgba(22,58,95,.18)">
    <h1 style="color:white;margin:0">3. Launch-timing decision</h1>
    <p style="margin:.35rem 0 0;color:#E6F4F3">Build awareness before the strongest seasonal demand arrives.</p>
    </div>""",
    unsafe_allow_html=True,
)
st.caption("Source: data/seasonality_and_weather.csv · Seasonal demand signal")

data = pd.read_csv("data/seasonality_and_weather.csv")
data["month_name"] = data["month"].map(lambda month: calendar.month_name[int(month)])

peak_row = data.loc[data["seasonality_index_100_avg"].idxmax()]
peak_month = int(peak_row["month"])
recommended_month = peak_month - 1 if peak_month > 1 else 12
acceptable_window = data[data["seasonality_index_100_avg"] >= 100]
window_start = int(acceptable_window["month"].min())
window_end = int(acceptable_window["month"].max())

month_labels = data["month_name"].tolist()
recommended_label = calendar.month_name[recommended_month]
window_start_label = calendar.month_name[window_start]
window_end_label = calendar.month_name[window_end]

st.markdown(
    "<h3 style='text-align: center;'>German demand seasonality and recommended launch timing</h3>",
    unsafe_allow_html=True,
)
st.caption(
    f"The green band covers the full acceptable demand window ({window_start_label}–{window_end_label}); "
    f"the red bar marks the recommended launch month ({recommended_label})."
)

fig = go.Figure()
fig.add_vrect(
    x0=window_start - 1.5,
    x1=window_end - 0.5,
    fillcolor="#D9F2E6",
    opacity=0.6,
    line_width=0,
)
fig.add_trace(
    go.Bar(
        x=month_labels,
        y=data["seasonality_index_100_avg"],
        marker_color=[
            "#E45756" if int(month) == recommended_month else "#4C78A8"
            for month in data["month"]
        ],
        hovertemplate="%{x}<br>Seasonality index: %{y}<extra></extra>",
    )
)
fig.add_hline(y=100, line_dash="dash", line_color="#555", annotation_text="Average demand")
fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Seasonality index (average = 100)",
    xaxis=dict(tickangle=-35, automargin=True),
    showlegend=False,
    height=560,
    margin=dict(t=45, r=45, b=95, l=65),
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Interpretation: the red bar is the recommended preparation month, one month before the demand peak. The dashed line marks average demand.")

st.markdown("### Key timing indicators")
st.markdown(
    f"""
    <style>
    .timing-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        max-width: 1100px;
        margin: 0 auto 1.5rem auto;
    }}
    .timing-kpi {{
        min-height: 125px;
        padding: 1rem 0.75rem;
        border-radius: 14px;
        text-align: center;
        color: #222831;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .timing-kpi-label {{ font-size: 0.9rem; font-weight: 600; margin-bottom: 0.45rem; }}
    .timing-kpi-value {{ font-size: 1.65rem; font-weight: 700; line-height: 1.15; }}
    .timing-kpi-peak {{ background: #DCEBFA; }}
    .timing-kpi-index {{ background: #E8E0F7; }}
    .timing-kpi-recommended {{ background: #FBE1DE; }}
    .timing-kpi-window {{ background: #D9F2E6; }}
    @media (max-width: 800px) {{
        .timing-kpi-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    </style>
    <div class="timing-kpi-grid">
        <div class="timing-kpi timing-kpi-peak">
            <div class="timing-kpi-label">Peak month</div>
            <div class="timing-kpi-value">{calendar.month_name[peak_month]}</div>
        </div>
        <div class="timing-kpi timing-kpi-index">
            <div class="timing-kpi-label">Peak index</div>
            <div class="timing-kpi-value">{int(peak_row["seasonality_index_100_avg"])}</div>
        </div>
        <div class="timing-kpi timing-kpi-recommended">
            <div class="timing-kpi-label">Recommended launch</div>
            <div class="timing-kpi-value">{recommended_label}</div>
        </div>
        <div class="timing-kpi timing-kpi-window">
            <div class="timing-kpi-label">Acceptable window</div>
            <div class="timing-kpi-value">{window_start_label}–{window_end_label}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Advice for the CEO and CFO")
st.info(
    f"**CEO:** prepare the launch for {recommended_label} to build momentum before the {calendar.month_name[peak_month]} peak. "
    f"**CFO:** use {window_start_label}–{window_end_label} as the planning window and release spend only when operations and inventory are ready."
)
