import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="LUMEN | Pricing", page_icon="💶", layout="wide")

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
        <h1>1. Pricing decision</h1>
        <p>Choose the price that balances customer adoption, contribution and competitive position.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

price_data = pd.read_csv("data/price_test_results.csv")
sensitivity = pd.read_csv("data/price_sensitivity_survey.csv")
channel_economics = pd.read_csv("data/channel_economics.csv")
competitor_data = pd.read_csv("data/competitor_prices_by_channel.csv")

price_names = {1.79: "Reach", 2.19: "Balanced", 2.59: "Premium"}
price_data["scenario"] = price_data["price_eur"].map(
    lambda price: f"{price_names.get(round(price, 2), 'Scenario')} · €{price:.2f}"
)
comparison = price_data.groupby(["price_eur", "scenario"], as_index=False).agg(
    acceptance=("estimated_acceptance_pct_of_survey", "first"),
    contribution=("unit_contribution_eur", "mean"),
    margin=("contribution_margin_pct", "mean"),
)

st.markdown("### Select your scenario")
price_options = sorted(price_data["price_eur"].unique())


def choose_price(price):
    st.session_state["pricing_selected_price"] = price
    for option in price_options:
        st.session_state[f"pricing_price_{option:.2f}"] = option == price


if "pricing_selected_price" not in st.session_state:
    st.session_state["pricing_selected_price"] = 2.19
for option in price_options:
    key = f"pricing_price_{option:.2f}"
    if key not in st.session_state:
        st.session_state[key] = option == st.session_state["pricing_selected_price"]

price_checkboxes = st.columns(len(price_options))
for column, option in zip(price_checkboxes, price_options):
    with column:
        st.checkbox(
            f"{price_names.get(round(option, 2), 'Scenario')} · €{option:.2f}",
            key=f"pricing_price_{option:.2f}",
            on_change=choose_price,
            args=(option,),
        )

selected_price = st.session_state["pricing_selected_price"]
st.info(
    "**How to use it**\n\n"
    "- Tick one price case to update the KPIs and price trade-off charts.\n"
    "- Choose a distribution channel to see its contribution at the selected price."
)
selected_channel = st.selectbox(
    "Distribution channel for the detailed view",
    sorted(channel_economics["channel"].unique()),
)
selected = comparison.loc[comparison["price_eur"] == selected_price].iloc[0]
selected_channel_row = price_data.loc[
    (price_data["channel"] == selected_channel)
    & (price_data["price_eur"] == selected_price)
].iloc[0]

def render_kpi(column, label, value, accent):
    with column:
        st.markdown(
            f'<div class="kpi-card" style="--accent:{accent}">'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )


kpis = st.columns(4)
render_kpi(kpis[0], "Tested acceptance", f"{selected['acceptance']:.1f}%", "#287C83")
render_kpi(kpis[1], "Avg. contribution", f"€{selected['contribution']:.2f}", "#4C78A8")
render_kpi(kpis[2], "Channel contribution", f"€{selected_channel_row['unit_contribution_eur']:.2f}", "#D97757")
render_kpi(kpis[3], "Contribution margin", f"{selected['margin']:.1f}%", "#8E6BBE")

st.markdown("### Price trade-off")
tradeoff = comparison.copy()
tradeoff["label"] = tradeoff.apply(
    lambda row: f"{price_names[row['price_eur']]} · €{row['price_eur']:.2f}", axis=1
)
tradeoff_fig = px.scatter(
    tradeoff,
    x="acceptance",
    y="contribution",
    text="label",
    size="margin",
    color="label",
    color_discrete_map={
        "Reach · €1.79": "#4C78A8",
        "Balanced · €2.19": "#287C83",
        "Premium · €2.59": "#D97757",
    },
    labels={
        "acceptance": "Tested acceptance (%)",
        "contribution": "Average contribution (€ / can)",
        "margin": "Contribution margin (%)",
        "label": "Scenario",
    },
)
tradeoff_fig.update_traces(textposition="top center", marker_line_color="white", marker_line_width=1)
tradeoff_fig.update_layout(height=430, margin=dict(t=25, r=25, b=60, l=60))
st.plotly_chart(tradeoff_fig, use_container_width=True)
st.caption(
    "Interpretation: €1.79 maximizes acceptance, €2.59 maximizes contribution, and €2.19 is the "
    "most balanced starting point."
)

st.markdown("### Customer price comfort")
sensitivity_prices = pd.concat(
    [
        pd.Series(range(100, 351), name="price_eur").div(100),
        pd.Series(comparison["price_eur"].unique(), name="price_eur"),
    ]
).drop_duplicates().sort_values()
sensitivity_curve = pd.DataFrame({"price_eur": sensitivity_prices})
sensitivity_curve["comfortable_share"] = sensitivity_curve["price_eur"].map(
    lambda price: (
        (sensitivity["cheap_eur"] <= price) & (sensitivity["expensive_eur"] >= price)
    ).mean()
    * 100
)
sensitivity_curve["price_label"] = sensitivity_curve["price_eur"].map(
    lambda price: f"€{price:.2f}"
)
sensitivity_fig = px.line(
    sensitivity_curve,
    x="price_eur",
    y="comfortable_share",
    labels={"price_eur": "Price (€)", "comfortable_share": "Survey comfort zone (%)"},
)
sensitivity_fig.update_traces(line_color="#287C83", line_width=4)
for price in sorted(comparison["price_eur"]):
    row = comparison.loc[comparison["price_eur"] == price].iloc[0]
    sensitivity_fig.add_scatter(
        x=[price],
        y=[sensitivity_curve.loc[sensitivity_curve["price_eur"] == price, "comfortable_share"].iloc[0]],
        mode="markers+text",
        text=[price_names[price]],
        textposition="top center",
        marker=dict(size=11, color="#D97757" if price == selected_price else "#163A5F"),
        showlegend=False,
    )
sensitivity_fig.update_layout(height=390, margin=dict(t=25, r=25, b=60, l=60))
st.plotly_chart(sensitivity_fig, use_container_width=True)
st.caption(
    "Interpretation: the curve estimates the share of respondents whose 'cheap' and 'expensive' "
    "thresholds contain each price. It is a comfort signal, not a demand forecast."
)

st.markdown("### Competitive price position")
competitors = competitor_data.loc[
    competitor_data["format"].eq("Single can (330ml)")
].copy()
competitors["brand"] = competitors["competitor"]
lumen_points = pd.DataFrame(
    {
        "brand": ["LUMEN"] * price_data["channel"].nunique(),
        "channel": sorted(price_data["channel"].unique()),
        "price_eur": [selected_price] * price_data["channel"].nunique(),
    }
)
competition = pd.concat(
    [competitors[["brand", "channel", "price_eur"]], lumen_points], ignore_index=True
)
competition_fig = px.bar(
    competition,
    x="channel",
    y="price_eur",
    color="brand",
    barmode="group",
    labels={"channel": "Distribution channel", "price_eur": "Price (€)", "brand": "Brand"},
    color_discrete_map={"LUMEN": "#D97757"},
)
competition_fig.update_layout(height=430, margin=dict(t=25, r=25, b=70, l=60))
st.plotly_chart(competition_fig, use_container_width=True)
st.caption(
    "Interpretation: use this comparison to decide whether LUMEN is entering as accessible premium "
    "or positioning clearly above the market."
)

st.markdown("### Advice for the CEO and CFO")
ceo, cfo = st.columns(2)
with ceo:
    st.markdown(
        '<div class="advice"><strong>CEO · positioning</strong><br>'
        "Use €2.19 as the launch reference: it keeps a premium signal while preserving more trial "
        "potential than €2.59.</div>",
        unsafe_allow_html=True,
    )
with cfo:
    st.markdown(
        '<div class="advice"><strong>CFO · decision gate</strong><br>'
        "Approve €2.19 as the base case, then scale only if observed conversion and repeat purchase "
        "support the contribution assumptions.</div>",
        unsafe_allow_html=True,
    )
