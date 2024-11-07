from flask import Blueprint, session, jsonify
import logging
from app.services import portfolio_service

bp = Blueprint("portfolio", __name__)


@bp.route("/update", methods=["POST"])
def update_portfolio():
    """Update portfolio values"""
    try:
        portfolio = session.get("portfolio", {})
        positions = portfolio.get("positions", {})

        for symbol in positions:
            # Update current prices and calculations for each position
            portfolio_service.update_position_value(symbol)

        portfolio_service.update_portfolio_value()
        session["portfolio"] = portfolio

        return jsonify({"success": True}), 200
    except Exception as e:
        logging.error(f"Error updating portfolio: {str(e)})")
        return jsonify({"success": False, "error": str(e)}), 500
