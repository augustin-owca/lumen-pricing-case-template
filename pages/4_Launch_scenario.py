import calendar
import math

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="LUMEN | Launch scenario", page_icon="🚀", layout="wide")

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
        <h1>4. Launch scenario</h1>
        <p>Turn a few launch assumptions into a simple CFO/CEO planning view.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

price_tests = pd.read_csv("data/price_test_results.csv")
funnel = pd.read_csv("data/marketing_funnel_monthly.csv")
seasonality = pd.read_csv("data/seasonality_and_weather.csv")

funnel["ltv_value_eur"] = funnel["ltv_estimate_eur"] * funnel["conversions_customers_acquired"]
funnel_summary = funnel.groupby("channel").agg(
    customers=("conversions_customers_acquired", "sum"),
    spend_eur=("spend_eur", "sum"),
    ltv_value_eur=("ltv_value_eur", "sum"),
)
funnel_summary["cac_eur"] = funnel_summary["spend_eur"] / funnel_summary["customers"]
funnel_summary["ltv_eur"] = funnel_summary["ltv_value_eur"] / funnel_summary["customers"]
funnel_summary["ltv_cac_ratio"] = funnel_summary["ltv_eur"] / funnel_summary["cac_eur"]

price_summary = price_tests.groupby("price_eur", as_index=False).agg(
    acceptance=("estimated_acceptance_pct_of_survey", "first"),
    unit_contribution_eur=("unit_contribution_eur", "mean"),
    margin=("contribution_margin_pct", "mean"),
)
price_options = sorted(price_summary["price_eur"].unique())
marketing_channels = sorted(funnel_summary.index.tolist())
best_channels = funnel_summary["ltv_cac_ratio"].sort_values(ascending=False).head(2).index.tolist()
month_options = [calendar.month_name[month] for month in range(1, 13)]

st.markdown("### Set your launch assumptions")
selected_price = st.selectbox(
    "1. Launch price (€ / can)",
    price_options,
    index=price_options.index(2.19) if 2.19 in price_options else 0,
    format_func=lambda price: f"€{price:.2f}",
)
marketing_budget = st.slider(
    "2. Marketing budget (€)",
    min_value=5_000,
    max_value=100_000,
    value=30_000,
    step=5_000,
    format="€%d",
)
selected_channels = st.multiselect(
    "3. Marketing channel mix",
    marketing_channels,
    default=best_channels,
)
selected_month = st.selectbox("4. Launch month", month_options, index=3)

with st.expander("How is the outcome calculated?", expanded=False):
    st.markdown(
        """
        - **Estimated customers:** the budget is split equally across the selected channels. For each channel, allocated budget ÷ historical CAC gives expected customers; the result is then adjusted by the selected month's seasonality index.
        - **Launch revenue:** estimated customers × selected price, assuming one can is bought in the first purchase.
        - **Blended CAC:** total marketing budget ÷ estimated customers.
        - **CAC payback:** blended CAC ÷ monthly LTV, where monthly LTV is estimated LTV ÷ 12 months.
        - **Marketing break-even volume:** marketing budget ÷ average unit contribution. This is the number of cans needed to recover marketing spend only.

        """
    )

if not selected_channels:
    selected_channels = [best_channels[0]]
    st.warning(f"No channel selected, so the model is using {best_channels[0]} as a fallback.")

price_row = price_summary.loc[price_summary["price_eur"] == selected_price].iloc[0]
seasonality["month_name"] = seasonality["month"].map(lambda month: calendar.month_name[int(month)])
seasonality_row = seasonality.loc[seasonality["month_name"] == selected_month].iloc[0]
seasonality_factor = seasonality_row["seasonality_index_100_avg"] / 100

budget_per_channel = marketing_budget / len(selected_channels)
mix = funnel_summary.loc[selected_channels].copy()
mix["allocated_budget_eur"] = budget_per_channel
mix["estimated_customers"] = budget_per_channel / mix["cac_eur"] * seasonality_factor
estimated_customers = mix["estimated_customers"].sum()
blended_cac = marketing_budget / estimated_customers if estimated_customers else 0
average_ltv = (
    (mix["ltv_eur"] * mix["estimated_customers"]).sum() / estimated_customers
    if estimated_customers
    else 0
)
payback_months = blended_cac / (average_ltv / 12) if average_ltv else math.inf
revenue = estimated_customers * selected_price
break_even_units = math.ceil(marketing_budget / price_row["unit_contribution_eur"])


def render_kpi(column, label, value, accent):
    with column:
        st.markdown(
            f'<div class="kpi-card" style="--accent:{accent}">'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )


st.markdown("### Scenario output")
first_row = st.columns(3)
render_kpi(first_row[0], "Estimated customers", f"{estimated_customers:,.0f}", "#287C83")
render_kpi(first_row[1], "Launch revenue", f"€{revenue:,.0f}", "#4C78A8")
render_kpi(first_row[2], "CAC payback", f"{payback_months:.1f} months", "#8E6BBE")

second_row = st.columns(2)
render_kpi(second_row[0], "Blended CAC", f"€{blended_cac:.2f}", "#163A5F")
render_kpi(second_row[1], "Marketing break-even volume", f"{break_even_units:,.0f} cans", "#6B7280")

st.markdown("### Estimated customers by selected channel")
mix_view = mix.reset_index().rename(columns={"channel": "Marketing channel"})
mix_fig = px.bar(
    mix_view,
    x="estimated_customers",
    y="Marketing channel",
    orientation="h",
    text_auto=",.0f",
    color="Marketing channel",
    color_discrete_sequence=["#287C83", "#4C78A8", "#D97757", "#8E6BBE"],
    labels={"estimated_customers": "Estimated customers", "Marketing channel": ""},
)
mix_fig.update_layout(height=350, margin=dict(t=20, r=25, b=55, l=25), showlegend=False)
st.plotly_chart(mix_fig, use_container_width=True)
st.caption(
    "Interpretation: the largest bar is the channel expected to generate the most customers under "
    "the selected equal-budget split and launch-month seasonality."
)

st.markdown("### What the model assumes")
st.caption(
    "The simulation uses historical channel CAC and LTV, equal budget allocation across the selected mix, "
    "average contribution across distribution channels, one first purchase per acquired customer, and a "
    "12-month interpretation of LTV for the payback proxy. Break-even volume recovers marketing spend only; "
    "it excludes fixed overhead and working-capital costs."
)

st.markdown("### Advice for the CEO and CFO")
ceo, cfo = st.columns(2)
with ceo:
    st.markdown(
        f'<div class="advice"><strong>CEO · launch design</strong><br>'
        f"Use {selected_month} as the working launch month and keep the mix focused on the selected "
        "channels until the first German test shows where demand is strongest.</div>",
        unsafe_allow_html=True,
    )
with cfo:
    finance_signal = (
        f"Use {break_even_units:,.0f} cans as the minimum marketing break-even volume and track actual CAC "
        f"against the €{blended_cac:.2f} planning benchmark before scaling."
    )
    st.markdown(
        f'<div class="advice"><strong>CFO · investment gate</strong><br>{finance_signal}</div>',
        unsafe_allow_html=True,
    )
