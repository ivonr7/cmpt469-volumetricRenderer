import numpy as np
from time import perf_counter_ns
from typing import Callable

def time_render(func:Callable) -> Callable:
    def wrapper(*args,**kwargs):
        ts = perf_counter_ns()
        result = func(*args,**kwargs)
        te = perf_counter_ns()
        print(f"{func.__name__} took {(te - ts) / 1000}us")
        return result
    return wrapper


if __name__ == "__main__":
    @time_render
    def long_func():
        for _ in range(1_000_000):
            continue

    long_func()
    
        