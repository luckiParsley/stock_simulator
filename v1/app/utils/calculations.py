# app/utils/calculations.py
class PortfolioCalculator:
    @staticmethod
    def calculate_position_value(shares, price):
        return round(shares * price, 2)

    @staticmethod
    def calculate_unrealized_pnl(position):
        if position["side"] == "long":
            return round(
                (position["current_price"] - position["avg_price"])
                * position["shares"],
                2,
            )
        else:
            return round(
                (position["avg_price"] - position["current_price"])
                * position["shares"],
                2,
            )

    @staticmethod
    def calculate_portfolio_value(portfolio):
        total = portfolio["cash"]
        for position in portfolio["positions"].values():
            total += PortfolioCalculator.calculate_position_value(
                position["shares"], position["current_price"]
            )
        return round(total, 2)
