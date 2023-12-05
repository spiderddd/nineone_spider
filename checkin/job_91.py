import sys

from core.nineone.spider_91 import run

if __name__ == '__main__':
    mysql_host = sys.argv[1]
    mysql_user = sys.argv[2]
    mysql_pwd = sys.argv[3]

    run(mysql_host, mysql_user, mysql_pwd)