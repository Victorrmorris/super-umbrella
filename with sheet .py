import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Cross-Border Spending Insights",
    layout="wide",
    page_icon="🌍",
)

# Google Sheets Setup
# Path to your Google Cloud credentials JSON file
credentials_file = "credentials.json"  # Ensure this is the correct path

# Google Sheets URL
sheet_url = "https://docs.google.com/spreadsheets/d/1lJAlPxYHSbmXaW31QWk8cKmQGRdElBL3JqwFvt8eopQ/edit?usp=sharing"

# Connect to Google Sheets
def connect_to_google_sheet(credentials_file, sheet_url):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(credentials_file, scopes=scope)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_url(sheet_url)
    return sheet

# Fetch data from the Google Sheet
def fetch_spreadsheet_data(sheet, sheet_name="Sheet1"):
    worksheet = sheet.worksheet(sheet_name)
    data = worksheet.get_all_records()  # Fetch all rows as dictionaries
    return pd.DataFrame(data)

# Helper Function: Style Section Titles
def style_section_title(title):
    st.markdown(f"<h2 style='text-align: center; color: #4CAF50;'>{title}</h2>", unsafe_allow_html=True)

# Main Content
st.title("🌍 Cross-Border Spending Insights")
st.markdown(
    """
    Welcome to the Cross-Border Spending Insights Dashboard! This app provides actionable 
    insights into household spending using data from a 90-day spending spreadsheet.
    """
)
st.markdown("---")

# Load Google Sheets data
try:
    sheet = connect_to_google_sheet(credentials_file, sheet_url)
    spending_data = fetch_spreadsheet_data(sheet)
    st.success("Google Sheet data loaded successfully!")
    st.dataframe(spending_data)  # Display the data

    # Ensure required columns exist
    if all(col in spending_data.columns for col in ["Date", "Amount"]):
        spending_data["Date"] = pd.to_datetime(spending_data["Date"], errors="coerce")
        spending_data["Amount"] = pd.to_numeric(spending_data["Amount"], errors="coerce")
        
        # Drop rows with missing critical data
        spending_data = spending_data.dropna(subset=["Date", "Amount"])
        
        # Provide insights
        st.header("Spending Insights")
        total_spending = spending_data["Amount"].sum()
        st.metric(label="Total Spending (90 days)", value=f"${total_spending:.2f}")

        # Monthly Breakdown
        spending_data["Month"] = spending_data["Date"].dt.to_period("M")
        monthly_spending = spending_data.groupby("Month")["Amount"].sum()
        st.bar_chart(monthly_spending)
    else:
        st.warning("The Google Sheet is missing required columns: 'Date' or 'Amount'.")
except Exception as e:
    st.error(f"Error loading Google Sheet: {e}")

# Static Data for US and Italy
us_data = {
    "Total Spent": "$4,200.50",
    "Categories": {
        "Transportation": "$650.00",
        "Rent": "$2,100.00",
        "Entertainment": "$450.50",
        "Utilities": "$300.00",
        "Groceries": "$700.00",
    },
}
italy_data = {
    "Total Spent": "€3,800.75",
    "Categories": {
        "Transportation": "€450.00",
        "Rent": "€1,800.75",
        "Entertainment": "€300.00",
        "Utilities": "€500.00",
        "Groceries": "€750.00",
    },
}

# US and Italy Insights Section
col1, col2 = st.columns(2)
with col1:
    style_section_title("US Household Spending")
    st.metric(label="US Total Spent", value=us_data["Total Spent"])
    st.write("**Category Breakdown:**")
    for category, amount in us_data["Categories"].items():
        st.markdown(f"- **{category}:** {amount}")

with col2:
    style_section_title("Italy Household Spending")
    st.metric(label="Italy Total Spent", value=italy_data["Total Spent"])
    st.write("**Category Breakdown:**")
    for category, amount in italy_data["Categories"].items():
        st.markdown(f"- **{category}:** {amount}")

# Chatbot Section
st.markdown("---")
style_section_title("💬 Chat with Your Spending Assistant")
chatbot_responses = {
    "What is the biggest expense in the US?": "In the US, the biggest expense is Rent, which accounts for $2,100.00.",
    "What is the biggest expense in Italy?": "In Italy, the biggest expense is Rent, which accounts for €1,800.75.",
    "How can I save on utilities in Italy?": "To save on utilities in Italy, consider reducing energy usage during peak hours and exploring more affordable energy plans.",
    "How can I reduce grocery expenses in the US?": "To reduce grocery expenses in the US, consider using coupons, buying in bulk, and exploring local farmer's markets.",
}
user_query = st.text_input("Ask a question about cross-border spending insights:")
if user_query:
    response = chatbot_responses.get(user_query, "I'm sorry, I don't have an answer for that question yet.")
    st.write(f"**Your Question:** {user_query}")
    st.info(f"**Chatbot Response:** {response}")
else:
    st.write("Try asking questions like:")
    for question in chatbot_responses.keys():
        st.markdown(f"- **{question}**")
