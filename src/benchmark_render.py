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



def imentropy(render:np.ndarray,bins = 256):
    if render.shape[2] == 3: render = (0.2989*render[:,:,0] +\
                                        0.587*render[:,:,1] +\
                                        0.114*render[:,:,2]).squeeze()
    hist, _ = np.histogram(render,bins=256)
    prob = hist / np.sum(hist) 
    return entropy(prob,base=2)

if __name__ == "__main__":
    @time_render
    def long_func():
        for _ in range(1_000_000):
            continue
    
    a = np.abs(np.random.normal(0,5,size=(300,300,3)))
    print(a[0,0])
    print(imentropy(a))
    
        