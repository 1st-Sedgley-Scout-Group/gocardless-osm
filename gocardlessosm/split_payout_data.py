import streamlit as st
import pandas as pd
from accounting import ReadGoCardlessPayoutExport
import pendulum

def get_data():
    data = pd.read_csv(st.session_state['file'])
    st.session_state['payout'] = ReadGoCardlessPayoutExport(data).create_payout()

st.title("GoCardless Payouts")

with st.form("form", clear_on_submit=True):
    st.session_state['file'] = st.file_uploader("Payout CSV from GoCardless", accept_multiple_files=False)
    st.session_state['submit'] = st.form_submit_button("submit")

if st.session_state['submit'] is True:
    get_data()

if 'payout' in st.session_state:
    st.divider()
    st.success(":partying_face: Success payout information available below")
    st.markdown(f"""
                |||
                |---|---|
                |Date|{pendulum.parse(st.session_state['payout'].date).format("DD MMM YYYY")}|
                |Gross|£{round(st.session_state['payout'].gross_amount, 2):,.2f}|
                |Net| £{round(st.session_state['payout'].net_amount, 2):,.2f}|
                |Fees| £{round(st.session_state['payout'].fees, 2):,.2f}|
                """)
    st.subheader("Subscriptions")
    st.write(st.session_state['payout'].subscriptions)

    st.subheader("Activities")
    st.write(st.session_state['payout'].activities)
