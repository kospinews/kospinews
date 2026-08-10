# -*- coding: utf-8 -*-
# listed.py
# KIND(한국거래소 상장공시)에서 유가증권시장 상장법인 목록을 API 키 없이 다운로드.
# 하루 1회만 실제 다운로드(20시간 캐시). urllib 표준 라이브러리만 사용.

import os, json, time, io
import urllib.request

KIND_URL = ("https://kind.krx.co.kr/corpgeneral/corpList.do"
            "?method=download&searchType=13&marketType=stockMkt")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "listed_cache.json")
CACHE_TTL = 20 * 3600  # 20시간
UA = {"User-Agent": "Mozilla/5.0 (news-alert-service)"}

def _download():
    req = urllib.request.Request(KIND_URL, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    # KIND 다운로드는 cp949(euc-kr) HTML table
    try:
        html = raw.decode("cp949")
    except UnicodeDecodeError:
        html = raw.decode("utf-8", "ignore")
    return _parse(html)

def _parse(html):
    # HTML <table> 안의 회사명/종목코드 컬럼 추출 (정규식 기반, 외부패키지 불필요)
    import re
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I)
    out = {}
    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)
        if len(cells) < 2:
            continue
        name = re.sub(r"<[^>]+>", "", cells[0]).strip()
        code = re.sub(r"<[^>]+>", "", cells[1]).strip()
        code = re.sub(r"[^0-9]", "", code)
        if not name or not code:
            continue
        if len(code) > 6:
            continue
        code = code.zfill(6)
        out[normalize(name)] = {"name": name, "code": code}
    return out

def normalize(name):
    # (주)/㈜/주식회사/공백 제거 후 비교용 표준화
    if not name:
        return ""
    s = name.replace("㈜", "").replace("(주)", "").replace("주식회사", "")
    s = s.replace(" ", "").replace("\u3000", "")
    return s.strip()

def _read_cache():
    if not os.path.exists(CACHE):
        return None
    try:
        with open(CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _write_cache(data):
    try:
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "data": data}, f, ensure_ascii=False)
    except Exception:
        pass

def load_listed(force=False):
    # 3단계 폴백: 유효캐시 -> 다운로드 -> 만료캐시(stale) -> {}
    cache = _read_cache()
    if cache and not force and (time.time() - cache.get("ts", 0) < CACHE_TTL):
        return cache["data"]
    try:
        data = _download()
        if data:
            _write_cache(data)
            return data
    except Exception as e:
        print("[listed] download failed:", e)
    if cache:
        print("[listed] using stale cache")
        return cache["data"]
    return {}

def find(company_text, listed=None):
    # 기사에서 뽑은 회사명이 상장사인지 조회. 반환: {name, code} or None
    if listed is None:
        listed = load_listed()
    return listed.get(normalize(company_text))
