import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Load the dataset
df = pd.read_csv('dashboard\\task_dashboarding_dataset.csv')

# Data Cleansing
# Drop duplicates
df = df.drop_duplicates()

# Handle missing values - fill missing values in numerical columns with 0 or median
df['quantity_sold'].fillna(0)
df['selling_price_per_unit'].fillna(df['selling_price_per_unit'].median())
df['purchasing_price_per_unit'].fillna(df['purchasing_price_per_unit'].median())
df['order_created'] = pd.to_datetime(df['order_created'], errors='coerce')  # Handle any non-datetime entries

# Drop rows where critical fields like 'order_id' or 'sku' are missing
df.dropna(subset=['order_id', 'sku'])

# Calculate profit and revenue
df['profit'] = (df['selling_price_per_unit'] - df['purchasing_price_per_unit']) * df['quantity_sold']
df['total_revenue'] = df['selling_price_per_unit'] * df['quantity_sold']
df['total_cost'] = df['purchasing_price_per_unit'] * df['quantity_sold']

# Metrics (KPIs)
total_revenue = df['total_revenue'].sum()
total_profit = df['total_revenue'].sum() - df['total_cost'].sum()
profit_margin = (total_profit / total_revenue) * 100
avg_order_value = total_revenue / df['order_id'].nunique()

# Visualization 1: Top 10 Selling Products by Quantity Sold
top_selling_skus = df.groupby('sku')['quantity_sold'].sum().nlargest(10).reset_index()
fig1 = px.bar(top_selling_skus, x='sku', y='quantity_sold', title="Top 10 Selling Products by Quantity Sold")

# Visualization 2: Top 10 Products Revenue vs Cost
top_revenue_skus = df.groupby('sku').agg({'total_revenue': 'sum', 'total_cost': 'sum'}).nlargest(10, 'total_revenue').reset_index()
fig2 = go.Figure()
fig2.add_trace(go.Bar(x=top_revenue_skus['sku'], y=top_revenue_skus['total_revenue'], name="Revenue"))
fig2.add_trace(go.Bar(x=top_revenue_skus['sku'], y=top_revenue_skus['total_cost'], name="Cost"))
fig2.update_layout(barmode='group', title="Top 10 Products: Revenue vs Cost")

# Visualization 3: Top 10 Suppliers by Profit
top_suppliers_profit = df.groupby('supplier_id')['profit'].sum().nlargest(10).reset_index()
fig3 = px.bar(top_suppliers_profit, x='supplier_id', y='profit', title="Top 10 Suppliers by Profit")

# Visualization 4: Orders by Hour of Day
df['hour_of_day'] = df['order_created'].dt.hour
orders_by_hour = df.groupby('hour_of_day')['order_id'].count().reset_index()
fig4 = px.line(orders_by_hour, x='hour_of_day', y='order_id', title="Number of Orders by Hour of the Day")

# New Visualization: Sales by Category (Pie Chart)
sales_by_category = df.groupby('item_category')['quantity_sold'].sum().reset_index()
fig5 = px.pie(sales_by_category, values='quantity_sold', names='item_category', title="Sales by Item Category")

# New Visualization: Top Selling Products by Revenue (Bar Chart)
top_selling_products_revenue = df.groupby('sku')['total_revenue'].sum().nlargest(10).reset_index()
fig6 = px.bar(top_selling_products_revenue, x='sku', y='total_revenue', title="Top 10 Selling Products by Revenue")

# Dash Layout - Improved Presentation
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    # Header
    dbc.Row(dbc.Col(html.H2("Sales Dashboard", className="text-center mb-4", style={"fontWeight": "bold", "color": "#3d7c98"}))),
    
    # KPI Metrics
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Total Revenue", className="card-title"),
                html.P(f"${total_revenue:,.2f}", className="card-text", style={"fontSize": "1.5em", "color": "#28a745"})
            ])
        ], className="shadow p-3 mb-5 bg-white rounded"), md=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Profit Margin", className="card-title"),
                html.P(f"{profit_margin:.2f}%", className="card-text", style={"fontSize": "1.5em", "color": "#17a2b8"})
            ])
        ], className="shadow p-3 mb-5 bg-white rounded"), md=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Average Order Value", className="card-title"),
                html.P(f"${avg_order_value:,.2f}", className="card-text", style={"fontSize": "1.5em", "color": "#ffc107"})
            ])
        ], className="shadow p-3 mb-5 bg-white rounded"), md=4),
    ], className="mb-4"),
    
    # Row 1: Top Selling Products & Revenue vs Cost
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig1), md=6),
        dbc.Col(dcc.Graph(figure=fig2), md=6),
    ]),
    
    # Row 2: Top Suppliers by Profit & Orders by Hour
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig3), md=6),
        dbc.Col(dcc.Graph(figure=fig4), md=6),
    ]),
    
    # Row 3: Sales by Category (Pie Chart) & Top Selling Products by Revenue
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig5), md=6),
        dbc.Col(dcc.Graph(figure=fig6), md=6),
    ]),
    
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)
