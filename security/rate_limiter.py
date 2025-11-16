import time
from collections import defaultdict
from flask import request

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def get_client_ip(self):
        return request.headers.get("X-Forwarded-For", request.remote_addr)
    
    def is_rate_limited(self, key, max_requests, window_seconds):
        now = time.time()
        self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < window_seconds]
        
        if len(self.requests[key]) >= max_requests:
            return True
        
        self.requests[key].append(now)
        return False

rate_limiter = RateLimiter()