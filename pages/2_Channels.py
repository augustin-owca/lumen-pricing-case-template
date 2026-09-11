import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="LUMEN | Channels", page_icon="📣", layout="wide")

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
    div[data-testid="stCheckbox"] { display: flex; justify-content: center; }
    div[data-testid="stCheckbox"] label { margin: 0 auto; }
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
        <h1>2. Channel decision</h1>
        <p>Separate the economics of selling from the efficiency of creating demand.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Distribution economics, marketing efficiency and home-market evidence")

economics = pd.read_csv("data/channel_economics.csv")
funnel = pd.read_csv("data/marketing_funnel_monthly.csv")
sales = pd.read_csv("data/historical_sales_weekly.csv", parse_dates=["week_start_date"])

price_options = sorted(economics["illustrative_retail_price_eur"].unique())


def choose_channel_price(price):
    st.session_state["channels_selected_price"] = price
    for option in price_options:
        st.session_state[f"channels_price_{option:.2f}"] = option == price


default_price = 2.19 if 2.19 in price_options else price_options[-1]
if "channels_selected_price" not in st.session_state:
    st.session_state["channels_selected_price"] = default_price
for option in price_options:
    key = f"channels_price_{option:.2f}"
    if key not in st.session_state:
        st.session_state[key] = option == st.session_state["channels_selected_price"]

st.markdown("**Select price view**")
price_checkboxes = st.columns(len(price_options))
for column, option in zip(price_checkboxes, price_options):
    with column:
        st.checkbox(
            f"Price view · €{option:.2f}",
            key=f"channels_price_{option:.2f}",
            on_change=choose_channel_price,
            args=(option,),
        )

selected_price = st.session_state["channels_selected_price"]
st.info(
    "**How to use it**\n\n"
    "- Tick one price view to update the distribution contribution chart.\n"
    "- In Part 3, choose a country to filter historical sales; the marketing-efficiency chart "
    "stays based on the funnel dataset."
)

selected_economics = economics.loc[
    economics["illustrative_retail_price_eur"] == selected_price
].sort_values("unit_contribution_eur", ascending=False)
top_distribution = selected_economics.iloc[0]

funnel["conversion_rate"] = funnel["conversions_customers_acquired"] / funnel["reach"]
funnel["ltv_value_eur"] = funnel["ltv_estimate_eur"] * funnel["conversions_customers_acquired"]
funnel_summary = funnel.groupby("channel").agg(
    reach=("reach", "sum"),
    customers=("conversions_customers_acquired", "sum"),
    spend_eur=("spend_eur", "sum"),
    ltv_value_eur=("ltv_value_eur", "sum"),
)
funnel_summary["cac_eur"] = funnel_summary["spend_eur"] / funnel_summary["customers"]
funnel_summary["ltv_eur"] = funnel_summary["ltv_value_eur"] / funnel_summary["customers"]
funnel_summary["ltv_cac_ratio"] = funnel_summary["ltv_eur"] / funnel_summary["cac_eur"]
top_acquisition = funnel_summary["ltv_cac_ratio"].idxmax()

def render_kpi(column, label, value, accent):
    with column:
        st.markdown(
            f'<div class="kpi-card" style="--accent:{accent}">'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )


kpis = st.columns(4)
render_kpi(kpis[0], "Best unit contribution", f"€{top_distribution['unit_contribution_eur']:.2f}", "#287C83")
render_kpi(kpis[1], "Best distribution channel", top_distribution["channel"], "#4C78A8")
render_kpi(kpis[2], "Best LTV:CAC channel", top_acquisition, "#D97757")
render_kpi(kpis[3], "Historical markets", f"{sales['country'].nunique()}", "#8E6BBE")

st.markdown("### 1 · Distribution economics")
economics_fig = px.bar(
    selected_economics,
    x="unit_contribution_eur",
    y="channel",
    orientation="h",
    text_auto=".2f",
    color="channel",
    color_discrete_sequence=["#287C83", "#4C78A8", "#A9C4D4"],
    labels={"unit_contribution_eur": "Contribution (€ / unit)", "channel": ""},
)
economics_fig.update_layout(
    height=350, margin=dict(t=20, r=25, b=55, l=25), showlegend=False
)
st.plotly_chart(economics_fig, use_container_width=True)
st.caption(
    "Interpretation: at the selected price, the longest bar gives LUMEN the most contribution "
    "per unit. It does not tell us which channel will sell the most."
)

st.markdown("### 2 · Marketing efficiency")
efficiency = funnel_summary.reset_index()
efficiency_fig = px.scatter(
    efficiency,
    x="cac_eur",
    y="ltv_cac_ratio",
    size="customers",
    text="channel",
    color_discrete_sequence=["#287C83"],
    labels={
        "cac_eur": "CAC (€) · lower is better",
        "ltv_cac_ratio": "LTV:CAC · higher is better",
        "customers": "Customers acquired",
    },
)
efficiency_fig.update_traces(textposition="top center", marker_line_color="white", marker_line_width=1)
efficiency_fig.update_layout(height=400, margin=dict(t=20, r=25, b=55, l=60), showlegend=False)
st.plotly_chart(efficiency_fig, use_container_width=True)
st.caption(
    "Interpretation: the strongest acquisition channel sits toward the top-left—high customer "
    "value with lower acquisition cost. Bubble size adds the scale context."
)

st.markdown("### 3 · Existing-market sales reference")
selected_country = st.selectbox(
    "Country for the historical-sales view",
    ["All markets"] + sorted(sales["country"].unique()),
)
sales_view = sales if selected_country == "All markets" else sales.loc[sales["country"] == selected_country]
sales_view = sales_view.groupby(["week_start_date", "channel"], as_index=False)["units_sold"].sum()
sales_fig = px.line(
    sales_view,
    x="week_start_date",
    y="units_sold",
    color="channel",
    markers=True,
    labels={"week_start_date": "Week", "units_sold": "Units sold", "channel": "Channel"},
    color_discrete_sequence=["#163A5F", "#287C83", "#D97757"],
)
sales_fig.update_layout(height=380, margin=dict(t=20, r=25, b=55, l=60))
st.plotly_chart(sales_fig, use_container_width=True)
st.caption(
    "Interpretation: this is evidence from the Netherlands, Denmark and Sweden—not Germany. "
    "Use it to understand execution patterns, not as a direct German forecast."
)

st.markdown("### Advice for the CEO and CFO")
ceo, cfo = st.columns(2)
with ceo:
    st.markdown(
        '<div class="advice"><strong>CEO · channel choice</strong><br>'
        "Use the economics and marketing views together: choose a channel that protects the brand "
        "experience while still reaching enough customers.</div>",
        unsafe_allow_html=True,
    )
with cfo:
    st.markdown(
        '<div class="advice"><strong>CFO · investment gate</strong><br>'
        "Start with the acquisition channels closest to the top-left of the efficiency chart, "
        "then validate volume before committing to physical distribution.</div>",
        unsafe_allow_html=True,
    )
