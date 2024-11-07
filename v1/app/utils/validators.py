# app/utils/validators.py
from datetime import datetime


class OrderValidator:
    @staticmethod
    def validate_order_input(data):
        errors = []

        if not data.get("symbol"):
            errors.append("Symbol is required")

        try:
            shares = int(data.get("shares", 0))
            if shares <= 0:
                errors.append("Number of shares must be positive")
        except ValueError:
            errors.append("Invalid number of shares")

        if data.get("side") not in ["buy", "sell"]:
            errors.append("Invalid order side")

        if data.get("order_type") not in ["market", "limit"]:
            errors.append("Invalid order type")

        return errors
