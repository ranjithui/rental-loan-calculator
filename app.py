import streamlit as st
import pandas as pd

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
# Currency Conversion Rates
# ===============================
def get_conversion_rates():
    return {"USD": 1.0, "INR": 88.0, "EUR": 0.86, "GBP": 0.74, "AUD": 1.50}

conversion_rates = get_conversion_rates()

# ===============================
# Streamlit UI Setup
# ===============================
st.set_page_config(page_title="Dubai Rental Loan Calculator", page_icon="🏢", layout="wide")

# --- Centered Bigger Logo ---
logo_path = "logo.png"  # Replace with your actual logo path
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="{logo_path}" width="150">
    </div>
    """,
    unsafe_allow_html=True
)

# --- Page Title ---
st.markdown("<h1 style='text-align:center; color:#0A81AB;'>🏢 Dubai Property Rental & Loan Calculator</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- Currency Selection ---
currency_map = {"INR (₹)": "INR", "USD ($)": "USD", "GBP (£)": "GBP", "EUR (€)": "EUR", "AUD (A$)": "AUD"}
currency_choice_label = st.selectbox("Select Currency for Calculation", list(currency_map.keys()))
calc_currency = currency_map[currency_choice_label]
currency_symbol_map = {"INR": "₹", "USD": "$", "GBP": "£", "EUR": "€", "AUD": "A$"}
currency_symbol = currency_symbol_map[calc_currency]

# --- Property Segment Table ---
st.markdown("<h2 style='color:#FF6600;'>🏘️ Dubai Property Segments – Multi-Currency Prices & ROI</h2>", unsafe_allow_html=True)
rows = []
for seg, data in property_segments.items():
    price_usd = data["price_usd"]
    roi = data["roi"]
    rows.append({
        "Property Type": seg,
        "Price (USD)": price_usd,
        "Price (INR)": price_usd * conversion_rates["INR"],
        "Price (EUR)": price_usd * conversion_rates["EUR"],
        "Price (GBP)": price_usd * conversion_rates["GBP"],
        "Price (AUD)": price_usd * conversion_rates["AUD"],
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

# --- Payment Option ---
st.markdown("<h2 style='color:#0A81AB;'>💳 Payment Option</h2>", unsafe_allow_html=True)
loan_option = st.radio("Are you planning to take a loan?", ("Yes, use loan", "No, pay full amount"))

# --- Auto-Fill Inputs ---
st.markdown("<h2 style='color:#FF6600;'>💡 Select Property Segment to Auto-Fill Values</h2>", unsafe_allow_html=True)
selected_segment = st.selectbox("Select Property Segment", list(property_segments.keys()))
segment_price_usd = property_segments[selected_segment]["price_usd"]
segment_roi = property_segments[selected_segment]["roi"]
suggested_price = segment_price_usd * conversion_rates[calc_currency]

st.info(f"Suggested Property Value: {currency_symbol}{suggested_price:,.0f} ({currency_choice_label})")
st.info(f"Suggested Rental ROI: {segment_roi}%")

# --- Inputs ---
st.markdown("<h2 style='color:#0A81AB;'>🏦 Loan and Investment Inputs</h2>", unsafe_allow_html=True)
if loan_option == "Yes, use loan":
    col1, col2 = st.columns(2)
    with col1:
        property_value = st.number_input(f"Property Value ({currency_symbol})", value=float(suggested_price), step=10000.0)
        down_payment_pct = st.slider("Down Payment %", 0, 100, 25)
        interest_rate = st.number_input("Home Loan Interest Rate (%)", value=4.0, step=0.1)
    with col2:
        tenure_years = st.number_input("Loan Tenure (Years)", value=25, step=1)
        rental_roi = st.number_input("Rental ROI (%)", value=float(segment_roi), step=0.1)
else:
    property_value = st.number_input(f"Property Value ({currency_symbol})", value=float(suggested_price), step=10000.0)
    rental_roi = st.number_input("Rental ROI (%)", value=float(segment_roi), step=0.1)

# --- Calculation ---
if st.button("Calculate"):
    if loan_option == "Yes, use loan":
        loan_amount, emi, monthly_rent, years_taken, annual_rental_income, total_interest, df_schedule = loan_clearance_schedule(
            property_value, down_payment_pct, interest_rate, tenure_years, rental_roi
        )

        # --- Loan Summary ---
        with st.container():
            st.markdown("<h3 style='color:#0A81AB;'>🧾 Loan Summary</h3>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Loan Amount", f"{currency_symbol}{loan_amount:,.0f}")
            c2.metric("Monthly EMI", f"{currency_symbol}{emi:,.0f}")
            c3.metric("Monthly Rent", f"{currency_symbol}{monthly_rent:,.0f}")
            c4, c5, c6 = st.columns(3)
            c4.metric("Yearly Rental Yield", f"{currency_symbol}{annual_rental_income:,.0f}")
            c5.metric("Total Interest Paid", f"{currency_symbol}{total_interest:,.0f}")
            c6.metric("Loan Cleared In", f"{years_taken:.1f} years")

        # --- Yearly Balance Chart ---
        with st.expander("📉 Yearly Loan Balance Overview"):
            st.dataframe(df_schedule.style.format({
                "Remaining Balance": f"{currency_symbol}" + "{:,.0f}",
                "Annual Rental Yield": f"{currency_symbol}" + "{:,.0f}"
            }))
            st.line_chart(df_schedule.set_index("Year")["Remaining Balance"])
    else:
        # --- Full Payment ROI ---
        annual_rental_income = property_value * rental_roi / 100
        with st.container():
            st.markdown("<h3 style='color:#0A81AB;'>🧾 Full Payment Summary</h3>", unsafe_allow_html=True)
            st.metric("Property Value", f"{currency_symbol}{property_value:,.0f}")
            st.metric("Yearly Rental Income", f"{currency_symbol}{annual_rental_income:,.0f}")
            st.metric("ROI (%)", f"{rental_roi:.2f}%")
