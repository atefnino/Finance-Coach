import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from openai import OpenAI

st.set_page_config(page_title="Grok Finance Coach", page_icon="💰", layout="wide")
st.title("💰 AI Personal Finance Coach")
st.markdown("Upload transactions • Receive Grok-powered insights • Track goals • Get market updates")

# --- API Setup ---
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("xAI API Key", type="password", value=os.getenv("XAI_API_KEY", ""))
    if api_key:
        os.environ["XAI_API_KEY"] = api_key
    model = st.selectbox("Grok Model", ["grok-4-1-fast-reasoning", "grok-4"], index=0)
    st.caption("Recommended: grok-4-1-fast-reasoning ($0.20/$0.50 per million tokens)")

# --- Data Upload & Dashboard ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧠 Grok Analysis", "📈 Market Insights"])

with tab1:
    uploaded_file = st.file_uploader("Upload your transactions CSV (columns: Date, Description, Amount, Category optional)", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        if "Amount" in df.columns:
            df["Type"] = df["Amount"].apply(lambda x: "Income" if x > 0 else "Expense")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Income", f"${df[df['Amount'] > 0]['Amount'].sum():,.0f}")
        col2.metric("Total Expenses", f"${abs(df[df['Amount'] < 0]['Amount'].sum()):,.0f}")
        col3.metric("Net Balance", f"${df['Amount'].sum():,.0f}")
        col4.metric("Transactions", len(df))
        
        st.subheader("Spending by Category")
        if "Category" in df.columns:
            fig_pie = px.pie(df[df["Amount"] < 0], names="Category", values="Amount", title="Expense Breakdown")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("Cash Flow Over Time")
        df_time = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum().reset_index()
        df_time["Date"] = df_time["Date"].dt.to_timestamp()
        fig_line = px.line(df_time, x="Date", y="Amount", title="Monthly Cash Flow")
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.dataframe(df, use_container_width=True)

# --- Grok Analysis ---
with tab2:
    if uploaded_file and api_key:
        if st.button("Generate Personalized Grok Analysis", type="primary"):
            with st.spinner("Grok is analyzing your finances..."):
                client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
                
                # Prepare data summary
                summary = f"""
                Date range: {df['Date'].min().date()} to {df['Date'].max().date()}
                Total Income: ${df[df['Amount'] > 0]['Amount'].sum():,.0f}
                Total Expenses: ${abs(df[df['Amount'] < 0]['Amount'].sum()):,.0f}
                Net: ${df['Amount'].sum():,.0f}
                Top categories: {df[df['Amount'] < 0].groupby('Category')['Amount'].sum().nlargest(3).to_dict() if 'Category' in df.columns else 'N/A'}
                """
                
                response = client.responses.create(
                    model=model,
                    input=[
                        {"role": "system", "content": "You are an expert financial advisor. Provide clear, actionable, non-legal advice. Always include budgeting tips, risk warnings, and savings recommendations."},
                        {"role": "user", "content": f"Analyze this user's transaction data and give personalized advice:\n\n{summary}\n\nUser goal (optional): {st.text_area('Add your financial goal (e.g., save $5000 for vacation)', '')}"}
                    ]
                )
                st.success("Grok Analysis Complete")
                st.markdown(response.output_text)
		st.session_state.analysis_count += 1

    else:
        st.info("Upload a CSV and enter your API key to unlock Grok analysis.")

# --- Market Insights ---
with tab3:
    if api_key and st.button("Get Current Market & Investment Insights"):
        with st.spinner("Fetching real-time insights via Grok..."):
            client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
            market_prompt = "Provide a concise 2026 market summary (stocks, interest rates, crypto) and 3 personalized investment tips for an average individual based on general economic conditions."
            response = client.responses.create(
                model=model,
                input=[{"role": "user", "content": market_prompt}]
            )
            st.markdown(response.output_text)

# --- Monetization & Premium Upgrade (Lemon Squeezy) ---
st.divider()
st.subheader("Monetization & Premium")
st.caption("Free tier: 5 analyses per session • Premium unlocks unlimited usage")

if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0

if st.session_state.analysis_count >= 5:
    st.warning("You have reached the free limit for this session.")
    if st.button("🚀 Upgrade to Premium – $4.99/month", type="primary"):
        st.link_button("Open Premium Checkout", "https://ninofinance.lemonsqueezy.com/checkout/buy/c3c22bf3-e4f1-4859-ba73-0d377db7ff38")
else:
    st.info(f"Analyses used this session: {st.session_state.analysis_count}/5")

# Inside the Grok Analysis tab, AFTER successful response, add this line:
# st.session_state.analysis_count += 1
# Stripe quick-start snippet (add later)
st.code("""
import stripe
stripe.api_key = "sk_..."  # Your secret key
# Create checkout session and redirect user (full code provided in next message if requested)
""", language="python")
