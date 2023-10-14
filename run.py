from app import app
import logging
from logging.handlers import RotatingFileHandler


if __name__ == '__main__':
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
