# -*- coding: utf-8 -*-
# naver_fallback.py
# RSS 검증 실패(DEAD) 매체를 네이버 언론사홈(oid)에서 우회 수집.
# API 키/토큰 없이 표준 라이브러리만 사용. 하루 3회 저빈도 접근.
# 주의: 네이버 페이지 구조 변경 시 파서 보정이 필요할 수 있음(로그로 표시).

import re, json, time
import urllib.request
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
UA = {"User-Agent": "Mozilla/5.0 (news-alert-service)"}

def _fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    for enc in ("utf-8", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")

def fetch_press(oid, press_name, limit=40):
    # 네이버 언론사홈 최신기사 목록 수집. 반환: [{title, link, source, published}]
    url = "https://media.naver.com/press/%s/newspaper" % oid
    items = []
    try:
        html = _fetch(url)
    except Exception as e:
        print("[naver] fetch fail %s(%s): %s" % (press_name, oid, e))
        return items
    # 기사 링크 패턴: /article/<oid>/<aid>
    seen = set()
    for m in re.finditer(r'href="(https://n\.news\.naver\.com/article/%s/(\d+)[^"]*)"[^>]*>(.*?)</a>' % oid, html, re.S):
        link, aid, inner = m.group(1), m.group(2), m.group(3)
        title = re.sub(r"<[^>]+>", "", inner).strip()
        if not title or aid in seen:
            continue
        seen.add(aid)
        items.append({
            "title": title,
            "link": link.split("?")[0],
            "source": press_name,
            "published": datetime.now(KST).isoformat(),  # 목록에 정확 시각 없으면 수집시각
            "via": "naver",
        })
        if len(items) >= limit:
            break
    print("[naver] %s(%s): %d items" % (press_name, oid, len(items)))
    return items
