import streamlit as st


st.set_page_config(page_title="LUMEN | Germany launch", page_icon="🥤", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f4f8fb 0%, #ffffff 36%); }
    .hero {
        background: linear-gradient(120deg, #163A5F, #287C83);
        color: white; padding: 2rem 2.1rem; border-radius: 20px;
        margin-bottom: 1.25rem; box-shadow: 0 10px 26px rgba(22,58,95,.18);
    }
    .hero h1 { color: white; margin: 0; font-size: 2.5rem; }
    .hero p { color: #E6F4F3; font-size: 1.1rem; margin: .45rem 0 0; }
    .context {
        background: white; border: 1px solid #dbe7ef; border-radius: 14px;
        padding: 1rem 1.2rem; box-shadow: 0 3px 10px rgba(22,58,95,.06);
    }
    .decision-card {
        background: #ffffff; border-top: 5px solid #287C83; border-radius: 12px;
        padding: 1rem 1.1rem; min-height: 130px;
        box-shadow: 0 3px 10px rgba(22,58,95,.08);
    }
    .decision-card h3 { margin-top: 0; color: #163A5F; }
    .step { color: #287C83; font-weight: 700; letter-spacing: .04em; font-size: .8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>LUMEN · Germany launch dashboard</h1>
        <p>A decision-support tool for the CFO and CEO to prepare the Germany launch.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="context">
        <strong>What this tool does</strong><br>
        LUMEN is preparing to enter Germany with a functional beverage. This dashboard helps the
        CFO and CEO compare the key launch trade-offs—adoption, contribution, channel efficiency
        and timing—so they can make a focused decision before committing resources.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Explore the three decisions")
price, channel, timing = st.columns(3)
with price:
    st.markdown(
        """
        <div class="decision-card">
            <div class="step">01 · PRICING</div>
            <h3>What should we charge?</h3>
            Compare tested price points, customer comfort, contribution and competitive position.
            Use the result to set a launch price and a decision gate for the first market test.
        </div>
        """,
        unsafe_allow_html=True,
    )
with channel:
    st.markdown(
        """
        <div class="decision-card">
            <div class="step">02 · CHANNELS</div>
            <h3>Where should we sell?</h3>
            Compare distribution contribution, marketing efficiency and evidence from existing
            markets to prioritize where launch effort should go.
        </div>
        """,
        unsafe_allow_html=True,
    )
with timing:
    st.markdown(
        """
        <div class="decision-card">
            <div class="step">03 · TIMING</div>
            <h3>When should we launch?</h3>
            Use seasonal demand and competitor promotions to choose a launch window and prepare
            inventory, awareness and spend at the right time.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Build a launch scenario")
st.info(
    "The Launch scenario page lets you choose a price, marketing budget, channel mix and launch month. "
    "It combines the case data into directional estimates for customers, revenue, contribution, CAC payback "
    "and marketing break-even volume—useful for comparing plans before committing resources."
)
st.page_link("pages/4_Launch_scenario.py", label="Open Launch scenario", icon="🚀")

st.markdown("### How to use this dashboard")
st.info(
    "Start with Pricing, then check Channels and Timing. Each page ends with a short "
    "CEO/CFO recommendation and clearly separates evidence from assumptions."
)

st.caption(
    "Case workspace · The results are decision support, not a substitute for a German market test."
)
