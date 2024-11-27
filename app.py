from flask import Flask, render_template, request
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Polygon.io API Key
API_KEY = 'J7HkZy97OoCKoHu5wvlK9oh7QOmoJ_5j'

# Function to fetch stock data for a specific month
def get_historical_data(ticker, month):
    year = datetime.now().year
    start_date = f"{year}-{month:02d}-01"
    end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=30)).strftime('%Y-%m-%d')

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?apiKey={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json().get("results", [])
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['t'], unit='ms')
        df.set_index('date', inplace=True)
        return df[['c']]  # Closing prices
    else:
        return None

# Predict stock prices and calculate model accuracy
def predict_stock_prices(df):
    df['day'] = np.arange(len(df))
    X = df[['day']]
    y = df['c']

    models = {
        "Linear Regression": LinearRegression(),
        "SVM": SVR(kernel='rbf', C=1e3, gamma=0.1),
        "Random Forest": RandomForestRegressor(n_estimators=100),
    }

    predictions = {}
    accuracies = {}

    for name, model in models.items():
        model.fit(X, y)
        future_days = np.arange(len(df), len(df) + 7).reshape(-1, 1)
        pred = model.predict(future_days)
        predictions[name] = pred

        # Calculate MAPE accuracy
        y_pred = model.predict(X)
        accuracy = 100 - mean_absolute_percentage_error(y, y_pred) * 100
        accuracies[name] = accuracy

    return predictions, accuracies

# Function to fetch company details
def get_company_details(ticker):
    company_info = {
        "AAPL": {"name": "Apple Inc.", "description": "A multinational technology company that designs, develops, and sells consumer electronics, computer software, and online services."},
        "MSFT": {"name": "Microsoft Corp.", "description": "A technology company that develops, licenses, and supports a wide range of software products, services, and devices."},
        "GOOGL": {"name": "Alphabet Inc.", "description": "The parent company of Google, focusing on technology and internet services."},
        # Add more companies as needed
    }
    return company_info.get(ticker, {"name": "Unknown", "description": "No details available."})

# Generate profit/loss graph
def generate_profit_loss_graph(df, predictions):
    current_price = df['c'].iloc[-1]
    profit_loss = [pred - current_price for pred in predictions["Linear Regression"]]

    fig = go.Figure(data=go.Bar(x=list(range(len(profit_loss))), y=profit_loss, name='Profit/Loss'))
    fig.update_layout(title="Potential Profit and Loss", xaxis_title="Future Days", yaxis_title="Profit/Loss")
    
    return pio.to_html(fig, full_html=False)

# Generate user buy/sell statistics graph
def generate_user_statistics_graphs():
    buy_users = 50  # Placeholder value
    sell_users = 30  # Placeholder value
    
    fig = go.Figure(data=[
        go.Bar(name='Users Buying', x=['Buying', 'Selling'], y=[buy_users, sell_users])
    ])
    fig.update_layout(title="User Buy/Sell Statistics", yaxis_title="Number of Users")

    return pio.to_html(fig, full_html=False)

# Generate multiple graphs for data visualization
def generate_graphs(df, predictions, accuracies):
    graphs = []

    # Graph 1: Historical Prices Line Graph
    fig1 = go.Figure(data=[go.Scatter(x=df.index, y=df['c'], mode='lines+markers', name='Closing Price')])
    fig1.update_layout(title="Historical Closing Prices", xaxis_title="Date", yaxis_title="Price")
    graphs.append(pio.to_html(fig1, full_html=False))

    # Graph 2: Weekly Predictions (Bar Chart)
    future_dates = pd.date_range(df.index[-1] + timedelta(days=1), periods=7)
    fig2 = px.bar(x=future_dates, y=predictions["Linear Regression"], labels={'x': 'Date', 'y': 'Predicted Price'},
                  title="Weekly Predictions (Linear Regression)")
    graphs.append(pio.to_html(fig2, full_html=False))

    # Graph 3: Accuracy Comparison (Pie Chart)
    fig3 = px.pie(values=list(accuracies.values()), names=list(accuracies.keys()), title="Model Accuracy Comparison")
    graphs.append(pio.to_html(fig3, full_html=False))

    return graphs




@app.route('/', methods=['GET', 'POST'])
def home():
    predictions, accuracies, graphs, company_details, decision, summary = None, None, [], {}, "", ""

    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        month = int(request.form['month'])

        df = get_historical_data(ticker, month)
        company_details = get_company_details(ticker)

        if df is not None:
            predictions, accuracies = predict_stock_prices(df)
            graphs = generate_graphs(df, predictions, accuracies)
            profit_loss_graph = generate_profit_loss_graph(df, predictions)
            graphs.append(profit_loss_graph)

            user_stats_graph = generate_user_statistics_graphs()
            graphs.append(user_stats_graph)

            # Determine predicted and current prices
            predicted_price = predictions["Linear Regression"][-1]
            current_price = df['c'].iloc[-1]

            # Make buy/sell decision
            if predicted_price > current_price:
                decision = "Buy"
                summary = f"The predicted price is ${predicted_price:.2f}, which is higher than the current price of ${current_price:.2f}. It is recommended to buy."
            else:
                decision = "Sell"
                summary = f"The predicted price is ${predicted_price:.2f}, which is lower than the current price of ${current_price:.2f}. It is recommended to sell."

    return render_template('index.html', graphs=graphs, accuracies=accuracies, company_details=company_details, decision=decision, summary=summary)




if __name__ == '__main__':
    app.run(debug=True)


