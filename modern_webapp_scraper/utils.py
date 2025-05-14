import random, time, logging
from functools import wraps


def random_delay(min_s, max_s):
    time.sleep(random.uniform(min_s, max_s))


def backoff_retry(max_attempts=3, base_delay=1.0):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Attempt {attempt} failed: {e}")
                    time.sleep(delay)
                    delay *= 2
            raise

        return wrapper

    return decorator
