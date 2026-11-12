import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from google import genai
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from main import analyze_business_data

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None


def create_business_prompt(business_results):

    kpis = business_results["KPIs"]

    category = business_results["Category"].round(2)
    region = business_results["Region"].round(2)

    state = business_results["State"]
    product = business_results["Product"]

    yearly = business_results["Yearly"].round(2)
    discount = business_results["Discount"].round(2)

    prompt = f"""
    You are a business analyst reviewing a company's performance.

    Analyse the following business results and provide useful insights.

    OVERALL BUSINESS PERFORMANCE:
    {kpis}

    CATEGORY PERFORMANCE:
    {category.to_string()}

    REGIONAL PERFORMANCE:
    {region.to_string()}

    TOP 5 STATES BY SALES:
    {state.sort_values(by="Total_Sales", ascending=False).head(5).round(2).to_string()}

    BOTTOM 5 STATES BY PROFIT:
    {state.sort_values(by="Total_Profit").head(5).round(2).to_string()}

    TOP 5 PRODUCTS BY SALES:
    {product.sort_values(by="Total_Sales", ascending=False).head(5).round(2).to_string()}

    BOTTOM 5 PRODUCTS BY PROFIT:
    {product.sort_values(by="Total_Profit").head(5).round(2).to_string()}

    YEARLY PERFORMANCE:
    {yearly.to_string()}

    DISCOUNT ANALYSIS:
    {discount.to_string()}

    YOUR TASK:

    
    YOUR TASK:

    Write a business performance summary in 6-7 sentences.

    The summary should:
    1. Start with an overall view of how the business is performing.
    2. Highlight 2-3 important findings from the data.
    3. Explain the biggest business concern in simple language.
    4. Suggest one or two practical actions the business could consider.

    WRITING STYLE:
    - Use very simple, everyday English.
    - Write as if explaining the findings to a business manager
      who does not have a data or analytics background.
    - Keep sentences natural and easy to follow.
    - Include a few relevant numbers to support your findings.
    - Avoid technical terms, jargon and complicated phrases.
    - Do not use headings, bullet points or numbered lists.
    - Do not try to cover every analysis in the dataset.

    IMPORTANT:
    - Use only the facts provided in the data.
    - Do not invent reasons for business performance.
    - Do not present possible explanations as confirmed facts.
    - Recommendations should be reasonable and supported
      by the findings.

    """

    return prompt



def create_pdf_report(business_results, ai_insights):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # Report title
    elements.append(
        Paragraph("Business Performance Report", styles["Title"])
    )

    elements.append(Spacer(1, 15))

    # Overall KPIs
    elements.append(
        Paragraph("Overall Business Performance", styles["Heading2"])
    )

    kpis = business_results["KPIs"]

    kpi_data = [["Metric", "Value"]]

    for key, value in kpis.items():

        if "Orders" in key:
            formatted_value = f"{value:,.0f}"
        elif "Margin" in key:
            formatted_value = f"{value:,.2f}%"
        else:
            formatted_value = f"${value:,.2f}"

        kpi_data.append([str(key), formatted_value])

    kpi_table = Table(kpi_data, hAlign="LEFT")

    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("PADDING", (0, 0), (-1, -1), 5)
    ]))

    elements.append(kpi_table)
    elements.append(Spacer(1, 20))

    # AI-generated insights
    elements.append(
        Paragraph("AI-Generated Business Insights", styles["Heading2"])
    )

    from xml.sax.saxutils import escape

    safe_insights = escape(str(ai_insights))

    elements.append(
        Paragraph(safe_insights, styles["BodyText"])
    )

    elements.append(Spacer(1, 20))

    # Helper function to add tables
    def add_table(title, dataframe):

        elements.append(
            Paragraph(title, styles["Heading2"])
        )

        table_data = [
            [str(column) for column in dataframe.columns]
        ]

        for row in dataframe.values.tolist():

            table_data.append([
                str(value) for value in row
            ])

        table = Table(
            table_data,
            repeatRows=1,
            hAlign="LEFT"
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ]))

        elements.append(table)
        elements.append(Spacer(1, 15))

    # Category performance
    add_table(
        "Category Performance",
        business_results["Category"].reset_index()
    )

    # Regional performance
    add_table(
        "Regional Performance",
        business_results["Region"].reset_index()
    )

    # Top 10 states by sales
    top_states = business_results["State"].sort_values(
        by="Total_Sales",
        ascending=False
    ).head(10)

    add_table(
        "Top 10 States by Sales",
        top_states.reset_index()
    )

    # Bottom 10 states by profit
    bottom_states = business_results["State"].sort_values(
        by="Total_Profit",
        ascending=True
    ).head(10)

    add_table(
        "Bottom 10 States by Profit",
        bottom_states.reset_index()
    )

    # Top 10 products by sales
    top_products = business_results["Product"].sort_values(
        by="Total_Sales",
        ascending=False
    ).head(10)

    add_table(
        "Top 10 Products by Sales",
        top_products.reset_index()
    )

    # Bottom 10 products by profit
    bottom_products = business_results["Product"].sort_values(
        by="Total_Profit",
        ascending=True
    ).head(10)

    add_table(
        "Bottom 10 Products by Profit",
        bottom_products.reset_index()
    )

    # Yearly performance
    add_table(
        "Yearly Performance",
        business_results["Yearly"].reset_index()
    )

    # Discount analysis
    add_table(
        "Discount Analysis",
        business_results["Discount"].reset_index()
    )

    # Generate PDF
    doc.build(elements)

    buffer.seek(0)

    return buffer.getvalue()


st.set_page_config(
    page_title="AI Business Insights Generator"
)
# Application title
st.title("AI Business Insights Generator")

st.write(
    "Upload your business dataset to generate "
    "automated business analysis and AI-powered insights."
)
st.subheader("Required CSV Columns")

st.write(
    "Your dataset must contain the following 10 columns:"
)

required_columns = [
    "Sales", "Profit", "Order ID", "Category",
    "Region", "State", "Product Name",
    "Quantity", "Order Date", "Discount"
]

st.write(", ".join(required_columns))

st.subheader("Important Notes")

st.write("""
- Column names must match exactly.
- Sales, Profit, Quantity and Discount must be numeric.
- Order Date must contain valid dates.
- Each row should represent an order line item.
""")

st.subheader("Don't have a dataset?")

st.markdown(
    "Download the [Sample Superstore dataset from Kaggle]"
    "(https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) "
    "to test the application."
)


# File uploader
uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file, encoding="cp1252")

     # Check required columns
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        st.error("Your CSV file is missing required columns:")
        st.write(missing_columns)
        st.stop()

    st.success("File uploaded successfully!")

    st.write("Dataset Preview")

    st.dataframe(df.head())

    st.write("Dataset Shape:", df.shape)

    # Run business analysis
    business_results = analyze_business_data(df)

    # Display overall KPIs
    st.subheader("Overall Business Performance")

    kpis = business_results["KPIs"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Sales", f"${kpis['Total Sales']:,.2f}")
    col2.metric("Total Profit", f"${kpis['Total Profit']:,.2f}")
    col3.metric("Total Orders", f"{kpis['Total Orders']:,}")
    col4.metric("Profit Margin", f"{kpis['Profit Margin (%)']:.2f}%")

    st.subheader("Category Performance")

    category_results = business_results["Category"]

    st.dataframe(category_results.round(2))

    st.write("Sales by Category")

    st.bar_chart(category_results["Total_Sales"])

    # Regional Analysis
    st.subheader("Regional Performance")

    region_results = business_results["Region"]

    st.dataframe(region_results.round(2))

    st.write("Sales by Region")

    st.bar_chart(region_results["Total_Sales"]) 

    # State Analysis
    st.subheader("State Performance")

    state_results = business_results["State"]

    st.write("Top 10 States by Sales")

    top_states = state_results.sort_values(
        by="Total_Sales", ascending=False
    ).head(10)

    st.dataframe(top_states.round(2))

    st.write("Bottom 10 States by Profit")

    bottom_states = state_results.sort_values(
        by="Total_Profit", ascending=True
    ).head(10)

    st.dataframe(bottom_states.round(2))

        # Product Analysis
    st.subheader("Product Performance")

    product_results = business_results["Product"]

    st.write("Top 10 Products by Sales")

    st.dataframe(
        product_results.sort_values(
            by="Total_Sales", ascending=False
        ).head(10).round(2)
    )

    st.write("Bottom 10 Products by Profit")

    st.dataframe(
        product_results.sort_values(
            by="Total_Profit", ascending=True
        ).head(10).round(2)
    )

        # Yearly Analysis
    st.subheader("Yearly Performance")

    yearly_results = business_results["Yearly"]

    st.dataframe(yearly_results.round(2))

    st.write("Yearly Sales Trend")

    st.line_chart(yearly_results["Total_Sales"])

    st.write("Yearly Profit Trend")

    st.line_chart(yearly_results["Total_Profit"])

    # Discount Analysis
    st.subheader("Discount and Profitability Analysis")

    discount_results = business_results["Discount"]

    st.dataframe(discount_results.round(2))

    st.write("Profit by Discount Level")

    st.bar_chart(discount_results["Total_Profit"])

if uploaded_file is not None:

    if st.button("Generate AI Business Insights"):

        prompt = create_business_prompt(business_results)

        with st.spinner("Analysing your business data..."):

            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )

                st.subheader("AI-Generated Business Insights")

                with st.container(border=True):
                    st.markdown(response.text)
                
                pdf_file = create_pdf_report(
                business_results,
                response.text
                )

                st.download_button(
                    label="Download Business Report (PDF)",
                    data=pdf_file,
                    file_name="business_performance_report.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Unable to generate insights: {e}")