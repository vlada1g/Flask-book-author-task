from functools import wraps 

def my_wrapper(orig_func):
    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        collect='test123'
        age=25
        return orig_func(collect, *args, **kwargs)
    
    return wrapper


@my_wrapper
def my_func(collect):
    print(collect)


my_func()