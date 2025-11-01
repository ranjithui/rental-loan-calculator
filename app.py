import streamlit as st
import numpy as np
import pandas as pd
import requests

# ===============================
# Function: Loan Clearance Model
# ===============================
def loan_clearance_schedule(property_value, down_payment_pct, interest_rate, tenure_years, rental_roi):
    down_payment = (down_payment_pct / 100) * property_value
    loan_amount = property_value - down_payment
    monthly_interest_rate = (interest_rate / 100) / 12
    tenure_months = tenure_years * 12

    emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure_months / ((1 + monthly_interest_rate) ** tenure_months - 1)
    annual_rental_income = (rental_roi / 100) * property_value
    monthly_rent = annual_rental_income / 12

    outstanding = loan_amount
    month = 0
    total_interest = 0
    schedule = []

    while outstanding > 0 and month < tenure_months * 2:
        month += 1
        interest = outstanding * monthly_interest_rate
        total_interest += interest
        principal = emi - interest
        outstanding -= principal
        surplus = monthly_rent - emi
        if surplus > 0:
            outstanding -= surplus
        outstanding = max(outstanding, 0)

        if month % 12 == 0:
            schedule.append({
                "Year": month // 12,
                "Remaining Balance": outstanding,
                "Annual Rental Yield": annual_rental_income
            })

        if outstanding <= 0:
            break

    years_taken = month / 12
    df_schedule = pd.DataFrame(schedule)

    return loan_amount, round(emi, 2), round(monthly_rent, 2), round(years_taken, 2), annual_rental_income, total_interest, df_schedule

# ===============================
# Property Segments Data
# ===============================
property_segments = {
    "Studio / Entry‑level Apartment": {"price_usd": 137500, "roi": 9},
    "1‑Bedroom Apartment": {"price_usd": 205000, "roi": 7.75},
    "2‑Bedroom Apartment": {"price_usd": 297500, "roi": 7},
    "Townhouse / Mid‑segment Villa": {"price_usd": 1020000, "roi": 5},
    "Premium / Luxury Villa": {"price_usd": 2000000, "roi": 5}
}

# ===============================
# Get live currency conversion rates (USD base)
# ===============================
def get_conversion_rates():
    # Example: using an open API or fixed rates for demo
    # For a real‑app you might use a reliable API from e.g. XE, OpenExchangeRates, etc.
    # Here we will define some sample rates:
    return {
        "USD": 1.0,
        "INR": 88.0,   # e.g. 1 USD = 88 INR (approx) :contentReference[oaicite:0]{index=0}
        "EUR": 0.86,   # 1 USD = 0.86 EUR :contentReference[oaicite:1]{index=1}
        "GBP": 0.74,   # 1 USD = 0.74 GBP :contentReference[oaicite:2]{index=2}
        "AUD": 1.50   # example rate for AUD
    }

conversion_rates = get_conversion_rates()

# ===============================
# Streamlit UI
# ===============================
st.set_page_config(page_title="Global Rental Loan Clearance Calculator", page_icon="🏢", layout="centered")
st.title("🏢 Global Rental Income Loan Clearance Calculator")

st.markdown("""
Welcome! Use this calculator to estimate **loan clearance with rental income** for property segments.
You can also explore average prices, typical ROI and check **multi‑currency price conversions** for each segment.
""")

# --- Currency selector for calculation ---
currency_map = {
    "INR (₹)": "INR",
    "USD ($)": "USD",
    "GBP (£)": "GBP",
    "EUR (€)": "EUR",
    "AUD (A$)": "AUD"
}
currency_choice_label = st.selectbox("Select Currency for Calculation", list(currency_map.keys()))
calc_currency = currency_map[currency_choice_label]
currency_symbol_map = {
    "INR": "₹",
    "USD": "$",
    "GBP": "£",
    "EUR": "€",
    "AUD": "A$"
}
currency_symbol = currency_symbol_map[calc_currency]

# --- Property Segment Table with conversions ---
st.subheader("🏘️ Property Segments – Price & ROI with Multi‑Currency Conversion")

# Build DataFrame
rows = []
for seg, data in property_segments.items():
    price_usd = data["price_usd"]
    roi = data["roi"]
    # Convert to other currencies
    price_inr = price_usd * conversion_rates["INR"]
    price_eur = price_usd * conversion_rates["EUR"]
    price_gbp = price_usd * conversion_rates["GBP"]
    price_aud = price_usd * conversion_rates["AUD"]
    rows.append({
        "Property Type": seg,
        "Price (USD)": price_usd,
        "Price (INR)": price_inr,
        "Price (EUR)": price_eur,
        "Price (GBP)": price_gbp,
        "Price (AUD)": price_aud,
        "Typical Gross ROI (%)": roi
    })

df_segments = pd.DataFrame(rows)
st.dataframe(df_segments.style.format({
    "Price (USD)": "${:,.0f}",
    "Price (INR)": "₹{:,.0f}",
    "Price (EUR)": "€{:,.0f}",
    "Price (GBP)": "£{:,.0f}",
    "Price (AUD)": "A${:,.0f}",
    "Typical Gross ROI (%)": "{:.1f}%"
}))

# --- Auto‑fill Inputs from Segment ---
st.subheader("💡 Select Property Segment to Auto‑Fill Values")
selected_segment = st.selectbox("Select Property Segment", list(property_segments.keys()))
if selected_segment:
    segment_price_usd = property_segments[selected_segment]["price_usd"]
    segment_roi = property_segments[selected_segment]["roi"]
    # Convert suggested property value into selected calculation currency
    suggested_price = segment_price_usd * conversion_rates[calc_currency]
    st.info(f"Suggested Property Value: {currency_symbol}{suggested_price:,.0f} ({currency_choice_label})")
    st.info(f"Suggested Rental ROI: {segment_roi}%")

# --- Inputs ---
st.subheader("🏦 Loan and Investment Inputs")
col1, col2 = st.columns(2)
with col1:
    property_value = st.number_input(
        f"Property Value ({currency_symbol})",
        value=float(suggested_price),
        step=10000.0
    )
    down_payment_pct = st.slider("Down Payment %", 0, 100, 25)
    interest_rate = st.number_input("Home Loan Interest Rate (%)", value=4.0, step=0.1)
with col2:
    tenure_years = st.number_input("Loan Tenure (Years)", value=25, step=1)
    rental_roi = st.number_input(
        "Rental ROI (%)",
        value=float(segment_roi),
        step=0.1
    )

# --- Calculate Button ---
if st.button("Calculate"):
    loan_amount, emi, monthly_rent, years_taken, annual_rental_income, total_interest, df_schedule = loan_clearance_schedule(
        property_value, down_payment_pct, interest_rate, tenure_years, rental_roi
    )

    st.markdown("### 🧾 Loan Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Loan Amount", f"{currency_symbol}{loan_amount:,.0f}")
    c2.metric("Monthly EMI", f"{currency_symbol}{emi:,.0f}")
    c3.metric("Monthly Rent", f"{currency_symbol}{monthly_rent:,.0f}")

    c4, c5, c6 = st.columns(3)
    c4.metric("Yearly Rental Yield", f"{currency_symbol}{annual_rental_income:,.0f}")
    c5.metric("Total Interest Paid", f"{currency_symbol}{total_interest:,.0f}")
    c6.metric("Loan Cleared In", f"{years_taken:.1f} years")

    st.subheader("📉 Yearly Loan Balance Overview")
    st.dataframe(df_schedule.style.format({
        "Remaining Balance": f"{currency_symbol}" + "{:,.0f}",
        "Annual Rental Yield": f"{currency_symbol}" + "{:,.0f}"
    }))

    st.line_chart(df_schedule.set_index("Year")["Remaining Balance"])
