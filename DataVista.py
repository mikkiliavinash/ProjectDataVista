import streamlit as st
import pandas as pd
from fpdf import FPDF, HTMLMixin
import io
from datetime import datetime

st.set_page_config(layout="wide")
# Sidebar Navigation
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio("Go to", ["Homepage", "Edit Data Type", "Replace Null's","Contact"])
st.session_state['current_page'] = selected_page

 # Title of the Streamlit app
st.title("📂 Upload and Preview CSV/Excel File")
    # File uploader widget
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])


if uploaded_file is not None:
    if st.session_state['current_page'] == "Homepage":
        try:
            # Read CSV or Excel file
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            if df.empty:
                st.warning("⚠️ Uploaded file is empty. Please upload a valid CSV/Excel file.")
            else:
                # Show file details
                st.write(f"### File Name: {uploaded_file.name}")
                st.write(f"📏 File Size: {uploaded_file.size / 1024:.2f} KB")

                # Show dataset summary
                n_rows, n_columns = df.shape
                st.write(f"Number of Rows: {n_rows}")  
                st.write(f"Number of Columns: {n_columns}")

                # Split into two columns
                col1, col2 = st.columns(2)
                with col1:
                    st.write("First 5 Rows")
                    st.write(df.head())

                with col2:
                    st.write("Last 5 Rows")
                    st.write(df.tail())

                # Creating dataset summary
                summary_data = {
                    "Column Name": df.columns,
                    "Uniques Count": [df[col].nunique() for col in df.columns],  # Count of unique values
                    "Total Count": [df[col].count() for col in df.columns],  # Total non-null values
                    #"Unique Values": [', '.join(map(str, df[col].unique())) + "..." if df[col].dtype == 'object' else df[col].unique() for col in df.columns],  # First 100 unique values as string
                    "Duplicates": [df[col].duplicated().sum() for col in df.columns],  # Duplicate count
                    "Nulls": [df[col].isnull().sum() for col in df.columns],  # Null count
                    "Data Type": [df[col].dtype for col in df.columns]  # Data type of column
                }


                # Show dataset details
                st.write("### 🏷️ Details:")
                summarydf = pd.DataFrame(summary_data)
                st.write(summarydf)

                # Function to generate a detailed PDF report
                
                def generate_pdf():
                    class pdff(FPDF):
                        def header(self):
                            # Title
                            self.set_font("Times", size=20)
                            self.cell(190, 8, 'Data Vista', ln=True, align="l")
                            # Developer Info
                            self.set_font('Times',size= 10)
                            self.cell(180, 5, 'Developed by: Mikkili Avinash', align="l")
                            #Date
                            current_date = datetime.now().strftime("%Y-%m-%d")
                            self.cell(10, 5, txt=f"Date: {current_date}", align='r',ln=True)



                        def footer(self):
                            #
                            self.set_y(-15)
                            self.cell(0,10,f'Page No-{self.page_no()}')
                            return super().footer()

                    #Object of FPDF
                    pdf = pdff('P', 'mm', 'A4')
                    #get total pages
                    pdf.alias_nb_pages()
                    #creating Page
                    pdf.add_page()
                    #Page Width
                    pdf.set_auto_page_break(auto=True,margin=5)
                    
                    #pdf.image("https://drive.google.com/uc?id=17y53wBuKpsorr8Cu39CwCUMVMf6GZniN", x=60, y=30, w=90, h=0, type="JPG")


                    # Adds a line beginning at point (10,30) and ending at point (110,30)
                    pdf.line(10, 23, 200, 23)

                    #number of rows and columns
                    pdf.set_font('Times',size= 10)                
                    pdf.cell(10,5,f"Number of Rows: {n_rows}",ln=True)
                    pdf.cell(10,5,f"Number of Columns: {n_columns}",ln=True)
                
                    pdf.cell(10,5," ",ln=True)
                    # ✅ Correct way to generate bordered table
                    #html_table = summarydf.to_html(index=False, border=1)
                    #pdf.write_html(html_table)
                # 🟢 **Manually Create Table with Borders**
                    col_widths = [40, 30, 30, 30, 30, 30]  # Adjust widths as needed
                    headers = ["Column Name", "Uniques Count", "Total Count", "Duplicates", "Nulls", "Data Type"]

                    # 🟢 **Draw Table Header**
                    pdf.set_font('Times', 'B', 10)
                    for i, header in enumerate(headers):
                        pdf.cell(col_widths[i], 7, header, border=1, align='C')
                    pdf.ln()

                    # 🟢 **Draw Table Rows**
                    pdf.set_font('Times', '', 10)
                    for _, row in summarydf.iterrows():
                        pdf.cell(col_widths[0], 6, str(row["Column Name"]), border=1)
                        pdf.cell(col_widths[1], 6, str(row["Uniques Count"]), border=1, align='C')
                        pdf.cell(col_widths[2], 6, str(row["Total Count"]), border=1, align='C')
                        pdf.cell(col_widths[3], 6, str(row["Duplicates"]), border=1, align='C')
                        pdf.cell(col_widths[4], 6, str(row["Nulls"]), border=1, align='C')
                        pdf.cell(col_widths[5], 6, str(row["Data Type"]), border=1, align='C')
                        pdf.ln()

                    # Save PDF to a BytesIO buffer
                    pdf_buffer = io.BytesIO()
                    pdf.output(pdf_buffer)  
                    pdf_buffer.seek(0)  # Move cursor to start
                    
                    return pdf_buffer  # Return raw bytes
                
                if st.button("Generate PDF"):
                    pdf_buffer = generate_pdf()  # Get the PDF as a BytesIO object
                    st.download_button(
                    label="📥 Download PDF",
                    data=pdf_buffer,  # Pass the BytesIO object directly
                    file_name="DataVista_Report.pdf",
                    mime="application/pdf"
                    )

        except Exception as e:
            st.error(f"❌ Error: {e}")

    if st.session_state['current_page'] == "Edit Data Type":
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            if df.empty:
                st.warning("⚠️ Uploaded file is empty. Please upload a valid CSV/Excel file.")
            else:
                try:
                    st.sidebar.subheader("Select a Column")
                    selected_column = st.sidebar.radio("Columns", df.columns)

                    st.write(f"#### Editing Data Type for Column: `{selected_column}`")
                    original_dtype = df[selected_column].dtype
                    st.write(f"Original Data Type: `{original_dtype}`")

                    new_dtype = st.selectbox(
                    "Select New Data Type:",
                    ["object", "int64", "float64", "bool", "datetime64[ns]"]
                    )

                    if st.button('Change Data Type'):
                        if new_dtype in ["int64", "float64"]:
                            # Try converting to numeric
                            df_temp = pd.to_numeric(df[selected_column], errors='coerce')

                            # Find rows where conversion failed (NaN means the value was not numeric)
                            non_numeric_rows = df_temp[df_temp.isna()].index.tolist()

                            if non_numeric_rows:
                                st.error(f"❌ Cannot convert `{selected_column}` to `{new_dtype}`. Non-numeric values found at rows: {non_numeric_rows}")
                            else:
                                df[selected_column] = df_temp.astype(new_dtype)
                                st.success(f"✅ Successfully changed `{selected_column}` to `{new_dtype}`!")
                        elif new_dtype == "datetime64[ns]":
                            try:
                                df[selected_column] = pd.to_datetime(df[selected_column], errors='raise')
                                st.success(f"✅ Successfully changed `{selected_column}` to `datetime64[ns]`!")
                            except Exception as e:
                                st.error(f"❌ Error converting `{selected_column}` to datetime: {e}")
                        else:
                            df[selected_column] = df[selected_column].astype(new_dtype)
                            st.success(f"✅ Successfully changed `{selected_column}` to `{new_dtype}`!")

                    changed_dtype = df[selected_column].dtype
                    st.write(f"New Data Type: `{changed_dtype}`")

                    # 🟢 **Button to Download Updated DataFrame**
                    if st.button("Download Updated DataFrame"):
                        output = io.BytesIO()
                        df.to_csv(output, index=False)
                        output.seek(0)
                        st.download_button(
                            label="📥 Download CSV",
                            data=output,
                            file_name="Updated_Data.csv",
                            mime="text/csv"
                            )

                except Exception as e:
                    st.error(f"❌ Error: {e}")
    if st.session_state['current_page'] == "Replace Null's":
         if uploaded_file is not None:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            if df.empty:
                st.warning("⚠️ Uploaded file is empty. Please upload a valid CSV/Excel file.")
            else:
                try:
                    st.sidebar.subheader("Select a Column")
                    selected_column = st.sidebar.radio("Columns", df.columns)

                    st.write(f"#### Replace Nulls in : `{selected_column}`")
                    
                    nullcount = df[selected_column].isnull().sum()  # Null count
                    # ✅ Display rows containing nulls in the selected column
                    null_rows = df[df[selected_column].isnull()]
                    st.write("### Rows with Null Values")
                    st.write(null_rows)  # This will show the full row where nulls exist
                    st.write(f"Nulls in the column: `{nullcount}`") 

                    replacevalue = st.text_input('Enter replacement value')

                    st.write(f'{replacevalue}')

                    if st.button("Replace Nulls"):
                        if replacevalue:
                            df[selected_column] = df[selected_column].fillna(replacevalue)
                            st.success(f"Null values in `{selected_column}` replaced with `{replacevalue}`!")
                            st.write("### Updated DataFrame")
                            st.write(df)
                        else:
                            st.warning("Please enter a valid replacement value.")


                except Exception as e:
                    st.error(f"❌ Error: {e}")

                    

    # 📌 Contact Page
if st.session_state['current_page'] == "Contact":
    st.write("### 📞 Contact Developer")
    st.write("👨‍💻 **Mikkili Avinash**")
    st.write("📧 Email: mikkiliavinash7@gmail.com")
    st.write("📞 Phone: +91-9963696413")