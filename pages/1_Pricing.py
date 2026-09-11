import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="LUMEN | Pricing", page_icon="💶", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f4f8fb 0%, #ffffff 32%); }
    h1, h2, h3 { color: #163A5F; }
    .hero {
        background: linear-gradient(120deg, #163A5F, #287C83);
        color: white; padding: 1.35rem 1.6rem; border-radius: 18px;
        margin-bottom: 1.25rem; box-shadow: 0 8px 22px rgba(22,58,95,.18);
    }
    .hero h1 { color: white; margin: 0; }
    .hero p { margin: .35rem 0 0; color: #E6F4F3; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #dbe7ef; padding: .8rem;
        border-radius: 12px; box-shadow: 0 3px 10px rgba(22,58,95,.08);
    }
    .advice {
        background: #eef7f5; border-left: 5px solid #287C83; border-radius: 10px;
        padding: .85rem 1rem; margin-top: .5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>1. Pricing decision</h1>
        <p>Find the price that protects acceptance today and contribution tomorrow.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

price_data = pd.read_csv("data/price_test_results.csv")
competitor_data = pd.read_csv("data/competitor_prices_by_channel.csv")
price_names = {1.79: "Reach", 2.19: "Balanced", 2.59: "Premium"}
price_data["scenario"] = price_data["price_eur"].map(
    lambda price: f"{price_names[price]} · €{price:.2f}"
)

comparison = price_data.groupby(["price_eur", "scenario"], as_index=False).agg(
    acceptance=("estimated_acceptance_pct_of_survey", "first"),
    contribution=("unit_contribution_eur", "mean"),
    margin=("contribution_margin_pct", "mean"),
)
recommended_price = 2.19
recommended = comparison.loc[comparison["price_eur"] == recommended_price].iloc[0]

st.success(
    f"**Base-case recommendation: €{recommended_price:.2f} ({price_names[recommended_price]})** · "
    f"{recommended['acceptance']:.1f}% tested acceptance and €{recommended['contribution']:.2f} "
    "average contribution per can."
)

st.markdown("### Selected scenario")
st.caption("Change the scenario to see the commercial and financial implications.")
selected_price = st.radio(
    "Retail price per 330ml can",
    sorted(price_data["price_eur"].unique()),
    index=1,
    horizontal=True,
    format_func=lambda price: f"{price_names[price]} · €{price:.2f}",
)
selected = comparison.loc[comparison["price_eur"] == selected_price].iloc[0]

kpis = st.columns(3)
kpis[0].metric("Tested acceptance", f"{selected['acceptance']:.1f}%")
kpis[1].metric("Avg. contribution / can", f"€{selected['contribution']:.2f}")
kpis[2].metric("Avg. contribution margin", f"{selected['margin']:.1f}%")

st.markdown("### Price trade-off")
st.caption(
    "Each point is one tested price. The ideal direction is up and right: higher contribution "
    "with higher acceptance."
)
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
        "label": "Price scenario",
    },
)
tradeoff_fig.update_traces(textposition="top center", marker_line_color="white", marker_line_width=1)
tradeoff_fig.update_layout(
    height=430, margin=dict(t=25, r=25, b=60, l=60), legend_title_text="Scenario"
)
st.plotly_chart(tradeoff_fig, use_container_width=True)
st.caption(
    "Interpretation: €1.79 maximizes acceptance, while €2.59 maximizes contribution. "
    "€2.19 is the practical middle ground for a first launch test."
)

st.markdown("### Contribution by channel")
channel_data = price_data.pivot(
    index="channel", columns="price_eur", values="unit_contribution_eur"
).reset_index().melt(id_vars="channel", var_name="price_eur", value_name="contribution")
channel_data["price"] = channel_data["price_eur"].map(lambda price: f"€{price:.2f}")
channel_fig = px.bar(
    channel_data,
    x="channel",
    y="contribution",
    color="price",
    barmode="group",
    text_auto=".2f",
    labels={
        "channel": "Distribution channel",
        "contribution": "Contribution (€ / can)",
        "price": "Retail price",
    },
    color_discrete_sequence=["#A9C4D4", "#287C83", "#D97757"],
)
channel_fig.update_layout(height=430, margin=dict(t=25, r=25, b=70, l=60))
st.plotly_chart(channel_fig, use_container_width=True)
st.caption(
    "Interpretation: DTC Online produces the highest contribution at each tested price; "
    "the channel choice still requires a separate volume and acquisition analysis."
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
    "Interpretation: use this chart to check whether the selected LUMEN price is accessible, "
    "market-aligned or clearly premium versus single-can competitors."
)

st.markdown("### Advice for the CEO and CFO")
advice_left, advice_right = st.columns(2)
with advice_left:
    st.markdown("**CEO · position and launch**")
    st.markdown(
        '<div class="advice">Start with <strong>€2.19</strong>: it signals quality without '
        "cutting off as much trial as €2.59. Keep €1.79 as a controlled introductory test.</div>",
        unsafe_allow_html=True,
    )
with advice_right:
    st.markdown("**CFO · economics and risk**")
    st.markdown(
        '<div class="advice">Use €2.19 as the base case, but approve scale only after observed '
        "conversion, repeat purchase and channel costs confirm the contribution assumption.</div>",
        unsafe_allow_html=True,
    )

