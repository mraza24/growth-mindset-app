import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set up the Streamlit App
st.set_page_config(page_title="Growth Mindset App", layout="wide")

# Center-aligned title and description
st.markdown("""
    <h1 style='text-align: center;'>🚀 Growth Mindset App</h1>
    <p style='text-align: center; font-size:18px;'>Easily clean, transform, and visualize your data!</p>
""", unsafe_allow_html=True)

# File Upload Section
uploaded_files = st.file_uploader("📂 Upload CSV or Excel files:", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read file
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file, engine="openpyxl")
        else:
            st.error(f"❌ Unsupported file type: {file_ext}")
            continue  

        # Display File Info
        st.write(f"**📄 File:** {file.name} | **📏 Size:** {file.size / 1024:.2f} KB")

        # Preview Raw Data
        st.markdown("### 📋 Data Preview")
        st.dataframe(df.head())

        # **Fix Unnamed Columns**
        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

        # Column Selection with Hover Effect
        st.subheader("🔍 Select Columns")
        selected_columns = st.multiselect(
            f"Choose columns for {file.name}", df.columns.tolist(), default=df.columns.tolist()
        )

        if selected_columns:
            df_selected = df[selected_columns]
        else:
            st.warning("⚠️ Please select at least one column.")
            df_selected = df

        # Updated Data Preview
        st.markdown("### 🔄 Updated Data")
        st.dataframe(df_selected)

        # **Data Cleaning Options**
        st.subheader("🛠 Data Cleaning")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(f"🧹 Remove Duplicates - {file.name}"):
                df_selected.drop_duplicates(inplace=True)
                st.success("✅ Duplicates removed!")

        with col2:
            if st.button(f"📊 Fill Missing Values (Mean) - {file.name}"):
                numeric_cols = df_selected.select_dtypes(include=["number"]).columns
                df_selected[numeric_cols] = df_selected[numeric_cols].fillna(df_selected[numeric_cols].mean())
                st.success("✅ Missing values filled!")
        
        with col3:
            if st.button(f"🗑 Remove Null Rows - {file.name}"):
                df_selected.dropna(inplace=True)
                st.success("✅ Null rows removed!")

        # **Data Visualization**
        st.subheader("📊 Data Visualization") 
        if st.checkbox(f"📈 Show Charts - {file.name}"):
            numeric_data = df_selected.select_dtypes(include="number")
            if not numeric_data.empty:
                st.bar_chart(numeric_data.iloc[:, :2])
            else:
                st.warning("⚠️ No numeric data for visualization.")

        # **File Conversion**
        st.subheader("💾 Download Processed File")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

        if st.button(f"⬇️ Convert & Download - {file.name}"):
            buffer = BytesIO()

            if conversion_type == "CSV":
                df_selected.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            
            elif conversion_type == "Excel":
                df_selected.to_excel(buffer, index=False, engine="xlsxwriter")
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            st.download_button(
                label=f"⬇️ Download {file_name}",
                data=buffer,
                file_name=file_name,
                mime=mime_type,
            )
            st.success(f"✅ {file_name} is ready for download!")

st.success("✅ All files processed successfully!")