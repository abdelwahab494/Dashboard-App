import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for card and background styling
st.markdown("""
    <style>
    body, .stApp {
        background-color: #f8fafc !important;
    }
    .card {
        background-color: #e2e8f0;
        border-radius: 18px;
        padding: 2rem 2rem 2rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(60, 120, 216, 0.07);
    }
    .section-title {
        color: #2563eb;
        font-size: 1.6rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #e2e8f0;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    main_data = "Data/Data After Milestone 1.csv"
    original_data = "Data/Original Data.csv"
    sales = pd.read_csv(main_data, encoding="latin-1")
    main = pd.read_csv(original_data, encoding="latin-1")
    return sales, main

sales, main = load_data()

# Calculate metrics
total_revenue = sales["Total_sales"].sum().round(2)
total_profit = sales["Profit"].sum().round(2)
total_units_sold = sales["Quantity"].sum().round(2)
avg_discount = (main["Discount"].mean() * 100).round(2)
total_orders = sales["Order Date"].count()
avg_shipping_time = sales["Shipping Time (Days)"].mean().round(2)

# Title
st.markdown('<h1 style="text-align:center; color:#3b82f6; font-weight:800;">Sales Dashboard</h1>', unsafe_allow_html=True)

# KPIs in cards inside a flex container
total_revenue_card = f'''
<div class="metric-card card" style="flex:1; margin:0 10px;">
    <div style="font-weight:600; color:#2d3748; font-size:1.1rem;">Total Revenue</div>
    <div style="font-size:2rem; font-weight:700; color:#2563eb;">${total_revenue:,.2f}</div>
</div>'''
total_profit_card = f'''
<div class="metric-card card" style="flex:1; margin:0 10px;">
    <div style="font-weight:600; color:#2d3748; font-size:1.1rem;">Total Profit</div>
    <div style="font-size:2rem; font-weight:700; color:#2563eb;">${total_profit:,.2f}</div>
</div>'''
total_units_card = f'''
<div class="metric-card card" style="flex:1; margin:0 10px;">
    <div style="font-weight:600; color:#2d3748; font-size:1.1rem;">Total Units Sold</div>
    <div style="font-size:2rem; font-weight:700; color:#2563eb;">{total_units_sold:,.0f}</div>
</div>'''
avg_discount_card = f'''
<div class="metric-card card" style="flex:1; margin:0 10px;">
    <div style="font-weight:600; color:#2d3748; font-size:1.1rem;">Average Discount</div>
    <div style="font-size:2rem; font-weight:700; color:#2563eb;">{avg_discount:.1f}%</div>
</div>'''
total_orders_card = f'''
<div class="metric-card card" style="flex:1; margin:0 10px;">
    <div style="font-weight:600; color:#2d3748; font-size:1.1rem;">Total Orders</div>
    <div style="font-size:2rem; font-weight:700; color:#2563eb;">{total_orders:,}</div>
</div>'''
avg_shipping_card = f'''
<div class="metric-card card" style="flex:1; margin:0 10px;">
    <div style="font-weight:600; color:#2d3748; font-size:1.1rem;">AVG Shipping Time</div>
    <div style="font-size:2rem; font-weight:700; color:#2563eb;">{avg_shipping_time:.2f} days</div>
</div>'''

kpi_row = f'''
<div style="display:flex; flex-direction:row; justify-content:space-between; align-items:stretch; margin-bottom:2rem;">
    {total_revenue_card}
    {total_profit_card}
    {total_units_card}
    {avg_discount_card}
    {total_orders_card}
    {avg_shipping_card}
</div>'''

st.markdown(kpi_row, unsafe_allow_html=True)

st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

# --- Sales & Profit Over Time ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Sales & Profit Over Time</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1,2])
with col1:
    date_range = st.date_input(
        "Select Date Range",
        value=(pd.to_datetime(sales['Order Date'].min()), pd.to_datetime(sales['Order Date'].max())),
        min_value=pd.to_datetime(sales['Order Date'].min()),
        max_value=pd.to_datetime(sales['Order Date'].max())
    )
    measure = st.selectbox("Select Measure", ["Sales", "Profit"], key="fig1_measure")
    ma_window = st.select_slider("Moving Average Window", options=[7, 14, 30], value=7, key="fig1_ma")
with col2:
    filtered_df = sales[
        (sales['Order Date'] >= str(date_range[0])) & 
        (sales['Order Date'] <= str(date_range[1]))
    ].copy()
    filtered_df = filtered_df.sort_values('Order Date')
    filtered_df['Moving_Avg'] = filtered_df[measure].rolling(window=ma_window).mean()
    fig1 = px.line(
        filtered_df, 
        x='Order Date', 
        y='Moving_Avg', 
        title=f'{measure} Over Time',
        color_discrete_sequence=["#3b82f6"]
    )
    fig1.update_layout(
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#e2e8f0',
        font_color='#2d3748',
        title_x=0.5,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Sales by Region, Market or Country ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Sales by Region, Market or Country</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1,2])
with col1:
    selected_category = st.selectbox(
        "Select Category",
        ["Region", "Market", "Country"],
        key="fig2_cat"
    )
    selected_metric = st.radio(
        "Select Metric",
        ["Sales", "Profit"],
        horizontal=True,
        key="fig2_metric"
    )
with col2:
    grouped_df = sales.groupby(selected_category)[selected_metric].sum().reset_index()
    if selected_category == "Country":
        fig2 = px.choropleth(
            grouped_df,
            locations="Country",
            locationmode="country names",
            color=selected_metric,
            title=f"{selected_metric} by Country",
            color_continuous_scale=["#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8"]
        )
    else:
        fig2 = px.bar(
            grouped_df,
            x=selected_category,
            y=selected_metric,
            title=f"{selected_metric} by {selected_category}",
            text_auto=True,
            color=selected_metric,
            color_continuous_scale=["#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8"]
        )
    fig2.update_layout(
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#e2e8f0',
        font_color='#2d3748',
        title_x=0.5,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Top Performing Products and Categories ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Top Performing Products and Categories</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1,2])
with col1:
    chart_type = st.selectbox(
        "Select Chart Type",
        ["Horizontal Bar Chart", "Treemap"],
        key="fig3_type"
    )
    measure = st.selectbox(
        "Select Measure",
        ["Sales", "Profit", "Quantity"],
        key="fig3_measure"
    )
    selected_categories = st.multiselect(
        "Select Categories",
        options=sales['Category'].unique(),
        default=["Technology", "Furniture", "Office Supplies"],
        key="fig3_cats"
    )
with col2:
    filtered_df = sales[sales['Category'].isin(selected_categories)]
    grouped_df = filtered_df.groupby(['Category', 'Sub-Category'])[measure].sum().reset_index()
    if chart_type == 'Treemap':
        fig3 = px.treemap(
            grouped_df,
            path=['Category', 'Sub-Category'],
            values=measure,
            color=measure,
            title=f'{measure} by Category and Sub-Category',
            color_continuous_scale=["#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8"]
        )
    else:
        fig3 = px.bar(
            grouped_df,
            x=measure,
            y='Sub-Category',
            orientation='h',
            color=measure,
            text_auto=True,
            title=f'{measure} by Category and Sub-Category',
            color_continuous_scale=["#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8"]
        )
    fig3.update_layout(
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#e2e8f0',
        font_color='#2d3748',
        title_x=0.5,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Seasonality & Time Patterns ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Seasonality & Time Patterns</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1,2])
with col1:
    category = st.selectbox(
        "Select Category",
        options=sales['Category'].unique(),
        key="fig4_cat"
    )
    view_type = st.radio(
        "Select View",
        ["Day of Week vs. Month", "Monthly Trends"],
        horizontal=True,
        key="fig4_view"
    )
with col2:
    filtered_df = sales[sales['Category'] == category].copy()
    filtered_df['Order Date'] = pd.to_datetime(filtered_df['Order Date'])
    filtered_df['Month'] = filtered_df['Order Date'].dt.strftime('%b')
    filtered_df['Day of Week'] = filtered_df['Order Date'].dt.day_name()
    if view_type == 'Day of Week vs. Month':
        pivot_table = filtered_df.pivot_table(
            index='Day of Week',
            columns='Month',
            values='Total_sales',
            aggfunc='sum'
        )
        fig4 = px.imshow(
            pivot_table,
            labels=dict(x="Month", y="Day of Week", color="Sales"),
            title=f"Sales Heatmap for {category}",
            color_continuous_scale=["#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8"]
        )
    else:
        monthly_sales = filtered_df.groupby('Month')['Total_sales'].sum().reset_index()
        fig4 = px.line(
            monthly_sales,
            x='Month',
            y='Total_sales',
            title=f"Monthly Sales Trend for {category}",
            color_discrete_sequence=['#3b82f6']
        )
    fig4.update_layout(
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#e2e8f0',
        font_color='#2d3748',
        title_x=0.5,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig4, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Discount Impact on Profit ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Discount Impact on Profit</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1,2])
with col1:
    discount_range = st.slider(
        "Select Discount Range",
        min_value=float(main['Discount'].min()),
        max_value=float(main['Discount'].max()),
        value=(float(main['Discount'].min()), float(main['Discount'].max())),
        step=0.05,
        key="fig5_range"
    )
    selected_category = st.selectbox(
        "Select Category",
        options=['All'] + list(sales['Category'].unique()),
        key="fig5_cat"
    )
with col2:
    filtered_df = sales[
        (sales['Discount'] >= discount_range[0]) & 
        (sales['Discount'] <= discount_range[1])
    ].copy()
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    fig5 = px.scatter(
        filtered_df,
        x='Discount',
        y='Profit',
        color='Profit',
        title="Impact of Discount on Profit",
        trendline="ols",
        color_continuous_scale=["#93c5fd", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8"]
    )
    fig5.update_traces(marker=dict(size=8))
    fig5.update_layout(
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#e2e8f0',
        font_color='#2d3748',
        title_x=0.5,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig5, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True) 