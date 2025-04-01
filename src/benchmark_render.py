import numpy as np
from time import perf_counter_ns
from typing import Callable
from scipy.stats import entropy
import matplotlib.pyplot as plt
def time_render(func:Callable) -> Callable:
    def wrapper(*args,**kwargs):
        ts = perf_counter_ns()
        result = func(*args,**kwargs)
        te = perf_counter_ns()
        print(f"{func.__name__} took {(te - ts) / 1000}us")
        return result
    return wrapper



def relative_entropy(render:np.ndarray,baseline:np.ndarray) -> float:
    render,render_bins = np.histogram(render.flatten())
    baseline,baseline_bins = np.histogram(baseline.flatten())
    return entropy(render,baseline)

if __name__ == "__main__":
    @time_render
    def long_func():
        for _ in range(1_000_000):
            continue
    

    print(relative_entropy(np.random.normal(0,10,size=(300,300)),np.random.normal(0,1,size=(300,300))))
    long_func()
    
        