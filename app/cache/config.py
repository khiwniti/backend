import redis
import os
from dotenv import load_dotenv
import json
from typing import Any, Optional
from datetime import timedelta

load_dotenv()

class RedisConfig:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis cache"""
        value = self.redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a value in Redis cache"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.redis_client.set(key, value, ex=expire)
        except Exception as e:
            print(f"Error setting cache: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from Redis cache"""
        return bool(self.redis_client.delete(key))
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis cache"""
        return bool(self.redis_client.exists(key))
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in Redis cache"""
        return self.redis_client.incr(key, amount)
    
    def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement a counter in Redis cache"""
        return self.redis_client.decr(key, amount)
    
    def set_with_expiry(self, key: str, value: Any, expiry: timedelta) -> bool:
        """Set a value with expiry time in Redis cache"""
        return self.set(key, value, int(expiry.total_seconds()))
    
    def get_or_set(self, key: str, default_value: Any, expiry: Optional[timedelta] = None) -> Any:
        """Get a value from cache or set it if it doesn't exist"""
        value = self.get(key)
        if value is None:
            self.set(key, default_value, int(expiry.total_seconds()) if expiry else None)
            return default_value
        return value

# Create a singleton instance
redis_config = RedisConfig() 