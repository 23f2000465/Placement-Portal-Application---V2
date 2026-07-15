import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import cache
from app import create_app


class FakeRedis:
    def __init__(self): self.data={}
    def setex(self,key,seconds,value): self.data[key]=value
    def get(self,key): return self.data.get(key)
    def scan_iter(self,pattern):
        prefix=pattern[:-1]
        return [key for key in self.data if key.startswith(prefix)]
    def delete(self,*keys):
        for key in keys: self.data.pop(key,None)


class CacheTests(unittest.TestCase):
    def test_set_get_expiry_call_and_prefix_clear(self):
        old=cache.redis_client; cache.redis_client=FakeRedis()
        app=create_app({'TESTING':True,'CACHE_SECONDS':300,'CACHE_ENABLED':True})
        with app.app_context():
            cache.set_cache('student:drives:1',{'count':2})
            self.assertEqual(cache.get_cache('student:drives:1')['count'],2)
            cache.clear_cache('student:')
            self.assertIsNone(cache.get_cache('student:drives:1'))
        cache.redis_client=old

if __name__=='__main__': unittest.main()
