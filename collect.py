# -*- coding: utf-8 -*-
# collect.py
# 30분 주기로 30개사 RSS를 폴링하여 store.json 에 누적(기사 최초 배포시각 pubDate 저장).
# RSS 실패/빈 응답 + naver_oid 보유 매체는 네이버 언론사홈으로 자동 우회.
# 표준 라이브러리만 사용(외부 패키지 불필요).

import os, json, time
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

import feeds as feeds_mod
import naver_fallback as nf

KST = timezone(timedelta(hours=9))
UA = {"User-Agent": "Mozilla/5.0 (news-alert-service)"}
STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store.json")
RETAIN_HOURS = 48

def _fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def _parse_dt(s):
    if not s:
        return None
    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=KST)
        return dt.astimezone(KST)
    except Exception:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(s.strip()[:25], fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=KST)
            return dt.astimezone(KST)
        except Exception:
            continue
    return None

def parse_rss(xml_bytes, source):
    items = []
    try:
        root = ET.fromstring(xml_bytes)
    except Exception:
        try:
            root = ET.fromstring(xml_bytes.decode("utf-8", "ignore"))
        except Exception:
            return items
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date")
        desc = (it.findtext("description") or "").strip()
        dt = _parse_dt(pub) or datetime.now(KST)
        if title and link:
            items.append({"source": source, "title": title, "link": link.split("?")[0],
                          "published": dt.isoformat(), "summary": desc, "via": "rss"})
    if not items:
        ns = "{http://www.w3.org/2005/Atom}"
        for it in root.iter(ns + "entry"):
            title = (it.findtext(ns + "title") or "").strip()
            le = it.find(ns + "link")
            link = le.get("href") if le is not None else ""
            pub = it.findtext(ns + "updated") or it.findtext(ns + "published")
            dt = _parse_dt(pub) or datetime.now(KST)
            if title and link:
                items.append({"source": source, "title": title, "link": link.split("?")[0],
                              "published": dt.isoformat(), "summary": "", "via": "rss"})
    return items

def collect_one(feed):
    name = feed["name"]
    got = []
    try:
        raw = _fetch(feed["url"])
        got = parse_rss(raw, name)
    except Exception as e:
        print("[rss] %s fail: %s" % (name, e))
    if not got and feed.get("naver_oid") and feed.get("naver"):
        got = nf.fetch_press(feed["naver_oid"], name)
    return got

def load_store():
    if os.path.exists(STORE):
        try:
            with open(STORE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_store(store):
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False)

def prune(store):
    cutoff = datetime.now(KST) - timedelta(hours=RETAIN_HOURS)
    for link in list(store.keys()):
        dt = _parse_dt(store[link].get("published"))
        if dt and dt < cutoff:
            del store[link]

def run():
    store = load_store()
    total = 0
    for f in feeds_mod.all_feeds():
        for it in collect_one(f):
            link = it["link"]
            if link not in store:
                store[link] = it
                total += 1
    prune(store)
    save_store(store)
    print("[collect] %s | new=%d total=%d" % (datetime.now(KST).strftime("%m-%d %H:%M"), total, len(store)))

if __name__ == "__main__":
    run()
