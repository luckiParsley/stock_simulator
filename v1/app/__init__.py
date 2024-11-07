from flask import Flask, render_template
from flask_session import Session
from config import config
import logging.config


def create_app(config_name="default"):
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize Flask-Session
    Session(app)

    # Configure logging
    logging.config.dictConfig(app.config["LOGGING_CONFIG"])

    # Initialize services
    from app.services.market_data_service import MarketDataService
    from app.services.order_service import OrderService
    from app.services.portfolio_service import PortfolioService

    # Register blueprints
    from app.views.main import bp as main_bp
    from app.views.stock import bp as stock_bp
    from app.views.order import bp as order_bp
    from app.views.portfolio import bp as portfolio_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(stock_bp, url_prefix="/stock")
    app.register_blueprint(order_bp, url_prefix="/order")
    app.register_blueprint(portfolio_bp, url_prefix="/portfolio")

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    return app
