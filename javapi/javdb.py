import requests
from bs4 import BeautifulSoup
from pylibz import log, deepcopy
from pylibz.func import base64_encode
from .config import get_javdb_host, get_local
from .func import get_cache, write_cache


def get_values(item):
    values = []
    contents = item.select("a")
    for i in range(len(contents)):
        values.append(contents[i].text)
    return values


def get_data(session: requests.Session, vid: str, vmsg: dict):
    vmsg = deepcopy(vmsg)
    url = "%s/v/%s" % (get_javdb_host(), vid)
    r = session.get(url)
    r = r.content.decode("utf-8")
    soup = BeautifulSoup(r, 'lxml')
    title = soup.select(".title")[0].select("strong")[0].text.strip()
    vmsg["title"] = title
    contents = soup.select(".panel-block")
    for i in range(len(contents) - 1):
        if len(contents[i].select("strong")) < 1:
            continue
        tag = contents[i].select("strong")[0].text
        tag = tag.strip().strip(":")
        if tag == '片商':
            t = get_values(contents[i])
            if isinstance(t, list):
                vmsg["writer"] += t
            else:
                vmsg["writer"].append(t)
        elif tag == '發行':
            t = get_values(contents[i])
            if isinstance(t, list):
                vmsg["writer"] += t
            else:
                vmsg["writer"].append(t)
        elif tag == '系列':
            tagline = get_values(contents[i])
            if isinstance(tagline, list):
                if len(tagline) > 0:
                    tagline = tagline[0]
                else:
                    tagline = ""
            vmsg["director"] = [tagline]
        elif tag == '日期':
            vmsg["release_date"] = contents[i].select('.value')[0].text
        elif tag == '類別':
            vmsg["genre"] = get_values(contents[i])
        elif tag == '演員':
            vmsg["actor"] = get_values(contents[i])
    backdrop = soup.select('.video-cover')[0].get("src")
    if backdrop.find("http") == -1:
        backdrop = "https:" + backdrop
    backdrop = "%s/javdb/img/%s" % (get_local(), base64_encode(backdrop))
    vmsg["extra"]["com.zanjo.javdb"]["backdrop"].append(backdrop)
    return vmsg


def search_javdb(query: str):
    query = query
    cache = get_cache("javdb", query)
    if cache is not None:
        return cache
    url = "%s/search?f=all&q=" % get_javdb_host()
    session = requests.session()
    session.headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39"
    }
    r = session.get(url + query)
    r = r.content.decode("utf-8")
    try:
        soup = BeautifulSoup(r, "lxml")
    except Exception as e:
        log().warning(r)
        raise e
    contents = soup.select("#videos .grid-item.column")
    res = []
    for i in range(len(contents)):
        if i > 5:
            break
        vid = contents[i].select("a")[0].get('href').replace("/v/", "")
        title = contents[i].select(".uid")[0].text.strip()
        sub_title = contents[i].select(".video-title")[0].text.strip()
        original_available = contents[i].select(".meta")[0].text.strip()
        poster = contents[i].select(".item-image > img")[0].get("data-src")
        if poster.find("http") == -1:
            poster = "https:" + poster
        poster = "%s/javdb/img/%s" % (get_local(), base64_encode(poster))
        vmsg = {
            "title": "%s %s" % (title, sub_title),
            "tagline": sub_title,
            "original_available": original_available,
            "original_title": title,
            "summary": sub_title,
            "certificate": "",
            "genre": [
            ],
            "actor": [],
            "director": "",
            "writer": [],
            "extra": {
                "com.zanjo.javdb": {
                    "poster": [poster],
                    "backdrop": []
                }
            }
        }
        tt = title.lower().strip()
        if i < 1 or tt == query or tt in query or query in tt:
            try:
                vmsg = get_data(session, vid, vmsg)
            except:
                log().trace()
        res.append(vmsg)
    resp = {

        "success": True,
        "result": res
    }
    write_cache("javdb", query, resp)
    return resp
