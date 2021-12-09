from functools import wraps
from hashlib import sha256
import os
import pickle


def cache(namespace="unnamed", log=False, refresh=False):
    def inner_decorator(func):
        root_cache = "__cache_result__"
        if not os.path.exists(root_cache):
            os.mkdir(root_cache)

        def is_cached(key):
            return key in os.listdir(root_cache)

        def dump_cache(key, data):
            with open(os.path.join(root_cache, key), "wb") as fp:
                pickle.dump(data, fp)

        def load_cache(key):
            with open(os.path.join(root_cache, key), "rb") as fp:
                return pickle.load(fp)

        def gen_key(*args):
            return sha256(pickle.dumps(args)).hexdigest()

        @wraps(func)
        async def decorated(*args, **kwargs):
            key = gen_key(namespace, func.__name__, args, kwargs)
            if not refresh and is_cached(key):
                if log:
                    print("[LOG] LOADING CACHE")
                return load_cache(key)
            else:
                result = await func(*args, **kwargs)
                if log:
                    print("[LOG] DUMPED CACHE")
                dump_cache(key, result)
                return result
        return decorated
    return inner_decorator


@cache()
async def get_html(url):
    pass
