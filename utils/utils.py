import os

from utils.constant import LOCAL_FLAG_PATH


def check_local():
    return os.path.exists(LOCAL_FLAG_PATH)