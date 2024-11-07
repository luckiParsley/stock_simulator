import yfinance as yf
from flask import session
from datetime import timedelta
import plotly.graph_objs as go
import pandas as pd
import logging


class Stock:
    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol
        self.ticker = yf.Ticker(ticker_symbol)

    def fetch_historical_data(self, end_date=None):
        """Fetch historical data from yfinance"""
        try:
            start_date = session.get("start_date") - timedelta(days=365)
            if end_date is None:
                end_date = session.get("current_date")

            historical_data = yf.download(
                self.ticker_symbol, start_date, end_date, interval="1d"
            )
            historical_data.index = historical_data.index.tz_localize(None)
            return historical_data
        except Exception as e:
            logging.error(f"Error fetching historical data: {str(e)}")
            return None

    def fetch_metadata(self):
        """Fetch stock metadata"""
        try:
            metadata = self.ticker.info
            return {
                "Symbol": self.ticker_symbol,
                "longName": metadata.get("longName", "N/A"),
                "industry": metadata.get("industry", "N/A"),
                "sector": metadata.get("sector", "N/A"),
                "website": metadata.get("website", "N/A"),
                "longBusinessSummary": metadata.get("longBusinessSummary", "N/A"),
            }
        except Exception as e:
            logging.error(f"Error fetching metadata: {str(e)}")
            return None

    def fetch_recent_price(self, historical_data, current_date):
        """Get the price for a specific date"""
        try:
            current_date = pd.to_datetime(current_date)
            current_date = current_date.replace(tzinfo=None)

            if current_date in historical_data.index:
                return (
                    round(historical_data.loc[current_date]["Close"], 2),
                    current_date,
                )

            # If exact date not found, get the most recent previous date
            available_dates = historical_data.index[
                historical_data.index <= current_date
            ]
            if len(available_dates) > 0:
                closest_date = available_dates[-1]
                return (
                    round(historical_data.loc[closest_date]["Close"], 2),
                    closest_date,
                )

            return None, None
        except Exception as e:
            logging.error(f"Error fetching recent price: {str(e)}")
            return None, None

    def generate_candlestick_chart(self, current_date=None):
        """Generate a candlestick chart"""
        try:
            if current_date is None:
                current_date = session.get("current_date")

            historical_data = self.fetch_historical_data(current_date)
            if historical_data is None:
                return None

            historical_data.index = pd.to_datetime(historical_data.index)
            historical_data.index = historical_data.index.tz_localize(None)

            filtered_data = historical_data.loc[historical_data.index <= current_date]

            candlestick = go.Figure(
                data=[
                    go.Candlestick(
                        x=filtered_data.index,
                        open=filtered_data["Open"],
                        high=filtered_data["High"],
                        low=filtered_data["Low"],
                        close=filtered_data["Close"],
                        name="Candlesticks",
                    )
                ]
            )

            candlestick.update_layout(
                title="Price History",
                yaxis_title="Price",
                xaxis_title="Date",
                template="plotly_white",
                height=500,  # Match the CSS height
                margin=dict(l=40, r=40, t=30, b=30),
            )

            return candlestick.to_html(full_html=False, include_plotlyjs=True)
        except Exception as e:
            logging.error(f"Error generating candlestick chart: {str(e)}")
            return None
