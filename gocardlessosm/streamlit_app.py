"""The streamlit app to host the GoCardless Payout formatter."""

import pandas as pd
import streamlit as st

from gocardlessosm.payout_processor import process_gocardless_export

st.set_page_config(
    page_title="GoCardless Payouts",
    menu_items={
        "About": "Created by 1st Sedgley Scout Group for internal use only.",
    },
)


def get_data() -> None:
    """Callback to get the data from the uploaded file."""
    data = pd.read_csv(st.session_state["file"])
    st.session_state["payout"] = process_gocardless_export(data)


st.title("GoCardless Payouts")

with st.form("form", clear_on_submit=True, border=False):
    st.session_state["file"] = st.file_uploader(
        "Payout CSV from GoCardless", accept_multiple_files=False
    )
    instructions = st.expander("Instructions", expanded=False)
    instructions.markdown(
        """
        1. Download the payout CSV from GoCardless
        (Payments > Payouts > Select desired payout > Payout breakdown > Export > transactions > Export)
        2. Upload the file here.
        3. Click submit.
        4. The payout information will be displayed below.
        """
    )

    st.session_state["submit"] = st.form_submit_button("submit")

if st.session_state["submit"] is True:
    get_data()

if "payout" in st.session_state:
    st.divider()
    st.success(":partying_face: Success payout information available below")
    st.markdown(f"""
                |||
                |---|---|
                |Date|{pd.Timestamp(st.session_state['payout'].date).strftime("%d %b %Y")}|
                |Gross|£{round(st.session_state['payout'].gross_amount, 2):,.2f}|
                |Net| £{round(st.session_state['payout'].net_amount, 2):,.2f}|
                |Fees| £{round(st.session_state['payout'].fees, 2):,.2f}|
                """)
    st.subheader("Subscriptions")
    st.write(
        st.session_state["payout"].subscriptions
        if not st.session_state["payout"].subscriptions.empty
        else "No subscriptions payments in this payout"
    )

    st.subheader("Activities")
    st.write(
        st.session_state["payout"].activities
        if not st.session_state["payout"].activities.empty
        else "No activities payments in this payout"
    )

    st.subheader("Summer Camp")
    st.write(
        st.session_state["payout"].summer
        if not st.session_state["payout"].summer.empty
        else "No summer camp payments in this payout"
    )
