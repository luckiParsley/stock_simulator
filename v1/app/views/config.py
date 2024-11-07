"""Configuration settings for the application views"""

# Template configuration
TEMPLATE_CONFIG = {"template_folder": "../templates", "static_folder": "../static"}

# Pagination settings
ITEMS_PER_PAGE = 20

# Date format settings
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Market data settings
MARKET_DATA_CACHE_DURATION = 3600  # 1 hour in seconds

# Session settings
SESSION_CONFIG = {
    "PERMANENT_SESSION_LIFETIME": 1800,  # 30 minutes in seconds
    "SESSION_TYPE": "filesystem",
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default",
            "level": "INFO",
        },
    },
    "root": {"level": "INFO", "handlers": ["console", "file"]},
}

# Error messages
ERROR_MESSAGES = {
    "invalid_symbol": "Invalid stock symbol provided",
    "insufficient_funds": "Insufficient funds to execute order",
    "invalid_quantity": "Invalid quantity specified",
    "invalid_date": "Invalid date format or range",
    "portfolio_not_found": "Portfolio not found",
    "market_data_error": "Error fetching market data",
}
