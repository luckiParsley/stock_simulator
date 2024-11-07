# views/order.py
from flask import Blueprint, request, redirect, url_for, flash, render_template
from ..services.order_service import OrderService
from ..services.portfolio_service import PortfolioService
import logging

bp = Blueprint("order", __name__)
order_service = OrderService()
portfolio_service = PortfolioService()


@bp.route("/place_order", methods=["POST"])
def place_order():
    try:
        data = request.form
        order_data = {
            "symbol": data.get("symbol"),
            "side": data.get("side"),
            "order_type": data.get("order_type"),
            "shares": int(data["shares"]),
            "price": None,  # Will be set by service
        }

        success, message = order_service.place_order(order_data, portfolio_service)
        if not success:
            flash(message, "error")

        return redirect(url_for("stock.stock_landing", symbol=order_data["symbol"]))

    except Exception as e:
        logging.error(f"Error in place_order: {str(e)}")
        return render_template("errors/500.html"), 500
