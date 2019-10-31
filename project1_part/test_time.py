import time

# python decorator to calculate time
def test_time(show_time=False):
    def decorator(func):
        def wrapper(*args, **dicts):
            start = time.time()
            result = func(*args, **dicts)
            end = time.time()
            test_time.total_time += (end - start)
            if show_time:
                print(func.__name__, "running time is ", end - start)
            return result

        return wrapper
    return decorator
test_time.total_time = 0
