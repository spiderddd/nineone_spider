import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOCAL_FLAG_PATH = os.path.join(PROJECT_ROOT, 'local.flag')

DEFAULT_2048_HOST = 'v8.y8rb4.com'

http_proxy = 'http://127.0.0.1:7890'
proxies = {'http':http_proxy,'https':http_proxy}