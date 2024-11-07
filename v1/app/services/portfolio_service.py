from flask import session
from ..models.portfolio import Portfolio
import logging
from pprint import pformat


class PortfolioService:
    def __init__(self):
        pass

    @staticmethod
    def get_portfolio():
        return session.get("portfolio")

    @staticmethod
    def update_position_history(position, symbol, current_price, current_date):
        """Track historical data for individual positions"""
        if "history" not in position:
            position["history"] = []

        # Calculate position PnL
        if position["side"] == "long":
            unrealized_pnl = (current_price - position["avg_price"]) * position[
                "shares"
            ]
        else:  # short position
            unrealized_pnl = (position["avg_price"] - current_price) * position[
                "shares"
            ]

        year = str(current_date.year)

        realized_pnl = position.get("yearly_pnl", {}).get(year, {}).get("realized", 0)

        # Create history entry
        history_entry = {
            "date": current_date.strftime("%Y-%m-%d"),
            "price": current_price,
            "shares": position["shares"],
            "value": position["value"],
            "unrealized_pnl": unrealized_pnl,
            "realized_pnl": realized_pnl,
            "total_pnl": unrealized_pnl + realized_pnl,
            "pnl_percentage": (
                (
                    (unrealized_pnl + realized_pnl)
                    / (position["value"] - (unrealized_pnl + realized_pnl))
                )
                * 100
                if position["value"] != (unrealized_pnl + realized_pnl)
                else 0
            ),
        }

        position["history"].append(history_entry)

        # Keep last 365 days of history
        if len(position["history"]) > 365:
            position["history"] = position["history"][-365:]

        return position

    @staticmethod
    def update_all_history(portfolio, current_date):
        """Update both position-level and portfolio-wide history"""
        try:
            # First update each position's history
            for symbol, position in portfolio["positions"].items():
                position = PortfolioService.update_position_history(
                    position, symbol, position["current_price"], current_date
                )
                portfolio["positions"][symbol] = position

            return portfolio
        except Exception as e:
            logging.error(f"Error updating history: {str(e)}")
            return portfolio

    @staticmethod
    def create_portfolio(name, initial_cash):
        portfolio = {
            "name": name,
            "cash": float(initial_cash),
            "positions": {},
            "closed_positions": {},
            "orders": {"active_orders": [], "filled_orders": []},
            "value": float(initial_cash),
        }
        session["portfolio"] = portfolio
        return portfolio

    @staticmethod
    def update_portfolio_value():
        """
        Accounts for current cash + position values.
        updates portfolio value
        """
        portfolio = session.get("portfolio")
        total_value = portfolio["cash"]
        logging.info(f"starting portfolio value calculations")
        logging.info(f"Initial cash value: {total_value}")

        logging.info(f"updating portfolio_value loop: \n")
        for symbol, position in portfolio["positions"].items():

            current_value = position["value"]
            logging.info(symbol)
            logging.info(current_value)
            total_value += current_value

            logging.info(f"Positions items: {pformat(position)}")

        portfolio["value"] = round(total_value, 2)
        logging.info(f"final portfolio value: {portfolio['value']}")
        session["portfolio"] = portfolio
        return portfolio["value"]
