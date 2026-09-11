import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="LUMEN | Channels", page_icon="📣", layout="wide")

st.markdown("""<style>
.stApp { background: linear-gradient(180deg, #f4f8fb 0%, #ffffff 28%); }
h1 { color: #163A5F; }
div[data-testid="stMetric"] { background: #ffffff; border: 1px solid #dbe7ef; padding: 0.8rem; border-radius: 12px; box-shadow: 0 3px 10px rgba(22,58,95,.08); }
</style>""", unsafe_allow_html=True)

st.markdown(
    """<div style="background:linear-gradient(120deg,#163A5F,#287C83);color:white;padding:1.35rem 1.6rem;border-radius:18px;margin-bottom:1.25rem;box-shadow:0 8px 22px rgba(22,58,95,.18)">
    <h1 style="color:white;margin:0">2. Channel decision</h1>
    <p style="margin:.35rem 0 0;color:#E6F4F3">Choose the route that protects contribution and supports the launch.</p>
    </div>""",
    unsafe_allow_html=True,
)
st.caption("Source: data/channel_economics.csv · Unit economics only")

data = pd.read_csv("data/channel_economics.csv")
data["price_label"] = data["illustrative_retail_price_eur"].map(lambda price: f"€{price:.2f}")

pivot = data.pivot(
    index="channel",
    columns="illustrative_retail_price_eur",
    values="unit_contribution_eur",
)
best_row = data.loc[data["unit_contribution_eur"].idxmax()]
best_channel = best_row["channel"]
best_price = best_row["illustrative_retail_price_eur"]
best_contribution = best_row["unit_contribution_eur"]

st.markdown(
    "<h3 style='text-align: center;'>Unit contribution by channel and price</h3>",
    unsafe_allow_html=True,
)
st.caption(
    "Unit contribution is the amount LUMEN keeps per unit after the channel deductions "
    "included in this dataset."
)

fig = px.bar(
    data,
    x="channel",
    y="unit_contribution_eur",
    color="price_label",
    barmode="group",
    text_auto=".2f",
    labels={
        "channel": "Distribution channel",
        "unit_contribution_eur": "Unit contribution (€)",
        "price_label": "Retail price",
    },
    color_discrete_sequence=["#4C78A8", "#E45756"],
)
fig.update_layout(
    height=500,
    margin=dict(t=35, r=35, b=80, l=65),
    legend_title_text="Retail price",
)
fig.update_traces(
    hovertemplate="%{x}<br>Contribution: €%{y:.2f}<extra></extra>"
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Interpretation: the taller bar shows the channel/price combination that leaves more value with LUMEN per unit. This is a unit-economics view, not a volume forecast.")

st.markdown("### Key channel indicators")
st.markdown(
    f"""
    <style>
    .channel-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        max-width: 950px;
        margin: 0 auto 1.5rem auto;
    }}
    .channel-kpi {{
        min-height: 120px;
        padding: 1rem 0.75rem;
        border-radius: 14px;
        text-align: center;
        color: #222831;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .channel-kpi-label {{ font-size: 0.9rem; font-weight: 600; margin-bottom: 0.45rem; }}
    .channel-kpi-value {{ font-size: 1.5rem; font-weight: 700; line-height: 1.15; }}
    .channel-kpi-best {{ background: #D9F2E6; }}
    .channel-kpi-contribution {{ background: #DCEBFA; }}
    .channel-kpi-channels {{ background: #E8E0F7; }}
    @media (max-width: 800px) {{
        .channel-kpi-grid {{ grid-template-columns: 1fr; }}
    }}
    </style>
    <div class="channel-kpi-grid">
        <div class="channel-kpi channel-kpi-best">
            <div class="channel-kpi-label">Highest contribution</div>
            <div class="channel-kpi-value">{best_channel}</div>
        </div>
        <div class="channel-kpi channel-kpi-contribution">
            <div class="channel-kpi-label">Contribution at €{best_price:.2f}</div>
            <div class="channel-kpi-value">€{best_contribution:.2f} / unit</div>
        </div>
        <div class="channel-kpi channel-kpi-channels">
            <div class="channel-kpi-label">Channels compared</div>
            <div class="channel-kpi-value">{data["channel"].nunique()}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Simple takeaway")
st.write(
    f"At the prices shown, **{best_channel} at €{best_price:.2f}** produces the highest "
    f"unit contribution (€{best_contribution:.2f}). This is a contribution comparison only: "
    "it does not measure reach, customer acquisition or total market potential."
)

st.markdown("### Advice for the CEO and CFO")
st.info(
    "**CEO:** use DTC Online at €2.19 as the clearest value-and-margin proposition. "
    "**CFO:** treat €1.16 per unit as the best observed contribution in this file, but confirm "
    "volumes and channel costs before committing budget."
)
