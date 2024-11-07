from flask import Blueprint, flash, render_template, session, request, redirect, url_for
from ..services.portfolio_service import PortfolioService
from ..services.market_data_service import MarketDataService
from ..models.stock import Stock
from datetime import datetime
import logging
from pprint import pformat

from app.services import market_data_service

bp = Blueprint("main", __name__)
portfolio_service = PortfolioService()
market_data_service = MarketDataService()


@bp.route("/")
def landing():
    try:
        logging.info("Accessing landing page")
        years = range(2019, 2025)
        return render_template("landing.html", years=years)
    except Exception as e:
        logging.error(f"Error in landing page: {str(e)}")
        return render_template("errors/500.html"), 500


@bp.route("/submit_date", methods=["POST"])
def submit_date():
    """
    Gets new prices for positions (position['current_price'])
    Recalculates position values
    updates unrealized pnl
    updates yearly pnl tracking
    calls portfolioService.update_portfolio_value()
    adds to history

    Returns Render Template for home.


    *** From what i can tell, the issue is not here ***

    could add improved logging, if i need to further diagnose.

    """
    logging.info(f".... logging submit date route ....")
    try:
        """Selected date -> session current_date and checks is portfolio is correctly established"""
        selected_date = request.form["sim_date"]
        logging.info(r"Selected date: {selected_date}")

        selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
        selected_date = selected_date.replace(tzinfo=None)

        # sets session current date to selected_date
        session["current_date"] = selected_date
        portfolio = session.get("portfolio")

        # dosn't act if portfolio is not correctly established
        if portfolio and "positions" in portfolio:
            logging.info(r"... portfolio is established ...")
            current_year = selected_date.year

            # Initialize yearly PnL if not exists
            if "yearly_pnl" not in portfolio:
                portfolio["yearly_pnl"] = {}
            if str(current_year) not in portfolio["yearly_pnl"]:
                portfolio["yearly_pnl"][str(current_year)] = {
                    "realized": 0,
                    "unrealized": 0,
                    "total": 0,
                }

            # Initialize history if not exists
            if "history" not in portfolio:
                portfolio["history"] = []

            # Update positions
            """For each position, gets current_price, difference, pnls, etc."""
            for symbol in list(portfolio["positions"].keys()):
                try:
                    stock = Stock(symbol)
                    historical_data = stock.fetch_historical_data()
                    current_price, price_date = stock.fetch_recent_price(
                        historical_data, selected_date
                    )

                    # if we find a price, set position for whatever this loop is
                    if current_price:
                        position = portfolio["positions"][symbol]
                        logging.info(
                            f"... position found {symbol}, {current_price}\n ..."
                        )

                        # Initialize yearly PnL for position if needed
                        if "yearly_pnl" not in position:
                            position["yearly_pnl"] = {}
                        if str(current_year) not in position["yearly_pnl"]:
                            position["yearly_pnl"][str(current_year)] = {
                                "realized": 0,
                                "unrealized": 0,
                                "total": 0,
                            }

                        # update current_price
                        position["current_price"] = current_price

                        # Calculate P&L and value
                        # calculation for longs looks good
                        if position["side"] == "long":
                            position["value"] = round(
                                position["shares"] * current_price, 2
                            )
                            position["difference"] = round(
                                current_price - position["avg_price"], 2
                            )
                            # percent_difference may throw an error is avg_price has gone to 0
                            position["percent_difference"] = round(
                                (position["difference"] / position["avg_price"]) * 100,
                                2,
                            )
                            unrealized_pnl = (
                                current_price - position["avg_price"]
                            ) * position["shares"]
                        else:
                            # calculation for shorts looks good
                            position["difference"] = round(
                                position["avg_price"] - current_price, 2
                            )
                            position["percent_difference"] = round(
                                (position["difference"] / position["avg_price"]) * 100,
                                2,
                            )
                            unrealized_pnl = (
                                position["avg_price"] - current_price
                            ) * position["shares"]
                            # value of shares at price + difference per share
                            position["value"] = round(
                                position["shares"]
                                * (position["avg_price"] + position["difference"]),
                                2,
                            )

                        # sets pnl values in accordance with the year
                        position["unrealized_pnl"] = round(unrealized_pnl, 2)
                        position["yearly_pnl"][str(current_year)]["unrealized"] = round(
                            unrealized_pnl, 2
                        )
                        position["yearly_pnl"][str(current_year)]["total"] = round(
                            position["yearly_pnl"][str(current_year)]["realized"]
                            + position["yearly_pnl"][str(current_year)]["unrealized"],
                            2,
                        )
                        position["yearly_total_pnl"] = position["yearly_pnl"][
                            str(current_year)
                        ]["total"]

                        # resets position within portfolio
                        portfolio["positions"][symbol] = position

                except Exception as e:
                    logging.error(f"Error updating position for {symbol}: {str(e)}")
                    continue

            """After calculating data for each position"""

            # Not sure why i need these
            total_unrealized = sum(
                pos["yearly_pnl"].get(str(current_year), {}).get("unrealized", 0)
                for pos in portfolio["positions"].values()
            )

            # Not sure why i need these
            portfolio["yearly_pnl"][str(current_year)]["unrealized"] = round(
                total_unrealized, 2
            )
            portfolio["yearly_pnl"][str(current_year)]["total"] = round(
                portfolio["yearly_pnl"][str(current_year)]["realized"]
                + portfolio["yearly_pnl"][str(current_year)]["unrealized"],
                2,
            )

            # Update session and calculate new portfolio value
            session["portfolio"] = portfolio
            logging.info(
                f"portfolio before update_portfolio_value is called: \n{pformat(portfolio)}"
            )
            logging.info(r"... calling portfolioService.update_portfolio_value() ....")

            # new_value new_value of portfolio?
            new_value = PortfolioService.update_portfolio_value()
            logging.info(f"new value: \n{pformat(new_value)}")

            # Add history entry
            history_entry = {
                "date": selected_date.strftime("%Y-%m-%d"),
                "portfolio_value": new_value,
                "total_pnl": portfolio["yearly_pnl"][str(current_year)]["total"],
                "cash": portfolio["cash"],
            }
            portfolio["history"].append(history_entry)

            if len(portfolio["history"]) > 365:
                portfolio["history"] = portfolio["history"][-365:]

            session["portfolio"] = portfolio
            logging.info(r"... portfolio re-initalized ...")

        current_date_str = selected_date.strftime("%Y-%m-%d")
        account_value = portfolio.get("value", 0)
        logging.info("finished submit date route execution")
        logging.info(f"\nCurrent portfolio state...\n\n{pformat(portfolio)}")

        return render_template(
            "home.html",
            portfolio=portfolio,
            current_date=selected_date,
            account_value=account_value,
            current_date_str=current_date_str,
            portfolio_history=portfolio.get("history", []),
        )

    except Exception as e:
        logging.error(f"Error in submit_date: {str(e)}")
        logging.error(f"Portfolio state: {session.get('portfolio')}")
        return render_template("errors/500.html"), 500


@bp.route("/home", methods=["POST"])
def submit():
    try:
        form_data = request.form
        start_year = form_data.get("start_date")
        if not start_year:
            flash("Please select a valid start year", "error")
            return redirect(url_for("main.landing"))

        start_date = datetime.strptime(f"{start_year}-01-01", "%Y-%m-%d")

        session["current_date"] = start_date
        session["start_date"] = start_date

        portfolio = portfolio_service.create_portfolio(
            name=form_data.get("portfolio_name", "My Portfolio"),  # Add default value
            initial_cash=float(
                form_data.get("starting_balance", 0)
            ),  # Add default value
        )

        # Initialize the portfolio history
        portfolio["history"] = []

        # Add initial history entry
        initial_history = {
            "date": start_date.strftime("%Y-%m-%d"),
            "portfolio_value": portfolio["value"],
            "total_pnl": 0,
            "cash": portfolio["cash"],
        }
        portfolio["history"].append(initial_history)

        session["portfolio"] = portfolio

        return render_template(
            "home.html",
            portfolio=portfolio,
            current_date_str=start_date.strftime("%Y-%m-%d"),
            account_value=portfolio["value"],
            current_date=start_date,
            portfolio_history=portfolio.get("history", []),
        )

    except Exception as e:
        logging.error(f"Error in submit: {str(e)}")
        return render_template("errors/500.html"), 500


@bp.route("/home", methods=["GET"])
def home():
    try:
        portfolio = session.get("portfolio")
        if not portfolio:
            return redirect(url_for("main.landing"))
        current_date = session.get("current_date")
        current_date_str = current_date.strftime("%Y-%m-%d")

        logging.info(f"current_portfolio_state:\n\n{pformat(portfolio)}")

        return render_template(
            "home.html",
            portfolio=portfolio,
            current_date_str=current_date_str,
            account_value=portfolio["value"],
            current_date=current_date,
            portfolio_history=portfolio.get("history", []),
        )
    except Exception as e:
        logging.error(f"Error in home: {str(e)}")
        logging.error(f"portfolio state: \n{pformat(portfolio)}")
        return render_template("errors/500.html"), 500

    """Old home logic, which i believe to be mostly redundant"""
    # try:
    #     portfolio = session.get('portfolio')
    #     if not portfolio:
    #         return redirect(url_for('main.landing'))

    #     current_date = session.get('current_date')
    #     current_date_str = current_date.strftime('%Y-%m-%d')
    #     current_year = str(current_date.year)

    #     # Initialize yearly_pnl if it doesn't exist
    #     if 'yearly_pnl' not in portfolio:
    #         portfolio['yearly_pnl'] = {
    #             current_year: {
    #                 'realized': 0,
    #                 'unrealized': 0,
    #                 'total': 0
    #             }
    #         }

    #     # Initialize history if it doesn't exist
    #     if 'history' not in portfolio:
    #         portfolio['history'] = []

    #     # Update positions and portfolio value
    #     if portfolio and 'positions' in portfolio:
    #         total_unrealized_pnl = 0
    #         for symbol in list(portfolio['positions'].keys()):
    #             try:
    #                 stock = Stock(symbol)
    #                 historical_data = stock.fetch_historical_data()
    #                 current_price, price_date = stock.fetch_recent_price(historical_data, current_date)

    #                 if current_price:
    #                     position = portfolio['positions'][symbol]
    #                     position['current_price'] = current_price
    #                     position['value'] = round(position['shares'] * current_price, 2)

    #                     # Update P&L calculations
    #                     if position['side'] == 'long':
    #                         position['difference'] = round(current_price - position['avg_price'], 2)
    #                         position['percent_difference'] = round((position['difference'] / position['avg_price']) * 100, 2)
    #                         position['unrealized_pnl'] = round(position['difference'] * position['shares'], 2)
    #                     else:  # short position
    #                         position['difference'] = round(position['avg_price'] - current_price, 2)
    #                         position['percent_difference'] = round((position['difference'] / position['avg_price']) * 100, 2)
    #                         position['unrealized_pnl'] = round(position['difference'] * position['shares'], 2)

    #                     total_unrealized_pnl += position['unrealized_pnl']

    #                     logging.info(f"Updated position for {symbol}: Price={current_price}, Value={position['value']}")
    #             except Exception as e:
    #                 logging.error(f"Error updating position for {symbol}: {str(e)}")
    #                 continue

    #         # Update portfolio total value
    #         total_position_value = sum(pos['value'] for pos in portfolio['positions'].values())
    #         portfolio['value'] = round(portfolio['cash'] + total_position_value, 2)

    #         # Update portfolio yearly PnL
    #         if current_year not in portfolio['yearly_pnl']:
    #             portfolio['yearly_pnl'][current_year] = {
    #                 'realized': 0,
    #                 'unrealized': 0,
    #                 'total': 0
    #             }

    #         portfolio['yearly_pnl'][current_year]['unrealized'] = round(total_unrealized_pnl, 2)
    #         portfolio['yearly_pnl'][current_year]['total'] = round(
    #             portfolio['yearly_pnl'][current_year]['realized'] + total_unrealized_pnl, 2
    #         )

    #         # Update portfolio history
    #         history_entry = {
    #             'date': current_date_str,
    #             'portfolio_value': portfolio['value'],
    #             'total_pnl': portfolio['yearly_pnl'][current_year]['total'],
    #             'cash': portfolio['cash']
    #         }

    #         # Only add history entry if it's a new date
    #         if not portfolio['history'] or portfolio['history'][-1]['date'] != current_date_str:
    #             portfolio['history'].append(history_entry)

    #             # Keep only last 365 days of history
    #             if len(portfolio['history']) > 365:
    #                 portfolio['history'] = portfolio['history'][-365:]

    #         # update portfolio value whenever home route is called
    #         PortfolioService.update_portfolio_value()
    #         session['portfolio'] = portfolio

    #     logging.info(f"Portfolio value: {portfolio['value']}")
    #     logging.info(f"Portfolio history entries: {len(portfolio.get('history', []))}")

    #     return render_template('home.html',
    #                          portfolio=portfolio,
    #                          current_date_str=current_date_str,
    #                          account_value=portfolio['value'],
    #                          current_date=current_date,
    #                          portfolio_history=portfolio.get('history', []))
    # except Exception as e:
    #     logging.error(f"Error in home: {str(e)}")
    #     logging.error(f"Portfolio state: {session.get('portfolio')}")
    #     return render_template('errors/500.html'), 500
