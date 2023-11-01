# Import streamlit modules
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie

# Import yfinance for stock information
import yfinance as yf

# Import plotly.express for data visualization
import plotly.express as px

# Import necessary modules for file navigation + lotties
from pathlib import Path
import json

# Import datetime for date configuration
from datetime import datetime

# Store the page icon and title in variables
PAGE_TITLE = "Stocks Comparison Tool"
PAGE_ICON = "✨"

# Set the page configuration to the title and icon variables defined above
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# Obtain the path of the current file
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()

# Find the CSS file
css_file = current_dir / "styles" / "main.css"

# Open CSS file
with open(css_file) as css:
    st.markdown("<style>{}</style>".format(css.read()), unsafe_allow_html=True)

# Define a function to load the Lottie file (basically a gif)
def load_lottie(filepath: str):
    with open(filepath, "r") as f:
        # Use json to load the file
        return json.load(f)

# Title the website
st.title("Stocks Comparison Tool\n")

# Create two columns
col1, col2 = st.columns(2, gap="small")

# Place the instructions in the first column
with col1: 
    st.write("\n**Instructions:**")
    st.write("- 📈 Select the \"Direct Comparison\" for comparing the prices of the stocks over time.")
    st.write("- 📉 Select the \"Relative Returns Comparison\" for comparing the percentage change in stock values over time.")

# Define the lottie
money_lottie = load_lottie("money.json")

# Add the lottie file in the second column
with col2:
    st_lottie(
    money_lottie,
)

# Use option_menu() to create two different sections in the webapp
selected = option_menu(
    # Leave the title blank (must include it, though, because it is mandatory)
    menu_title = "",
    # The user has two options: the direct comparison tool, and the relative returns comparison tool
    options = ["Direct Comparison", "Relative Returns Comparison"],
    icons = ["coin", "cash-coin"],
    # Set orientation to horizontal (looks better than vertical)
    orientation = "horizontal"
)


# Create a function to check if the tickers are valid
def check_tickers(tickers):
    valid_tickers = []
    # For every every valid ticker, append it into the valid_tickers empty list
    for ticker in tickers:
        if ticker:
            data = yf.download(ticker, start=start_date, end=end_date)
            if not data.empty:
                valid_tickers.append(ticker)
    # Return the list of valid tickers
    return valid_tickers


# If the user selects Direct Comparison, then run the code inside this
if selected == "Direct Comparison":

    # Set the subheader
    st.subheader("Direct Comparison")

    # Add an input field for the user to enter their own stock tickers (leave three common ones as default)
    user_input = st.text_input("Enter stock tickers (comma-separated)", value="TSLA, AAPL, MSFT")
    # Use list comprehension to split the tickers list as every comma, and then strip the ticker input to remove spaces
    tickers = [ticker.strip().upper() for ticker in user_input.split(",")]

    # Set default start date
    default_start_date = datetime(2022, 1, 1)
    
    # Allow the user to pick start and end dates
    start_date = st.date_input("Start Date", default_start_date)
    end_date = st.date_input("End Date")


    # Add a submit button
    if st.button("Submit"):

        # Execute this code if the user entered any tickers
        if len(tickers) > 0:
            valid_tickers = check_tickers(tickers)

            # If the user has entered in valid tickers, then run this
            if len(tickers) > 0:
                # Download the data from yfinance
                data_frame = yf.download(valid_tickers, start=start_date, end=end_date)["Adj Close"]
                # Create a placeholder for the chart
                chart_placeholder = st.empty()  

                # Create a header
                st.header(f"Price of {valid_tickers} in USD")

                # Plot the chart using streamlit's default data tools
                st.line_chart(data_frame)
            

# If the user selects Relative Returns Comparison, then run the code inside this
if selected == "Relative Returns Comparison":
    # Set the subheader
    st.subheader("Relative Returns Comparison")

    # Add an input field for the user to enter their own stock tickers (leave three common ones as default)
    user_input = st.text_input("Enter stock tickers (comma-separated)", value="TSLA, AAPL, MSFT")
    # Use list comprehension to split the tickers list as every comma, and then strip the ticker input to remove spaces
    tickers = [ticker.strip().upper() for ticker in user_input.split(",")]

    # Set default start date
    default_start_date = datetime(2022, 1, 1)
    
    # Allow the user to pick start and end dates
    start_date = st.date_input("Start Date", default_start_date)
    end_date = st.date_input("End Date")


    # Create a function that calculates relative returns and takens in a data frame as a parameter
    def calculate_relative_returns(data_frame):
        # Set relative returns equal to the percentage change of the data frame
        relative_returns = data_frame.pct_change()
        # Formula for calculating cumulative returns (total change in investment over a period of time)
        cumulative_returns = (relative_returns+1).cumprod()-1
        # Cumulative returns at the first day will be 0
        cumulative_returns = cumulative_returns.fillna(0)
        return cumulative_returns
    
        
    # Add a submit button
    if st.button("Submit"):

        # Execute this code if the user entered any tickers
        if len(tickers) > 0:

            # Check data validity
            valid_tickers = check_tickers(tickers)

            # Download the data from yfinance
            data_frame = calculate_relative_returns(yf.download(valid_tickers, start_date, end_date)["Adj Close"])
            # Create a placeholder for the chart
            chart_placeholder = st.empty()  

            st.header(f"Relative Returns of {valid_tickers}")

            fig = px.line(data_frame, x=data_frame.index, y=valid_tickers)
            fig.update_xaxes(title_text="Time")
            
            # Update the y-axis to display percentages with a '%' sign
            fig.update_yaxes(title_text="% Change in Stock Value", tickformat=".0%")
            fig.update_layout(legend_title_text="Stocks")

            # Plot the chart using plotly
            st.plotly_chart(fig)
