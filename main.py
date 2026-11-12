import pandas as pd


def calculate_kpis(df):

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()

    average_order_value = total_sales / total_orders
    profit_margin = (total_profit / total_sales) * 100

    kpis = {
        "Total Sales": total_sales,
        "Total Profit": total_profit,
        "Total Orders": total_orders,
        "Average Order Value": average_order_value,
        "Profit Margin (%)": profit_margin
    }

    return kpis


def analyze_category(df):

    category_analysis = df.groupby("Category").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Orders=("Order ID", "nunique")
    )

    category_analysis["Profit_Margin_%"] = (
        category_analysis["Total_Profit"] /
        category_analysis["Total_Sales"] * 100
    )

    return category_analysis


def analyze_region(df):

    region_analysis = df.groupby("Region").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Orders=("Order ID", "nunique")
    )

    region_analysis["Profit_Margin_%"] = (
        region_analysis["Total_Profit"] /
        region_analysis["Total_Sales"] * 100
    )

    return region_analysis


def analyze_state(df):

    state_analysis = df.groupby("State").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Orders=("Order ID", "nunique")
    )

    state_analysis["Profit_Margin_%"] = (
        state_analysis["Total_Profit"] /
        state_analysis["Total_Sales"] * 100
    )

    return state_analysis


def analyze_product(df):

    product_analysis = df.groupby("Product Name").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Quantity=("Quantity", "sum")
    )

    return product_analysis

def analyze_yearly(df):

    df = df.copy()

    df["Order Date"] = pd.to_datetime(df["Order Date"])

    df["Year"] = df["Order Date"].dt.year

    yearly_analysis = df.groupby("Year").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Orders=("Order ID", "nunique")
    )

    yearly_analysis["Sales_Growth_%"] = (
        yearly_analysis["Total_Sales"].pct_change() * 100
    )

    yearly_analysis["Profit_Growth_%"] = (
        yearly_analysis["Total_Profit"].pct_change() * 100
    )

    return yearly_analysis

def analyze_discount(df):

    discount_analysis = df.groupby("Discount").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Orders=("Order ID", "nunique")
    )

    discount_analysis["Profit_Margin_%"] = (
        discount_analysis["Total_Profit"] /
        discount_analysis["Total_Sales"] * 100
    )

    return discount_analysis

def analyze_business_data(df):

    results = {}

    results["KPIs"] = calculate_kpis(df)
    results["Category"] = analyze_category(df)
    results["Region"] = analyze_region(df)
    results["State"] = analyze_state(df)
    results["Product"] = analyze_product(df)
    results["Yearly"] = analyze_yearly(df)
    results["Discount"] = analyze_discount(df)

    return results

if __name__ == "__main__":

    df = pd.read_csv("Sample - Superstore.csv", encoding="cp1252")

    business_results = analyze_business_data(df)

    print("\n========== OVERALL KPIs ==========")
    print(business_results["KPIs"])
    