import redis
import os

def get_redis():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379' )
    redis_out = redis.from_url( redis_url )
    return( redis_out )
