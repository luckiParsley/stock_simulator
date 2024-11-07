# views/stock.py
from flask import Blueprint, render_template, session, redirect, request, url_for
from ..services.market_data_service import MarketDataService
import logging
import numpy as np

bp = Blueprint("stock", __name__)
market_data_service = MarketDataService()


@bp.route("/search", methods=["POST"])
def search_stock():
    """Handle stock search form submission"""
    stock_symbol = request.form["stock_symbol"].upper()
    return redirect(url_for("stock.stock_landing", symbol=stock_symbol))


@bp.route("/<symbol>")
def stock_landing(symbol):
    try:
        symbol = symbol.upper()
        current_date = session.get("current_date")

        stock_data = market_data_service.get_stock_data(symbol, current_date)
        if not stock_data:
            return render_template("errors/404.html"), 404

        portfolio = session.get("portfolio", {})
        # logging.info(f"Portfolio data in stock view: {portfolio}")

        # Ensure we have a single price value
        current_price = stock_data["price"]
        if isinstance(current_price, (list, np.ndarray)):
            current_price = float(current_price[-1])

        # Get previous day's close
        historical_data = stock_data.get("historical_data")
        previous_close = current_price  # default to current price
        if historical_data is not None and len(historical_data) > 1:
            previous_close = float(historical_data["Close"].iloc[-2])

        return render_template(
            "stock.html",
            symbol=symbol,
            current_price=current_price,
            previous_close=previous_close,
            display_date=stock_data["price_date"].strftime("%Y-%m-%d"),
            portfolio=portfolio,
            meta_data=stock_data["metadata"],
            historical_data=stock_data["historical_data"],
            candlestick_chart=stock_data["chart"],
        )

    except Exception as e:
        logging.error(f"Error in stock_landing: {str(e)}")
        return render_template("errors/500.html"), 500
