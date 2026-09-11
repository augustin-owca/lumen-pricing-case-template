import calendar

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="LUMEN | Timing", page_icon="📅", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f4f8fb 0%, #ffffff 34%); }
    h1, h2, h3 { color: #163A5F; }
    .hero {
        background: linear-gradient(120deg, #163A5F, #287C83);
        color: white; padding: 1.7rem 1.9rem; border-radius: 20px;
        margin-bottom: 1.2rem; box-shadow: 0 10px 26px rgba(22,58,95,.18);
    }
    .hero h1 { color: white; margin: 0; }
    .hero p { color: #E6F4F3; margin: .4rem 0 0; font-size: 1.05rem; }
    .kpi-card {
        background: white; border: 1px solid #dbe7ef; border-top: 5px solid var(--accent);
        border-radius: 12px; padding: .85rem .6rem; height: 112px; box-sizing: border-box;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; box-shadow: 0 3px 10px rgba(22,58,95,.08);
        overflow-wrap: anywhere;
    }
    .kpi-label { color: #5B6B7A; font-size: .76rem; font-weight: 700; text-transform: uppercase; }
    .kpi-value { color: #163A5F; font-size: 1.28rem; font-weight: 800; margin-top: .32rem; }
    .advice {
        background: #eef7f5; border-left: 5px solid #287C83; border-radius: 10px;
        padding: .85rem 1rem; min-height: 105px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>3. Launch timing decision</h1>
        <p>Build awareness before the strongest seasonal demand arrives.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Seasonal demand signal and competitor activity")

seasonality = pd.read_csv("data/seasonality_and_weather.csv")
competitor = pd.read_csv("data/competitor_price_history.csv", parse_dates=["month"])

peak_row = seasonality.loc[seasonality["seasonality_index_100_avg"].idxmax()]
peak_month = int(peak_row["month"])
lead_months = st.slider("Preparation lead time (months)", 1, 3, 1)
recommended_month = ((peak_month - lead_months - 1) % 12) + 1
recommended_label = calendar.month_name[recommended_month]
peak_label = calendar.month_name[peak_month]
acceptable = seasonality.loc[seasonality["seasonality_index_100_avg"] >= 100]
window_start = calendar.month_name[int(acceptable["month"].min())]
window_end = calendar.month_name[int(acceptable["month"].max())]

competitor_options = sorted(competitor["competitor"].unique())
st.info(
    "**How to use it**\n\n"
    "- Move the preparation slider from 1 to 3 months; the recommended launch month moves "
    "earlier as preparation time increases.\n"
    "- In the competitor section, select brands to filter the price and promotion chart."
)

def render_kpi(column, label, value, accent):
    with column:
        st.markdown(
            f'<div class="kpi-card" style="--accent:{accent}">'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )


kpis = st.columns(4)
render_kpi(kpis[0], "Demand peak", peak_label, "#287C83")
render_kpi(kpis[1], "Peak index", f"{peak_row['seasonality_index_100_avg']:.0f}", "#4C78A8")
render_kpi(kpis[2], "Recommended launch", recommended_label, "#D97757")
render_kpi(kpis[3], "Planning window", f"{window_start}–{window_end}", "#8E6BBE")

st.markdown("### Seasonal demand")
seasonality["month_name"] = seasonality["month"].map(lambda month: calendar.month_name[int(month)])
seasonality_fig = go.Figure()
seasonality_fig.add_trace(
    go.Bar(
        x=seasonality["month_name"],
        y=seasonality["seasonality_index_100_avg"],
        marker_color=[
            "#D97757" if int(month) == recommended_month else "#4C78A8"
            for month in seasonality["month"]
        ],
        hovertemplate="%{x}<br>Demand index: %{y}<extra></extra>",
    )
)
seasonality_fig.add_hline(
    y=100, line_dash="dash", line_color="#6B7280", annotation_text="Average demand"
)
seasonality_fig.update_layout(
    height=440,
    margin=dict(t=25, r=25, b=65, l=60),
    xaxis_title="Month",
    yaxis_title="Seasonality index",
    showlegend=False,
)
st.plotly_chart(seasonality_fig, use_container_width=True)
st.caption(
    f"Interpretation: launch in {recommended_label}, {lead_months} month(s) before the "
    f"{peak_label} peak, so awareness and distribution are ready when demand rises."
)

st.markdown("### Competitor price and promotion")
selected_competitors = st.multiselect(
    "Competitors to display",
    competitor_options,
    default=competitor_options,
)
if not selected_competitors:
    selected_competitors = competitor_options

competitor_view = competitor.loc[
    competitor["competitor"].isin(selected_competitors)
].copy()
competitor_fig = px.line(
    competitor_view,
    x="month",
    y="shelf_price_eur",
    color="competitor",
    markers=True,
    labels={"month": "Month", "shelf_price_eur": "Shelf price (€)", "competitor": "Competitor"},
    color_discrete_sequence=["#163A5F", "#287C83", "#D97757", "#8E6BBE"],
)
promo_view = competitor_view.loc[competitor_view["promo_active"]]
for _, row in promo_view.iterrows():
    competitor_fig.add_trace(
        go.Scatter(
            x=[row["month"]],
            y=[row["shelf_price_eur"]],
            mode="markers",
            marker=dict(size=12, color="#D97757", symbol="diamond"),
            name="Promotion",
            showlegend=False,
            hovertemplate=f"{row['competitor']}<br>Promotion<extra></extra>",
        )
    )
competitor_fig.update_layout(height=420, margin=dict(t=25, r=25, b=65, l=60))
st.plotly_chart(competitor_fig, use_container_width=True)
st.caption(
    "Interpretation: diamond markers indicate promotions. Avoid entering a crowded discount period "
    "unless LUMEN has a clear product or price advantage."
)

st.markdown("### Advice for the CEO and CFO")
ceo, cfo = st.columns(2)
with ceo:
    st.markdown(
        f'<div class="advice"><strong>CEO · launch momentum</strong><br>'
        f"Use {recommended_label} as the target launch month and build awareness ahead of the "
        f"{peak_label} demand peak.</div>",
        unsafe_allow_html=True,
    )
with cfo:
    st.markdown(
        f'<div class="advice"><strong>CFO · readiness gate</strong><br>'
        f"Keep the {window_start}–{window_end} period flexible, but release inventory and media "
        "spend only when operational readiness is confirmed.</div>",
        unsafe_allow_html=True,
    )
