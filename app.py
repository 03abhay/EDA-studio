import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import base64
import os

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="EDA STUDIO",
    layout="wide",
    page_icon="exploration.png",
    initial_sidebar_state="expanded"
)

# ================== LOAD LOCAL VIDEO (background.mp4) ==================
def get_video_base64(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

video_b64 = get_video_base64("background.mp4")


# ================== GLOBAL DARK THEME CSS ==================
custom_css = """
<style>
    body {
        margin: 0;
        padding: 0;
        overflow-x: hidden;
        background-color: #000000;
    }

    .stApp {
        background-color: transparent;  /* let video show through */
    }

    /* Put main content into a dark card */
    .block-container {
        max-width: 1200px;
        margin: 2rem auto 2rem auto;
        background-color: rgba(15, 23, 42, 0.97); /* almost solid dark */
        border-radius: 16px;
        padding: 2rem 2.5rem;
        box-shadow: 0 0 25px rgba(0, 0, 0, 0.75);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #020617;  /* very dark */
        border-right: 1px solid #1f2937;
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    .stMarkdown, .stText, .stTable, .stDataFrame {
        color: #e5e7eb;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ================== VIDEO BACKGROUND (IF FILE FOUND) ==================
if video_b64 is not None:
    video_html = f"""
    <style>
    .video-background {{
        position: fixed;
        top: 0;
        left: 0;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        z-index: 0;
        object-fit: cover;
        opacity: 0.3;   /* adjust brightness of video */
        pointer-events: none;
    }}
    </style>

    <video autoplay muted loop class="video-background">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    """
    st.markdown(video_html, unsafe_allow_html=True)
# If not found: silent, you just see a black static background.

# ================== HEADER ==================
col1, col2, col3, col4, col5 = st.columns(5)
with col3:
    st.title("EDA STUDIO")

c1, c2, c3, c4, c5 = st.columns(5)
with c3:
    st.image("exploration.png", width=260)

coll1, coll2, coll3 = st.columns(3)
with coll2:
    st.subheader("EXPLORATORY DATA ANALYSIS")

st.markdown("---")

# ================== SIDEBAR ==================
st.sidebar.title("⚙️ Configuration")

st.sidebar.markdown("**Welcome to EDA STUDIO** 👋")
st.sidebar.write(
    "Upload a CSV dataset to explore structure, summary statistics, "
    "visualizations, and basic data quality insights."
)

uploaded_file = st.sidebar.file_uploader("📂 Upload CSV File", type="csv")

if uploaded_file is None:
    st.info("Please upload a **CSV file** from the sidebar to begin the analysis.")

# ================== MAIN LOGIC ==================
if uploaded_file is not None:
    # Read raw data
    raw_df = pd.read_csv(uploaded_file)
    df = raw_df.copy()

    # ---------- Sidebar: Data Cleaning Options ----------
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧹 Data Cleaning")

    drop_duplicates = st.sidebar.checkbox("Drop duplicate rows", value=True)

    missing_strategy = st.sidebar.selectbox(
        "Handle missing values:",
        [
            "None (keep as is)",
            "Drop rows with any missing values",
            "Fill numeric NA with mean",
            "Fill numeric NA with median",
            "Fill all NA with 0"
        ]
    )

    if drop_duplicates:
        df = df.drop_duplicates()

    # Handle missing values according to strategy
    if missing_strategy != "None (keep as is)":
        if missing_strategy == "Drop rows with any missing values":
            df = df.dropna()
        elif missing_strategy == "Fill numeric NA with mean":
            num_cols = df.select_dtypes(include=[np.number]).columns
            df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
        elif missing_strategy == "Fill numeric NA with median":
            num_cols = df.select_dtypes(include=[np.number]).columns
            df[num_cols] = df[num_cols].fillna(df[num_cols].median())
        elif missing_strategy == "Fill all NA with 0":
            df = df.fillna(0)

    # Sidebar dataset summary
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Dataset Summary")
    st.sidebar.write(f"**Rows (raw):** {raw_df.shape[0]}")
    st.sidebar.write(f"**Columns:** {raw_df.shape[1]}")
    st.sidebar.write(f"**Rows (after cleaning):** {df.shape[0]}")

    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

    st.sidebar.markdown("---")
    # Download cleaned dataset
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label="⬇️ Download Cleaned Dataset",
        data=csv_data,
        file_name="cleaned_dataset.csv",
        mime="text/csv"
    )

    # ================== TABS ==================
    tab_overview, tab_viz, tab_quality = st.tabs(
        ["📘 Overview", "📊 Visualizations", "🧪 Data Quality & Categorical Analysis"]
    )

    # ---------- OVERVIEW TAB ----------
    with tab_overview:
        st.header("📘 Dataset Overview")

        colA, colB = st.columns(2)
        with colA:
            st.subheader("Shape")
            st.write(f"**Raw:** {raw_df.shape[0]} rows × {raw_df.shape[1]} columns")
            st.write(f"**Cleaned:** {df.shape[0]} rows × {df.shape[1]} columns")

            st.subheader("Column Types")
            st.write(df.dtypes)

        with colB:
            st.subheader("Quick Stats (Numeric Columns)")
            if len(numeric_columns) > 0:
                st.dataframe(df[numeric_columns].describe().T)
            else:
                st.info("No numeric columns found in this dataset.")

        st.markdown("---")

        st.subheader("🔎 First Few Rows (Cleaned Data)")
        st.dataframe(df.head())

        # Column information
        st.subheader("ℹ️ Detailed Column Info")
        buffer = StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()
        st.text(info_str)

        # Column mean calculation
        st.markdown("---")
        st.subheader("📐 Column Mean Calculation (Cleaned Data)")
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_columns:
            selected_column = st.selectbox(
                "Select a numeric column:",
                numeric_columns,
                key="mean_column_select"
            )
            column_mean = df[selected_column].mean()
            st.write(f"**The mean of '{selected_column}' is:** `{column_mean:.4f}`")
        else:
            st.info("No numeric columns available for mean calculation.")

    # ---------- VISUALIZATIONS TAB ----------
    with tab_viz:
        st.header("📊 Data Visualization")

        col1, col2, col3 = st.columns(3)
        with col2:
            st.image("pt.png", width=290)

        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

        # Histogram
        st.subheader("📊 Histogram")
        if numeric_columns:
            hist_column = st.selectbox(
                "Select a numeric column for histogram:",
                numeric_columns,
                key="hist_select"
            )
            fig = px.histogram(df, x=hist_column, title=f"Histogram of {hist_column}")
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e5e7eb"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns available for histogram.")

        # Scatter plot
        st.subheader("📈 Scatter Plot")
        if len(numeric_columns) >= 2:
            x_column = st.selectbox(
                "Select X-axis:",
                numeric_columns,
                key="scatter_x_select"
            )
            y_options = [col for col in numeric_columns if col != x_column]
            y_column = st.selectbox(
                "Select Y-axis:",
                y_options,
                key="scatter_y_select"
            )
            fig = px.scatter(
                df,
                x=x_column,
                y=y_column,
                title=f"Scatter Plot: {x_column} vs {y_column}",
                trendline="ols"
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e5e7eb"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need at least two numeric columns for a scatter plot.")

        # Correlation heatmap
        st.subheader("🔥 Correlation Heatmap")
        if len(numeric_columns) >= 2:
            corr_matrix = df[numeric_columns].corr()
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                title="Correlation Heatmap",
                aspect="auto",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e5e7eb"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need at least two numeric columns for a correlation heatmap.")

    # ---------- DATA QUALITY & CATEGORICAL ANALYSIS TAB ----------
    with tab_quality:
        st.header("🧪 Data Quality & Categorical Analysis")

        col1, col2, col3, col4, col5 = st.columns(5)
        with col3:
            st.image("chart.png", width=150)

        st.subheader("🕳 Missing Values (Cleaned Data View)")
        missing_values = df.isnull().sum()
        fig = px.bar(
            x=missing_values.index,
            y=missing_values.values,
            title="Missing Values by Column"
        )
        fig.update_xaxes(title="Columns")
        fig.update_yaxes(title="Number of Missing Values")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e5e7eb"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Unique values in categorical columns
        st.subheader("🔤 Unique Values in Categorical Columns")
        if categorical_columns:
            for col in categorical_columns:
                st.markdown(f"**{col}** – {df[col].nunique()} unique values")
                value_counts = df[col].value_counts()
                fig = px.pie(
                    names=value_counts.index,
                    values=value_counts.values,
                    title=f"Distribution of {col}"
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#e5e7eb"
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("---")
        else:
            st.info("No categorical columns found for analysis.")

# ================== FOOTER WITH LINKS ==================
st.markdown("---")

linkedin_url = "https://www.linkedin.com/in/your-linkedin-id/"
github_url = "https://github.com/your-github-username"

footer_html = f"""
<style>
.footer {{
    text-align: center;
    color: gray;
    font-size: 0.9rem;
    margin-top: 10px;
}}
.footer a {{
    color: #58a6ff;
    text-decoration: none;
}}
.footer a:hover {{
    text-decoration: underline;
}}
.github-btn {{
    display: inline-block;
    padding: 6px 14px;
    margin-left: 8px;
    border-radius: 999px;
    border: 1px solid #58a6ff;
    color: #58a6ff;
    font-size: 0.85rem;
    text-decoration: none;
}}
.github-btn:hover {{
    background-color: #58a6ff22;
}}
</style>

<div class="footer">
    <p>Built with ❤️ using Streamlit | EDA STUDIO – Exploratory Data Analysis App</p>
    <p>
        <a href="https://www.linkedin.com/in/abhaysingh212003/" target="_blank">Connect on LinkedIn</a>
        <a href="https://github.com/03abhay" target="_blank" class="github-btn">GitHub Profile</a>
    </p>
    <p>© 2025 EDA STUDIO by Abhay Singh. All rights reserved.</p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
