# In order_service.py

from flask import session
import logging
from ..models.order import Order
from ..models.stock import Stock
from datetime import datetime
from ..services.portfolio_service import PortfolioService
from pprint import pformat


class OrderService:
    def __init__(self):
        pass

    @staticmethod
    def place_order(order_data, porfolio_service):
        try:
            logging.info(f"... Executing place_order function ...")

            if not order_data.get("price"):
                stock = Stock(order_data["symbol"])
                historical_data = stock.fetch_historical_data()
                current_price, _ = stock.fetch_recent_price(
                    historical_data, session.get("current_date")
                )
                order_data["price"] = current_price
                logging.info(f"Fetched current price: {current_price}")

            order = Order(
                id=None,
                asset=order_data["symbol"],
                side=order_data["side"],
                order_type=order_data["order_type"],
                price=order_data["price"],
                amount=int(order_data["shares"]),
                simulation_date=session.get("current_date"),
            )

            logging.info(f"... Calling execute order function ...")
            success = OrderService._execute_order(order)
            if success:
                portfolio = session.get("portfolio")
                order.status = "filled"
                order.date_filled = session.get("current_date")
                portfolio["orders"]["filled_orders"].append(order.to_dict())
                session["portfolio"] = portfolio

                logging.info(f"Order executed successfully: {order.to_dict()}")

                return True, "Order executed successfully"
            return False, "Order execution failed"

        except Exception as e:
            logging.error(f"Error placing order: {str(e)}")
            return False, str(e)

    @staticmethod
    def _execute_order(order):
        """
        Updates cash
        creates/ modifies positions
        updates position values and pnl
        stores closed positions if applicable
        calles PortfolioService.update_portfolio_value()

        Returns True/False
        """
        portfolio = session.get("portfolio", {})
        current_position = portfolio["positions"].get(order.asset)
        current_year = str(session.get("current_date").year)

        logging.info(r"\n=== Starting Order Execution ===")
        logging.info(
            f"Order details: {order.asset}, Side: {order.side}, Shares/amoung: {order.amount}, Price: {order.price}"
        )
        logging.info(f"Current portfolio cash: {portfolio['cash']}")
        logging.info(f"Current portfolio value: {portfolio.get('value')}")

        if current_position is not None:
            logging.info(f"\nExisting position found for {order.asset}:")
            logging.info(
                f"Current position: Side={current_position['side']}, Shares={current_position['shares']}"
            )
            logging.info(
                f"Avg Price: {current_position['avg_price']}, Current Price: {current_position['current_price']}"
            )
            logging.info(f"Current position value: {current_position['value']}")

            # Extending position
            if (current_position["side"] == "long" and order.side == "buy") or (
                current_position["side"] == "short" and order.side == "sell"
            ):
                logging.info("\nExtending position...")
                order_cost = round(order.price * order.amount, 2)
                logging.info(f"Order cost: {order_cost}")
                if order_cost > portfolio["cash"]:
                    logging.info("Not enough cash for extension")
                    return False
                else:
                    total_shares = current_position["shares"] + order.amount
                    total_cost = (
                        current_position["avg_price"] * current_position["shares"]
                    ) + (order.price * order.amount)
                    new_avg_price = round(total_cost / total_shares, 2)

                    logging.info(f"New total shares: {total_shares}")
                    logging.info(f"New average price: {new_avg_price}")

                    if current_position["side"] == "long":
                        new_value = round(total_shares * order.price, 2)
                        difference = round(order.price - new_avg_price, 2)
                    else:
                        difference = round(new_avg_price - order.price, 2)
                        new_value = round(
                            total_shares * (new_avg_price + difference), 2
                        )

                    print(total_shares)
                    print(difference)
                    new_upl = round(difference * total_shares, 2)
                    print(new_upl)

                    current_position.update(
                        {
                            "shares": total_shares,
                            "avg_price": new_avg_price,
                            "value": new_value,
                            "current_price": order.price,
                            "difference": difference,
                            "unrealized_pnl": new_upl,
                        }
                    )

                    current_position["yearly_pnl"][current_year]["unrealized"] = (
                        current_position["shares"] * current_position["difference"]
                    )
                    current_position["yearly_pnl"][current_year]["total"] = (
                        current_position["yearly_pnl"][current_year]["realized"]
                        + current_position["yearly_pnl"][current_year]["unrealized"]
                    )

                    current_position["yearly_total_pnl"] = current_position[
                        "yearly_pnl"
                    ][current_year]["total"]
                    portfolio["cash"] -= order_cost
                    logging.info(f"Updated position value: {current_position['value']}")
                    logging.info(f"Remaining cash: {portfolio['cash']}")

                    session["portfolio"] = portfolio
                    return True
            else:
                logging.info("\nReversing, Closing, or Reducing position...")
                order_cost = round(order.price * order.amount, 2)
                logging.info(f"Order cost: {order_cost}")

                # Reducing
                if order.amount < current_position["shares"]:
                    logging.info("\nReducing position...")
                    remaining_shares = current_position["shares"] - order.amount

                    if current_position["side"] == "long":
                        logging.info(
                            f"current position side: {current_position['side']}"
                        )
                        realized_pnl = (
                            order.price - current_position["avg_price"]
                        ) * order.amount
                        new_upl = (
                            order.price - current_position["avg_price"]
                        ) * remaining_shares
                        logging.info(
                            f"realized_pnl: {realized_pnl}\nnew_upl: {new_upl}\n"
                        )
                    else:
                        realized_pnl = (
                            current_position["avg_price"] - order.price
                        ) * order.amount
                        new_upl = (
                            current_position["avg_price"] - order.price
                        ) * remaining_shares

                    if current_year not in current_position["yearly_pnl"]:
                        current_position["yearly_pnl"][current_year] = {
                            "realized": realized_pnl,
                            "unrealized": new_upl,
                            "total": sum(realized_pnl, new_upl),
                        }
                    else:
                        current_position["yearly_pnl"][current_year][
                            "realized"
                        ] += realized_pnl
                        current_position["yearly_pnl"][current_year][
                            "unrealized"
                        ] -= realized_pnl
                    if current_year not in portfolio["yearly_pnl"]:
                        portfolio["yearly_pnl"][current_year] = {
                            "realized": realized_pnl,
                            "unrealized": new_upl,
                            "total": sum(realized_pnl, new_upl),
                        }
                    else:
                        portfolio["yearly_pnl"][current_year][
                            "realized"
                        ] += realized_pnl
                        portfolio["yearly_pnl"][current_year][
                            "unrealized"
                        ] -= realized_pnl

                    logging.info(f"{new_upl}")
                    current_position.update(
                        {
                            "shares": remaining_shares,
                            "current_price": order.price,
                            "unrealized_pnl": new_upl,
                        }
                    )

                    portfolio["cash"] += order_cost
                    return True

                # Closing

                elif order.amount == current_position["shares"]:
                    logging.info("... Closing ...")

                    if current_position["side"] == "long":
                        realized_pnl = (
                            order.price - current_position["avg_price"]
                        ) * order.amount
                    else:
                        realized_pnl = (
                            current_position["avg_price"] - order.price
                        ) * order.amount

                    if current_year not in current_position["yearly_pnl"]:
                        current_position["yearly_pnl"][current_year] = {
                            "realized": 0,
                            "unrealized": 0,
                            "total": 0,
                        }
                    if current_year not in portfolio["yearly_pnl"]:
                        portfolio["yearly_pnl"][current_year] = {
                            "realized": 0,
                            "unrealized": 0,
                            "total": 0,
                        }

                    current_position["yearly_pnl"][current_year]["realized"] += round(
                        realized_pnl, 2
                    )
                    portfolio["yearly_pnl"][current_year]["realized"] += round(
                        realized_pnl, 2
                    )

                    portfolio["yearly_pnl"][current_year]["unrealized"] -= round(
                        realized_pnl, 2
                    )

                    if order.asset not in portfolio["closed_positions"]:
                        portfolio["closed_positions"][order.asset] = []

                    closed_position = {
                        "close_date": session.get("current_date").strftime("%Y-%m-%d"),
                        "side": current_position["side"],
                        "shares": current_position["shares"],
                        "avg_price": current_position["avg_price"],
                        "close_price": order.price,
                        # not so sure about this
                        "realized_pnl": round(realized_pnl, 2),
                        "yearly_pnl": current_position["yearly_pnl"],
                    }
                    portfolio["closed_positions"][order.asset].append(closed_position)

                    if current_position["side"] == "long":

                        portfolio["cash"] += order_cost
                    else:  # short position

                        portfolio["cash"] += round(
                            current_position["shares"]
                            * (
                                current_position["avg_price"]
                                + order.price
                                - current_position["avg_price"]
                            )
                        )

                    del portfolio["positions"][order.asset]
                    return True

                # Reversing
                else:

                    logging.info("\n... Reversing position ...")

                    new_shares = order.amount - current_position["shares"]
                    new_side = "long" if order.side == "buy" else "short"

                    logging.info(current_position["side"])

                    if current_position["side"] == "long":
                        realized_pnl = (
                            order.price - current_position["avg_price"]
                        ) * current_position["shares"]
                    else:
                        realized_pnl = (
                            current_position["avg_price"] - order.price
                        ) * current_position["shares"]

                    logging.info(f"Realized PnL: {realized_pnl}")

                    if current_year not in current_position["yearly_pnl"]:
                        current_position["yearly_pnl"][current_year] = {
                            "realized": 0,
                            "unrealized": 0,
                            "total": 0,
                        }
                    if current_year not in portfolio["yearly_pnl"]:
                        portfolio["yearly_pnl"][current_year] = {
                            "realized": 0,
                            "unrealized": 0,
                            "total": 0,
                        }

                    current_position["yearly_pnl"][current_year]["realized"] += round(
                        realized_pnl, 2
                    )
                    portfolio["yearly_pnl"][current_year]["realized"] += round(
                        realized_pnl, 2
                    )

                    portfolio["yearly_pnl"][current_year]["unrealized"] -= round(
                        realized_pnl, 2
                    )

                    if order.asset not in portfolio["closed_positions"]:
                        portfolio["closed_positions"][order.asset] = []

                    closed_position = {
                        "close_date": session.get("current_date").strftime("%Y-%m-%d"),
                        "side": current_position["side"],
                        "shares": current_position["shares"],
                        "avg_price": current_position["avg_price"],
                        "close_price": order.price,
                        "realized_pnl": round(realized_pnl, 2),
                        "yearly_pnl": current_position["yearly_pnl"],
                    }
                    portfolio["closed_positions"][order.asset].append(closed_position)
                    logging.info(f"Original position stored in closed_positions")
                    logging.info(f"closed position: \n{pformat(closed_position)}\n")

                    logging.info(
                        f"adding cash from closed position side = {closed_position['side']}"
                    )

                    close_cash = round(current_position["shares"] * order.price, 2)

                    logging.info(f"close_cash: {close_cash}")
                    logging.info(f"portfolio_cash_before: {portfolio['cash']}")
                    portfolio["cash"] += close_cash
                    logging.info(f"portfolio_cash_after: {portfolio['cash']}")

                    reverse_cost = round(new_shares * order.price, 2)
                    logging.info(f"New position cost: {reverse_cost}")

                    if reverse_cost > portfolio["cash"]:
                        logging.info("Not enough cash for reversal")
                        return False
                    else:

                        if new_side == "long":
                            new_value = round(new_shares * order.price, 2)
                        else:
                            new_value = round(new_shares * order.price, 2)

                        portfolio["positions"][order.asset] = {
                            "side": new_side,
                            "shares": new_shares,
                            "avg_price": order.price,
                            "value": new_value,
                            "current_price": order.price,
                            "difference": 0,
                            "percent_difference": 0,
                            "unrealized_pnl": 0,
                            "yearly_pnl": current_position["yearly_pnl"],
                        }
                        portfolio["cash"] -= reverse_cost

                        logging.info("\nNew position created:")
                        logging.info(f"{pformat(portfolio['positions'][order.asset])}")
                        return True

        else:
            logging.info("\nCreating new position...")
            order_cost = round(order.price * order.amount, 2)
            logging.info(f"Order cost: {order_cost}")
            logging.info(f"Available cash before: {portfolio['cash']}")

            if order_cost > portfolio["cash"]:
                logging.info("Not enough cash for new position")
                return False
            else:
                existing_yearly_pnl = None
                if (
                    order.asset in portfolio["closed_positions"]
                    and portfolio["closed_positions"][order.asset]
                ):
                    existing_yearly_pnl = portfolio["closed_positions"][order.asset][
                        -1
                    ]["yearly_pnl"]
                    logging.info("Found existing PnL history for this symbol")
                    logging.info(f"Existing yearly pnl: {existing_yearly_pnl}")

                if order.side == "buy":
                    initial_value = order_cost
                else:
                    initial_value = order_cost
                    logging.info(f"initial value: {initial_value}")

                portfolio["positions"][order.asset] = {
                    "side": "long" if order.side == "buy" else "short",
                    "shares": order.amount,
                    "avg_price": order.price,
                    "value": initial_value,
                    "current_price": order.price,
                    "difference": 0,
                    "percent_difference": 0,
                    "unrealized_pnl": 0,
                    "yearly_pnl": (
                        existing_yearly_pnl
                        if existing_yearly_pnl
                        else {
                            current_year: {"realized": 0, "unrealized": 0, "total": 0}
                        }
                    ),
                }
                portfolio["cash"] -= order_cost

                logging.info(f"New position created:")
                logging.info(f"New position: {portfolio['positions'][order.asset]}")

            session["portfolio"] = portfolio

            PortfolioService.update_portfolio_value()
            logging.info("\n=== Order Execution Complete ===")
            return True
