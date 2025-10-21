"""
Enhanced error handling dengan retry mechanism dan specific error handling
File ini menambahkan error handling yang lebih comprehensive tanpa mengubah fungsi existing
"""
import time
import logging
from functools import wraps
from typing import Callable, Any, Optional
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    ElementClickInterceptedException, StaleElementReferenceException
)
from .exceptions import (
    SnapfluxBaseException, AuthenticationError, NavigationError, 
    DataExtractionError, DriverSetupError
)

logger = logging.getLogger('error_handler')

def retry_on_failure(
    max_retries: int = 3, 
    delay: float = 1.0, 
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator untuk retry mechanism dengan exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff_factor ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: "
                            f"{str(e)}. Retrying in {wait_time:.2f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}: {str(e)}")
            
            raise last_exception
        return wrapper
    return decorator

def handle_selenium_errors(func: Callable) -> Callable:
    """
    Decorator untuk handle Selenium-specific errors dengan custom exceptions
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except TimeoutException as e:
            error_msg = f"Timeout occurred in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            raise AuthenticationError(error_msg, error_code="TIMEOUT_ERROR")
        except NoSuchElementException as e:
            error_msg = f"Element not found in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            raise DataExtractionError(error_msg, error_code="ELEMENT_NOT_FOUND")
        except ElementClickInterceptedException as e:
            error_msg = f"Element click intercepted in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            raise NavigationError(error_msg, error_code="CLICK_INTERCEPTED")
        except StaleElementReferenceException as e:
            error_msg = f"Stale element reference in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            raise NavigationError(error_msg, error_code="STALE_ELEMENT")
        except WebDriverException as e:
            error_msg = f"WebDriver error in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            raise DriverSetupError(error_msg, error_code="WEBDRIVER_ERROR")
        except SnapfluxBaseException:
            # Re-raise custom exceptions as-is
            raise
        except Exception as e:
            error_msg = f"Unexpected error in {func.__name__}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise SnapfluxBaseException(error_msg, error_code="UNEXPECTED_ERROR")
    
    return wrapper

def safe_execute(func: Callable, *args, **kwargs) -> tuple[Any, Optional[Exception]]:
    """
    Execute function safely dan return (result, exception)
    
    Returns:
        tuple: (result, None) jika success, (None, exception) jika error
    """
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        logger.error(f"Safe execution failed for {func.__name__}: {str(e)}")
        return None, e

class ErrorContext:
    """Context manager untuk error handling dengan logging"""
    
    def __init__(self, operation_name: str, log_errors: bool = True):
        self.operation_name = operation_name
        self.log_errors = log_errors
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is None:
            logger.debug(f"Operation '{self.operation_name}' completed successfully in {duration:.2f}s")
        else:
            if self.log_errors:
                logger.error(
                    f"Operation '{self.operation_name}' failed after {duration:.2f}s: "
                    f"{exc_type.__name__}: {exc_val}"
                )
        
        # Don't suppress exceptions
        return False

def log_function_execution(func: Callable) -> Callable:
    """Decorator untuk log function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        with ErrorContext(f"{func.__module__}.{func.__name__}"):
            return func(*args, **kwargs)
    return wrapper
