# -*- coding: utf-8 -*-
# check_feeds.py
# verify 매체의 RSS 주소가 살아있는지 1회 점검.
#   [OK]        정상 응답(RSS 파싱 성공)
#   [DEAD]      응답 실패
#   [DEAD->NAVER] 실패했지만 네이버 우회(naver_oid) 대상 -> 수집시 자동 전환됨
# 결과를 feeds_health.json 으로 저장. (실행: python check_feeds.py)

import json, os
import urllib.request
import feeds as feeds_mod
from collect import parse_rss

UA = {"User-Agent": "Mozilla/5.0 (news-alert-service)"}

def check(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
        items = parse_rss(raw, "test")
        return len(items) > 0, len(items)
    except Exception as e:
        return False, str(e)[:60]

def main():
    report = {}
    print("%-14s %-8s %s" % ("매체", "상태", "비고"))
    print("-" * 60)
    for f in feeds_mod.all_feeds():
        if f["status"] != "verify":
            report[f["name"]] = "ok(고정)"
            continue
        alive, info = check(f["url"])
        if alive:
            status = "OK"
            note = "%d items" % info
        elif f.get("naver"):
            status = "DEAD->NAVER"
            note = "네이버 우회(oid %s)" % f.get("naver_oid")
        else:
            status = "DEAD"
            note = "URL 교체 필요: %s" % info
        report[f["name"]] = status
        print("%-14s %-12s %s" % (f["name"], status, note))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "feeds_health.json"), "w", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    print("\n저장: feeds_health.json")

if __name__ == "__main__":
    main()
