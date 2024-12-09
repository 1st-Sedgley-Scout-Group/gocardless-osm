import streamlit as st
import pandas as pd
from accounting.accounting import ReadGoCardlessPayoutExport
import pendulum

def get_data():
    data = pd.read_csv(st.session_state['file'])
    st.session_state['payout'] = ReadGoCardlessPayoutExport(data).create_payout()

st.title("GoCardless Payouts")

if 'payout' not in st.session_state:
    st.session_state['file'] = st.file_uploader("Payout CSV from GoCardless", accept_multiple_files=False, on_change=get_data)
else:
    
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
    
