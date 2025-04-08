import logging
import os
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

class LoggingConfig:
    def __init__(self):
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Configure root logger
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(self.log_level)
        
        # Create formatters
        formatter = logging.Formatter(self.log_format)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.root_logger.addHandler(console_handler)
        
        # Create file handler
        file_handler = RotatingFileHandler(
            f"logs/app_{datetime.now().strftime('%Y%m%d')}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name"""
        return logging.getLogger(name)
    
    def log_request(self, logger: logging.Logger, request_data: dict):
        """Log HTTP request data"""
        logger.info("Request: %s", json.dumps(request_data, default=str))
    
    def log_response(self, logger: logging.Logger, response_data: dict):
        """Log HTTP response data"""
        logger.info("Response: %s", json.dumps(response_data, default=str))
    
    def log_error(self, logger: logging.Logger, error: Exception, context: dict = None):
        """Log error with context"""
        error_data = {
            "error": str(error),
            "type": type(error).__name__,
            "context": context
        }
        logger.error("Error: %s", json.dumps(error_data, default=str))
    
    def log_analytics(self, logger: logging.Logger, analytics_data: dict):
        """Log analytics data"""
        logger.info("Analytics: %s", json.dumps(analytics_data, default=str))
    
    def log_ai_operation(self, logger: logging.Logger, operation: str, data: dict):
        """Log AI operation data"""
        logger.info("AI Operation [%s]: %s", operation, json.dumps(data, default=str))

# Create a singleton instance
logging_config = LoggingConfig() 