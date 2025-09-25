import streamlit as st
import numpy as np

def loan_clearance(property_value, down_payment_pct, interest_rate, tenure_years, rental_roi):
    # Loan details
    down_payment = (down_payment_pct / 100) * property_value
    loan_amount = property_value - down_payment
    monthly_interest_rate = (interest_rate / 100) / 12
    tenure_months = tenure_years * 12

    # EMI calculation
    emi = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** tenure_months / ((1 + monthly_interest_rate) ** tenure_months - 1)

    # Rental income
    annual_rental_income = (rental_roi / 100) * property_value
    monthly_rent = annual_rental_income / 12

    # Simulation with surplus rent used to prepay loan
    outstanding = loan_amount
    month = 0
    while outstanding > 0 and month < 1000*12:
        month += 1
        interest = outstanding * monthly_interest_rate
        principal = emi - interest
        outstanding -= principal
        surplus = monthly_rent - emi
        if surplus > 0:
            outstanding -= surplus

    years_taken = month / 12

    return loan_amount, round(emi, 2), round(monthly_rent, 2), round(years_taken, 2)

# Streamlit UI
st.title("🏢 Rental Income Loan Clearance Calculator")

property_value = st.number_input("Property Value (in ₹)", value=5_00_00_000, step=1_00_000)
down_payment_pct = st.slider("Down Payment %", 0, 100, 25)
interest_rate = st.number_input("Home Loan Interest Rate (%)", value=4.0, step=0.1)
tenure_years = st.number_input("Loan Tenure (Years)", value=25, step=1)
rental_roi = st.number_input("Rental ROI (%)", value=6.0, step=0.1)

if st.button("Calculate"):
    loan_amount, emi, monthly_rent, years_taken = loan_clearance(property_value, down_payment_pct, interest_rate, tenure_years, rental_roi)

    st.subheader("📊 Results")
    st.write(f"**Loan Amount:** ₹{loan_amount:,.0f}")
    st.write(f"**Monthly EMI:** ₹{emi:,.0f}")
    st.write(f"**Monthly Rent:** ₹{monthly_rent:,.0f}")
    st.write(f"**Loan Clearance Time:** {years_taken} years")
