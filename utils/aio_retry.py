from functools import wraps
import asyncio


def retry_timeout(times=3, sleep=5):

    async def make_try(times_flag, func, args, kwargs):
        times_flag += 1
        try:
            await asyncio.sleep(sleep)
            return await func(*args, **kwargs)
        except asyncio.exceptions.TimeoutError:
            if times_flag < times:
                await asyncio.sleep(sleep)
                return await make_try(times_flag, func, args, kwargs)
            else:
                raise asyncio.exceptions.TimeoutError
        except Exception:
            raise Exception

    def inner_decorator(func):
        @wraps(func)
        async def decorated(*args, **kwargs):
            return await make_try(0, func, args, kwargs)
        return decorated
    return inner_decorator

