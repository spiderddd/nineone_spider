import sys

from core.uc.signin2048 import get_latest_url, run
from core.utils.constant import DEFAULT_2048_HOST

if __name__ == '__main__':
    user_name = sys.argv[1]
    password = sys.argv[2]
    answer = sys.argv[3]
    host = get_latest_url()
    success_flag = run(host, user_name, password, answer)
    if not success_flag:
        run(DEFAULT_2048_HOST, user_name, password, answer)
