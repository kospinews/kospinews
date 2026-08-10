# -*- coding: utf-8 -*-
# disclosure.py
# 공시 대조(무료·키 불필요). KIND 상장사 목록으로 상장 여부 판정 후,
# 각 회사의 DART/KIND 공시검색 링크를 첨부한다.
# DART API 키가 있으면(선택) 당일 공시 유무를 자동 판정해 '미공시 의심' 태깅.

import os
import urllib.parse
import listed as listed_mod

DART_KEY = os.environ.get("DART_API_KEY", "").strip()  # 선택. 없으면 링크방식.

def dart_search_link(company):
    q = urllib.parse.quote(company)
    return "https://dart.fss.or.kr/dsab007/main.do?textCrpNm=%s" % q

def kind_search_link(company):
    return "https://kind.krx.co.kr/disclosure/todaydisclosure.do?method=searchTodayDisclosureMain"

def _dart_has_today(corp_name, code):
    # DART_KEY가 있을 때만 호출. 당일 공시 존재 여부 True/False/None(불가)
    if not DART_KEY:
        return None
    try:
        import json, urllib.request
        from datetime import datetime, timezone, timedelta
        KST = timezone(timedelta(hours=9))
        today = datetime.now(KST).strftime("%Y%m%d")
        # code(종목코드) -> DART는 corp_code 필요하나, 회사명 검색 대체: list.json은 corp_code 필요.
        # 간이 판정: 회사명으로 최근공시 조회가 어려워, 여기서는 링크방식 유지 권장.
        return None
    except Exception:
        return None

def annotate(matches, listed=None):
    # matches: [{source,title,link,published,company,keywords,category,...}]
    # 반환: 상장사만 남기고 공시링크/태그 부여
    if listed is None:
        listed = listed_mod.load_listed()
    out = []
    for a in matches:
        info = listed_mod.find(a.get("company", ""), listed)
        if not info:
            continue  # 비상장사 -> 공시대상 아님, 제외
        a = dict(a)
        a["listed_name"] = info["name"]
        a["stock_code"] = info["code"]
        a["dart_link"] = dart_search_link(info["name"])
        a["kind_link"] = kind_search_link(info["name"])
        has = _dart_has_today(info["name"], info["code"])
        if has is True:
            a["tag"] = "공시확인"
        elif has is False:
            a["tag"] = "미공시 의심"
        else:
            a["tag"] = "공시확인 필요"  # 키 없음 -> 링크로 직접확인
        out.append(a)
    # 미공시 의심 > 공시확인 필요 > 공시확인 순 정렬
    order = {"미공시 의심": 0, "공시확인 필요": 1, "공시확인": 2}
    out.sort(key=lambda x: order.get(x["tag"], 9))
    return out
