import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime


df = pd.read_csv("Orders.csv", encoding="latin-1")


df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)


df["Sales"] = df["Sales"].replace(r'[\$,\s]', '', regex=True)
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0)

df["Profit"] = df["Profit"].replace(r'[\$,\s]', '', regex=True)
df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce").fillna(0)

df["Quantity"] = df["Quantity"].replace(r'[\$,\s]', '', regex=True)
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Sales Dashboard"


def make_card(title, value_id):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title",
                     style={"textAlign": "center", "color": "#a9a9a9"}),
            html.H4(id=value_id,
                     style={"textAlign": "center", "color": "white", "fontWeight": "bold"}),
        ]),
        style={
            "backgroundColor": "#1e1e2f",
            "border": "1px solid #444",
            "borderRadius": "10px",
            "margin": "5px",
        },
    )


app.layout = dbc.Container(fluid=True, style={"backgroundColor": "#0b0b1a", "minHeight": "100vh", "padding": "20px"}, children=[


    dbc.Row([

        dbc.Col(
            html.H3("🛒 SalesHub",
                     style={"color": "white", "margin": "0", "fontWeight": "bold"}),
            width=2,
            style={"display": "flex", "alignItems": "center"},
        ),

        dbc.Col([
            html.Label("Start Date", style={"color": "white", "fontSize": "12px"}),
            dcc.DatePickerSingle(
                id="start-date",
                min_date_allowed=df["Order Date"].min(),
                max_date_allowed=df["Order Date"].max(),
                date=df["Order Date"].min(),
                display_format="DD/MM/YYYY",
                style={"marginRight": "10px"},
            ),
            html.Label("End Date", style={"color": "white", "fontSize": "12px", "marginLeft": "10px"}),
            dcc.DatePickerSingle(
                id="end-date",
                min_date_allowed=df["Order Date"].min(),
                max_date_allowed=df["Order Date"].max(),
                date=df["Order Date"].max(),
                display_format="DD/MM/YYYY",
            ),
        ], width=4, style={"display": "flex", "alignItems": "center", "gap": "5px"}),
        # Title
        dbc.Col(
            html.H2("Sales Dashboard",
                     style={"color": "white", "textAlign": "center", "margin": "0"}),
            width=3,
            style={"display": "flex", "alignItems": "center", "justifyContent": "center"},
        ),
        # Timestamp
        dbc.Col(
            html.Div(id="timestamp",
                     style={"color": "#a9a9a9", "textAlign": "right", "fontSize": "14px"}),
            width=3,
            style={"display": "flex", "alignItems": "center", "justifyContent": "flex-end"},
        ),
    ], style={"marginBottom": "20px", "padding": "10px",
              "backgroundColor": "#1e1e2f", "borderRadius": "10px"}),


    dcc.Interval(id="interval", interval=60 * 1000, n_intervals=0),


    dbc.Row([
        dbc.Col(make_card("Total Sales", "total-sales"), width=3),
        dbc.Col(make_card("Total Profit", "total-profit"), width=3),
        dbc.Col(make_card("Total Customers", "total-customers"), width=3),
        dbc.Col(make_card("Total Orders", "total-orders"), width=3),
    ], style={"marginBottom": "20px"}),


    dbc.Row([
        dbc.Col(
            dcc.Graph(id="profit-histogram"),
            width=6,
        ),
        dbc.Col(
            dcc.Graph(id="category-pie"),
            width=6,
        ),
    ], style={"marginBottom": "20px"}),


    dbc.Row([
        dbc.Col(
            dcc.Graph(id="top5-bar"),
            width=6,
        ),
        dbc.Col(
            dcc.Graph(id="own-chart"),
            width=6,
        ),
    ]),
])


@app.callback(
    Output("timestamp", "children"),
    Input("interval", "n_intervals"),
)
def update_timestamp(n):
    now = datetime.now().strftime("%d %b %Y  %H:%M:%S")
    return f"Last updated: {now}"


@app.callback(
    Output("total-sales", "children"),
    Output("total-profit", "children"),
    Output("total-customers", "children"),
    Output("total-orders", "children"),
    Output("profit-histogram", "figure"),
    Output("category-pie", "figure"),
    Output("top5-bar", "figure"),
    Output("own-chart", "figure"),
    Input("start-date", "date"),
    Input("end-date", "date"),
)
def update_dashboard(start, end):

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    filtered = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)]


    total_sales = f"${filtered['Sales'].sum():,.2f}"
    total_profit = f"${filtered['Profit'].sum():,.2f}"
    total_customers = f"{filtered['Customer ID'].nunique():,}"
    total_orders = f"{filtered['Order ID'].nunique():,}"


    profit_by_date = filtered.groupby(filtered["Order Date"].dt.to_period("M")) \
                             .agg({"Profit": "sum"}).reset_index()
    profit_by_date["Order Date"] = profit_by_date["Order Date"].astype(str)

    fig_hist = px.bar(
        profit_by_date, x="Order Date", y="Profit",
        title="Sum of Profit by Order Date",
        labels={"Profit": "Profit ($)", "Order Date": "Month"},
        color_discrete_sequence=["#636EFA"],
    )
    fig_hist.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1e1e2f",
        plot_bgcolor="#1e1e2f",
        title_font_size=16,
        xaxis_tickangle=-45,
    )


    qty_by_cat = filtered.groupby("Category")["Quantity"].sum().reset_index()

    fig_pie = px.pie(
        qty_by_cat, names="Category", values="Quantity",
        title="Quantity % by Category",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1e1e2f",
        plot_bgcolor="#1e1e2f",
        title_font_size=16,
    )


    top5 = filtered.groupby("Product Name")["Sales"].sum() \
                   .nlargest(5).reset_index()

    fig_top5 = px.bar(
        top5, x="Sales", y="Product Name",
        orientation="h",
        title="Top 5 Products by Sales",
        labels={"Sales": "Sales ($)", "Product Name": ""},
        color_discrete_sequence=["#00CC96"],
    )
    fig_top5.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1e1e2f",
        plot_bgcolor="#1e1e2f",
        title_font_size=16,
        yaxis={"categoryorder": "total ascending"},
    )


    sales_region = filtered.groupby(["Region", "Category"])["Sales"].sum().reset_index()

    fig_own = px.treemap(
        sales_region, path=["Region", "Category"], values="Sales",
        title="Sales Distribution by Region & Category",
        color="Sales",
        color_continuous_scale="Blues",
    )
    fig_own.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1e1e2f",
        plot_bgcolor="#1e1e2f",
        title_font_size=16,
    )

    return (total_sales, total_profit, total_customers, total_orders,
            fig_hist, fig_pie, fig_top5, fig_own)



if __name__ == "__main__":
    app.run(debug=True, port=8051)