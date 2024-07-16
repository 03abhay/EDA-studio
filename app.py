import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import base64

# Set page config with dark theme
st.set_page_config(page_title="EDA STUDIO", layout="wide", page_icon='exploration.png', initial_sidebar_state="expanded")

# Custom CSS for dark theme and white text
custom_css = """
<style>
    body {
        color: white;
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    .stTextInput > div > div > input {
        color: white;
    }
    .stSelectbox > div > div > select {
        color: white;
    }
    .stMarkdown {
        color: white;
    }
    .stText {
        color: white;
    }
    .stTable {
        color: white;
    }
    .stDataFrame {
        color: white;
    }
    .plot-container {
        background-color: #0e1117 !important;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Background video setup
videohtml = """
<style>
    #vid {
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%; 
        min-height: 50%;
        opacity: 0.3;
    }
</style> 
<video autoplay muted loop class="videoback" id="vid">
    <source src='https://cdn.discordapp.com/attachments/1261563929910317091/1262286261373108286/in-y2mate.com_-_Blue_and_Black_Clouds_Background_Loop_1080p.mp4?ex=66960b30&is=6694b9b0&hm=8f36b6fb85453f002a6746e36458d1f6e27b1116cf23d887e3e29f689a02a6be&'
</video>
"""

st.markdown(videohtml, unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col3:    
    st.title("EDA STUDIO")
c1, c2, c3, c4, c5 = st.columns(5)
with col3:
    st.image("exploration.png", width=260)

coll1, coll2, coll3 = st.columns(3)
with coll2:
    st.subheader("EXPLORATORY DATA ANALYSIS")

# File uploader
uploaded_file = st.file_uploader("**Upload Your Raw Dataset Here**", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    
    # Display basic information about the dataset
    st.header("Dataset Information")
    st.write(f"Number of rows: {df.shape[0]}")
    st.write(f"Number of columns: {df.shape[1]}")
    
    # Display the first few rows of the dataset
    st.subheader("First Few Rows")
    st.write(df.head())
    
    # Display summary statistics
    st.subheader("Summary Statistics")
    st.write(df.describe())
    
    # Display column information
    st.subheader("Column Information")
    buffer = StringIO()
    df.info(buf=buffer)
    s = buffer.getvalue()
    st.text(s)

    # Column mean
    st.subheader("Column Mean calculation")
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    selected_column = st.selectbox("Select a column to calculate its mean:", numeric_columns)

    if selected_column:
        # Calculate and display the mean
        column_mean = df[selected_column].mean()
        st.write(f"**The mean of '{selected_column}' is: {column_mean:.2f}**")

    # Data Visualization
    col1, col2, col3 = st.columns(3)
    
    with col2:
        st.image("pt.png", width=290)
        st.header("**Data Visualization**")
    
    # Select columns for visualization
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    # Histogram
    st.subheader("Histogram")
    hist_column = st.selectbox("Select a numeric column for histogram:", numeric_columns)
    fig = px.histogram(df, x=hist_column, title=f"Histogram of {hist_column}")
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig)
    
    # Scatter plot
    st.subheader("Scatter Plot")
    x_column = st.selectbox("Select X-axis:", numeric_columns)
    y_column = st.selectbox("Select Y-axis:", [col for col in numeric_columns if col != x_column])
    fig = px.scatter(df, x=x_column, y=y_column, title=f"Scatter Plot: {x_column} vs {y_column}", trendline="ols")
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig)
    
    # Correlation heatmap
    st.subheader("Correlation Heatmap")
    corr_matrix = df[numeric_columns].corr()
    fig = px.density_heatmap(corr_matrix, text_auto=True, title="Correlation Heatmap")
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig)
    
    # Bar plot for categorical data
    if categorical_columns:
        st.subheader("Bar Plot")
        cat_column = st.selectbox("Select a categorical column:", categorical_columns)
        value_counts = df[cat_column].value_counts()
        fig = px.bar(x=value_counts.index, y=value_counts.values, title=f"Bar Plot of {cat_column}")
        fig.update_xaxes(title=cat_column)
        fig.update_yaxes(title="Count")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig)
    
    # Basic data analysis
    col1, col2, col3, col4, col5 = st.columns(5)
    with col3:
        st.image("chart.png", width=150)
    coll1, coll2, coll3 = st.columns(3)
    with coll2:
        st.header("**Basic Data Analysis**")
    
    # Check for missing values
    st.subheader("Missing Values")
    missing_values = df.isnull().sum()
    fig = px.bar(x=missing_values.index, y=missing_values.values, title="Missing Values by Column")
    fig.update_xaxes(title="Columns")
    fig.update_yaxes(title="Number of Missing Values")
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig)
    
    # Unique values in categorical columns
    st.subheader("Unique Values in Categorical Columns")
    for col in categorical_columns:
        st.write(f"{col}: {df[col].nunique()} unique values")
        value_counts = df[col].value_counts()
        fig = px.pie(names=value_counts.index, values=value_counts.values, title=f"Distribution of {col}")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig)
        st.write("---")

else:
    st.info("Please upload a **CSV File** to begin the analysis.")