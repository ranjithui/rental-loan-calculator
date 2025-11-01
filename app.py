import streamlit as st
import pandas as pd
from PIL import Image
import os
import base64

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
# Function: Project Property Value for 10 Years with Annual Increase %
# ===============================
def project_property_value_list(current_value, annual_increase_pct, years=10):
    projection = []
    value = current_value
    for year in range(1, years + 1):
        value = value * (1 + annual_increase_pct / 100)
        projection.append({
            "Year": year,
            "Projected Value": value,
            "Annual Increase %": annual_increase_pct
        })
    return pd.DataFrame(projection)

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
# Approximate Annual Property Value Increase
# ===============================
property_value_increase = {
    "Studio / Entry‑level Apartment": 6,
    "1‑Bedroom Apartment": 8,
    "2‑Bedroom Apartment": 7,
    "Townhouse / Mid‑segment Villa": 21,
    "Premium / Luxury Villa": 25
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

# ===============================
# Step 1: Header with Centered Logo or Fallback Heading
# ===============================
logo_path = "logo.png"  # Replace with your actual logo path

if os.path.exists(logo_path):
    def get_base64_of_bin_file(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

    logo_base64 = get_base64_of_bin_file(logo_path)
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:10px;">
            <img src="data:image/png;base64,{logo_base64}" width="150">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<h1 style='text-align:center; color:#1F4E79; font-family:Arial;'>Dubai Property Rental & Loan Calculator</h1>",
        unsafe_allow_html=True
    )

st.markdown(
    "<p style='text-align:center; color:#4B4B4B;'>Make informed investment decisions with multi-currency insights and rental ROI projections</p>",
    unsafe_allow_html=True
)
st.markdown("<hr style='border:1px solid #D3D3D3'>", unsafe_allow_html=True)

# ===============================
# Step 2: Select Property Segment & Currency
# ===============================
st.markdown("<h2 style='color:#1F4E79;'>Step 1: Select Property Segment & Currency</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#4B4B4B;'>Select a property segment to auto-fill suggested values for property price and rental ROI, and choose your preferred currency.</p>", unsafe_allow_html=True)

# Currency Selection
currency_map = {"INR (₹)": "INR", "USD ($)": "USD", "GBP (£)": "GBP", "EUR (€)": "EUR", "AUD (A$)": "AUD"}
currency_choice_label = st.selectbox("Select Currency for Calculation", list(currency_map.keys()))
calc_currency = currency_map[currency_choice_label]
currency_symbol_map = {"INR": "₹", "USD": "$", "GBP": "£", "EUR": "€", "AUD": "A$"}
currency_symbol = currency_symbol_map[calc_currency]

# Property Segment Selection
selected_segment = st.selectbox("Select Property Segment", list(property_segments.keys()))
segment_price_usd = property_segments[selected_segment]["price_usd"]
segment_roi = property_segments[selected_segment]["roi"]
suggested_price = segment_price_usd * conversion_rates[calc_currency]

st.info(f"Suggested Property Value: {currency_symbol}{suggested_price:,.0f} ({currency_choice_label})")
st.info(f"Suggested Rental ROI: {segment_roi}%")

# Display estimated annual property increase
annual_increase = property_value_increase.get(selected_segment, 5)  # default 5%
st.info(f"💡 Estimated Annual Property Value Increase: {annual_increase}% (based on recent Dubai market trends)")

# Project property value for 10 years with annual increase %
df_projection_list = project_property_value_list(suggested_price, annual_increase, years=10)
st.markdown("<h3 style='color:#1F4E79;'>📊 10-Year Projected Property Value List</h3>", unsafe_allow_html=True)
st.dataframe(df_projection_list.style.format({
    "Projected Value": f"{currency_symbol}" + "{:,.0f}",
    "Annual Increase %": "{:.1f}%"
}))
st.line_chart(df_projection_list.set_index("Year")["Projected Value"])

# ===============================
# Property Segments – Cards Layout
# ===============================
st.markdown("<h3 style='color:#1F4E79;'>Property Segments – Multi-Currency Prices & ROI</h3>", unsafe_allow_html=True)
st.markdown("<p style='color:#4B4B4B;'>Explore Dubai property segments with approximate prices and rental yield. Click each card to see details.</p>", unsafe_allow_html=True)

cols = st.columns(3)  # 3 cards per row
for i, (seg, data) in enumerate(property_segments.items()):
    col = cols[i % 3]
    price_converted = data["price_usd"] * conversion_rates[calc_currency]
    roi = data["roi"]
    with col:
        st.markdown(f"""
        <div style="border:1px solid #D3D3D3; border-radius:10px; padding:15px; margin:5px; background-color:#F9F9F9;">
            <h4 style='color:#1F4E79;'>{seg}</h4>
            <p style='color:#4B4B4B;'>Price ({currency_choice_label}): {currency_symbol}{price_converted:,.0f}</p>
            <p style='color:#4B4B4B;'>Typical ROI: {roi:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

# ===============================
# Step 2: Payment Option & Inputs
# ===============================
st.markdown("<h2 style='color:#1F4E79;'>Step 2: Choose Payment Option & Enter Inputs</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#4B4B4B;'>Select whether you want to take a loan or pay the full amount, and provide required input values.</p>", unsafe_allow_html=True)

# Payment Option
loan_option = st.radio("Do you plan to take a loan?", ("Yes, use loan", "No, pay full amount"))

# Input fields
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

# ===============================
# Step 3: Calculate & Display Results
# ===============================
if st.button("Calculate"):
    if loan_option == "Yes, use loan":
        loan_amount, emi, monthly_rent, years_taken, annual_rental_income, total_interest, df_schedule = loan_clearance_schedule(
            property_value, down_payment_pct, interest_rate, tenure_years, rental_roi
        )

        st.markdown("<h3 style='color:#1F4E79;'>Loan Summary</h3>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Loan Amount", f"{currency_symbol}{loan_amount:,.0f}")
        c2.metric("Monthly EMI", f"{currency_symbol}{emi:,.0f}")
        c3.metric("Monthly Rent", f"{currency_symbol}{monthly_rent:,.0f}")
        c4, c5, c6 = st.columns(3)
        c4.metric("Yearly Rental Yield", f"{currency_symbol}{annual_rental_income:,.0f}")
        c5.metric("Total Interest Paid", f"{currency_symbol}{total_interest:,.0f}")
        c6.metric("Loan Cleared In", f"{years_taken:.1f} years")

        with st.expander("Yearly Loan Balance Overview"):
            st.dataframe(df_schedule.style.format({
                "Remaining Balance": f"{currency_symbol}" + "{:,.0f}",
                "Annual Rental Yield": f"{currency_symbol}" + "{:,.0f}"
            }))
            st.line_chart(df_schedule.set_index("Year")["Remaining Balance"])
    else:
        # Full Payment mode: yearly and monthly rental
        annual_rental_income = property_value * rental_roi / 100
        monthly_rental_income = annual_rental_income / 12
        st.markdown("<h3 style='color:#1F4E79;'>Full Payment Summary</h3>", unsafe_allow_html=True)
        st.metric("Property Value", f"{currency_symbol}{property_value:,.0f}")
        st.metric("Yearly Rental Income", f"{currency_symbol}{annual_rental_income:,.0f}")
        st.metric("Monthly Rental Income", f"{currency_symbol}{monthly_rental_income:,.0f}")
        st.metric("ROI (%)", f"{rental_roi:.2f}%")
