from datetime import datetime


class Order:
    # Class variable to track order count
    order_count = 0

    def __init__(
        self,
        id=None,
        asset=None,
        side=None,
        order_type=None,
        price=None,
        amount=None,
        simulation_date=None,
    ):
        """
        Initialize a new order object.

        Args:
            id: Unique identifier for the order
            asset: The stock symbol (e.g., 'AAPL')
            side: 'buy' or 'sell'
            order_type: 'market', 'limit', etc.
            price: Price at which the stock is being bought or sold
            amount: Number of shares
            simulation_date: The simulation date when the order was placed
        """
        Order.order_count += 1  
        self.id = id if id is not None else Order.order_count
        self.asset = asset
        self.side = side  
        self.order_type = order_type  
        self.price = price  
        self.amount = amount  
        self.status = "open"  
        self.date_placed = simulation_date
        self.date_filled = None
        self.value = round(price * amount, 2) if price and amount else 0

    def to_dict(self):
        """Convert the order object to a dictionary"""
        return {
            "id": self.id,
            "asset": self.asset,
            "side": self.side,
            "order_type": self.order_type,
            "price": self.price,
            "amount": self.amount,
            "status": self.status,
            "date_placed": (
                self.date_placed.strftime("%Y-%m-%d") if self.date_placed else None
            ),
            "date_filled": (
                self.date_filled.strftime("%Y-%m-%d") if self.date_filled else None
            ),
            "value": self.value,
        }
