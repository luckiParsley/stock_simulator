# services/market_data_service.py
from ..models.stock import Stock
from flask import session
import logging
import numpy as np


class MarketDataService:
    @staticmethod
    def get_stock_data(symbol, current_date):
        """Get all stock data including price, metadata, and charts"""
        try:
            stock = Stock(symbol)

            # Get historical data
            historical_data = stock.fetch_historical_data()
            if historical_data is None:
                return None

            # Get current price
            current_price, price_date = stock.fetch_recent_price(
                historical_data, current_date
            )
            if current_price is None:
                return None

            # Ensure current_price is a single float value
            if isinstance(current_price, (list, np.ndarray)):
                current_price = float(current_price[-1])

            # Get metadata
            metadata = stock.fetch_metadata()
            if metadata is None:
                metadata = {
                    "Symbol": symbol,
                    "longName": symbol,
                    "industry": "N/A",
                    "sector": "N/A",
                    "website": "N/A",
                    "longBusinessSummary": "N/A",
                }

            # Generate chart
            chart = stock.generate_candlestick_chart(current_date)

            return {
                "price": current_price,
                "price_date": price_date,
                "metadata": metadata,
                "historical_data": historical_data,
                "chart": chart,
            }

        except Exception as e:
            logging.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None
