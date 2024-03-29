# coding=utf-8
import json

import requests
import logging
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

from core.constants import APPID, SECRET

logger = logging.getLogger(__name__)

beaker_opts = {
    "cache.type": "ext:redis",
    "cache.url": "redis://127.0.0.1:6379"
}
beaker_cache = CacheManager(**parse_cache_config_options(beaker_opts))


@beaker_cache.cache("get_access_token", expire=5400)
def get_access_token():
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential"
    url += "&appid={appid}&secret={secret}"
    url = url.format(appid=APPID, secret=SECRET)
    resp = requests.get(url)
    resp.raise_for_status()
    res = resp.json()
    return res["access_token"]


def check_msg_sec(msg):
    try:
        access_token = get_access_token()
        query = {"access_token": access_token}
        url = "https://api.weixin.qq.com/wxa/msg_sec_check"
        body = "{\"content\": \"%s\"}" % msg
        body = body.encode("utf-8")
        headers = {
            "Content-Type": "application/json",
        }
        logger.info("url: %s, data: %s", url, body)
        resp = requests.request("POST", url, data=body, headers=headers, params=query)
        resp.raise_for_status()
        res = resp.json()
    except Exception as e:
        logger.exception(e)
        return 5000, "网络异常"

    logger.info("Msg: %s, res:%s", msg, res)

    if res["errcode"] == 0:
        return 0, "ok"
    return 4000, "敏感信息"
