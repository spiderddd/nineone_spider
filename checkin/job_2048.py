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
    ls = "_ga=GA1.2.880967858.1732066543; _gid=GA1.2.1182749750.1732506042; eb9e6_cknum=UFFWUwEGBgdUVWxrUQEMCQgBBFVWVVcEVQ9WAQQGAgZRVA9QWFFTVQAGAFY%3D; eb9e6_ck_info=%2F%09; eb9e6_winduser=UF5cWQcBCD5bXFFVBwVQBQ5RAlBVBwEDUgcBUldUAVNRA1sAUwNVUj0%3D; peacemaker=1; eb9e6_lastpos=T2380240; eb9e6_lastvisit=898%091732506960%09%2Fread.php%3Ftid%3D2380240; eb9e6_ol_offset=55969; eb9e6_readlog=%2C2380240%2C; _gat=1; _ga_3G0BZEH5V0=GS1.2.1732506042.2.1.1732506958.0.0.0; cf_clearance=01vBp0CpQq71_kHuRdxljJDmjWYhhI3Mg1qzg6TqrU0-1732506962-1.2.1.1-ROlIXiCm21rgo2aGlxpEB6A2gL7_mV6BMexIAVNs3XXyYsSLCFLy6SPuNkzZPBEQ0j3.QzuIPNATsYrJ3P1WLPdxbf.pYX64EgcdwEskWsTF.XPGbKjzH6wNJ9JOSY01EI5RAmla4yyfRCElVNq694zijV_q02GzIv1qI9IjCe2vGIWfHAo5J1CNBF4zNm7txEg9FjG04rrvn3MQQ2BP.LVPb_KZAbdD.T4nBga1Hej9GdEebdhqnrZQkIoUMvVaTGhXguKDMzzInuFYikfgUBbd5rUgt0rH8BSCSlV0o.bk4KGJaqaYp9y48f8jYgEaz84Pw9fWf8s8hQoJCv504YwTze6HWfIYj5SnWX3paqXNviNcmzc.RVgIZKpCFfJv"
