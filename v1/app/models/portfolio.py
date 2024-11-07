class Portfolio:
    def __init__(self, name, cash):
        self.name = name
        self.cash = float(cash)
        self.positions = {}
        self.orders = {"active_orders": [], "filled_orders": []}
        self.value = float(cash)

    def to_dict(self):
        return {
            "name": self.name,
            "cash": self.cash,
            "positions": self.positions,
            "orders": self.orders,
            "value": self.value,
        }

    def from_dict(self, data):
        self.name = data.get("name")
        self.cash = data.get("cash")
        self.positions = data.get("positions", {})
        self.orders = data.get("orders", {"active_orders": [], "filled_orders": []})
        self.value = data.get("value", self.cash)
