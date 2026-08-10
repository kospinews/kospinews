# -*- coding: utf-8 -*-
# notify.py
# store.json 에서 발송 구간(최초 배포시각 기준)의 기사를 잘라
#   회사명(정밀필터)+키워드 동시 매칭 -> 상장사 판정 -> 공시링크/태그 -> Gmail 발송.
# 발송 슬롯: morning(06:20) / afternoon1(13:00) / afternoon2(14:20)
# 환경변수: GMAIL_USER, GMAIL_APP_PW, MAIL_TO, (선택)RUN_SLOT, DART_API_KEY

import os, sys, ssl, smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, timezone, timedelta

import feeds as feeds_mod
import keywords as kw_mod
import matcher
import listed as listed_mod
import disclosure
from collect import load_store, _parse_dt

KST = timezone(timedelta(hours=9))

def prev_business_day(d):
    x = d - timedelta(days=1)
    while x.weekday() >= 5:  # 5=토,6=일
        x -= timedelta(days=1)
    return x

def at(d, h, m):
    return d.replace(hour=h, minute=m, second=0, microsecond=0)

def compute_window(slot, now=None):
    now = now or datetime.now(KST)
    today = now
    if slot == "morning":       # 전영업일 14:20 ~ 당일 06:20
        start = at(prev_business_day(today), 14, 20)
        end = at(today, 6, 20)
    elif slot == "afternoon1":  # 당일 06:20 ~ 13:00
        start = at(today, 6, 20)
        end = at(today, 13, 0)
    elif slot == "afternoon2":  # 당일 13:00 ~ 14:20
        start = at(today, 13, 0)
        end = at(today, 14, 20)
    else:
        start = at(prev_business_day(today), 14, 20)
        end = now
    return start, end

def detect_slot(now=None):
    now = now or datetime.now(KST)
    hm = now.hour * 60 + now.minute
    if hm < 10 * 60:
        return "morning"
    if hm < 13 * 60 + 40:
        return "afternoon1"
    return "afternoon2"

def in_window(iso, start, end):
    dt = _parse_dt(iso)
    return dt is not None and start <= dt <= end

def build_matches(window_items, listed):
    # listed: {normname: {name,code}}  -> 회사명 목록
    names = [v["name"] for v in listed.values()]
    results = []
    for a in window_items:
        text = (a.get("title", "") + " " + a.get("summary", "")).strip()
        matched_company = None
        for nm in names:
            if matcher.company_hit(text, nm):
                matched_company = nm
                break
        if not matched_company:
            continue
        hits = [k for k in kw_mod.KEYWORDS if k in text]
        if not hits:
            continue
        cats = sorted({kw_mod.classify(k) for k in hits})
        results.append({
            "source": a.get("source"), "title": a.get("title"),
            "link": a.get("link"), "published": a.get("published"),
            "company": matched_company, "keywords": hits,
            "categories": cats, "via": a.get("via", "rss"),
        })
    return results

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

TAG_COLOR = {"미공시 의심": "#b91c1c", "공시확인 필요": "#b45309", "공시확인": "#15803d"}

def render_html(slot, start, end, rows, feed_report):
    slot_ko = {"morning": "오전(06:20)", "afternoon1": "오후 1차(13:00)", "afternoon2": "오후 2차(14:20)"}[slot]
    P = []
    P.append("<div style='font-family:Pretendard,Arial,sans-serif;color:#111827;max-width:860px'>")
    P.append("<h2 style='margin:0 0 4px'>유가증권시장 공시성 보도 알림 - " + slot_ko + "</h2>")
    P.append("<div style='color:#6b7280;font-size:13px;margin-bottom:14px'>수집구간(최초 배포시각): "
             + start.strftime("%m/%d %H:%M") + " ~ " + end.strftime("%m/%d %H:%M")
             + " | 매칭 " + str(len(rows)) + "건</div>")
    if not rows:
        P.append("<p style='padding:12px;background:#f3f4f6;border-radius:8px'>해당 구간에 회사명+키워드가 동시 등장한 상장사 보도가 없습니다.</p>")
    else:
        P.append("<table style='border-collapse:collapse;width:100%;font-size:13px'>")
        P.append("<tr style='background:#f9fafb;text-align:left'>"
                 "<th style='padding:6px;border-bottom:1px solid #e5e7eb'>태그</th>"
                 "<th style='padding:6px;border-bottom:1px solid #e5e7eb'>회사(종목)</th>"
                 "<th style='padding:6px;border-bottom:1px solid #e5e7eb'>제목/매체</th>"
                 "<th style='padding:6px;border-bottom:1px solid #e5e7eb'>키워드/분류</th>"
                 "<th style='padding:6px;border-bottom:1px solid #e5e7eb'>공시확인</th></tr>")
        for r in rows:
            c = TAG_COLOR.get(r["tag"], "#374151")
            kw = ", ".join(r["keywords"][:6])
            cat = " / ".join(r["categories"][:2])
            pub = _parse_dt(r["published"])
            pubs = pub.strftime("%m/%d %H:%M") if pub else ""
            via = " (네이버우회)" if r.get("via") == "naver" else ""
            P.append("<tr>")
            P.append("<td style='padding:6px;border-bottom:1px solid #f1f5f9;color:%s;font-weight:600;white-space:nowrap'>%s</td>" % (c, r["tag"]))
            P.append("<td style='padding:6px;border-bottom:1px solid #f1f5f9;white-space:nowrap'>%s<br><span style='color:#6b7280'>%s</span></td>" % (esc(r["listed_name"]), r["stock_code"]))
            P.append("<td style='padding:6px;border-bottom:1px solid #f1f5f9'><a href='%s' style='color:#2563eb;text-decoration:none'>%s</a><br><span style='color:#6b7280'>%s%s · %s</span></td>" % (esc(r["link"]), esc(r["title"]), esc(r["source"]), via, pubs))
            P.append("<td style='padding:6px;border-bottom:1px solid #f1f5f9'>%s<br><span style='color:#6b7280'>%s</span></td>" % (esc(kw), esc(cat)))
            P.append("<td style='padding:6px;border-bottom:1px solid #f1f5f9;white-space:nowrap'><a href='%s' style='color:#2563eb'>DART</a> · <a href='%s' style='color:#2563eb'>KIND</a></td>" % (r["dart_link"], r["kind_link"]))
            P.append("</tr>")
        P.append("</table>")
    # 태그 범례
    P.append("<div style='margin-top:14px;font-size:12px;color:#6b7280'>"
             "<b>태그</b> "
             "<span style='color:#b91c1c'>미공시 의심</span>=보도有·자동확인시 공시無 / "
             "<span style='color:#b45309'>공시확인 필요</span>=DART키 미사용, 링크로 직접확인 / "
             "<span style='color:#15803d'>공시확인</span>=자동확인됨</div>")
    # 매체 수집 리포트(투명성)
    if feed_report:
        P.append("<div style='margin-top:10px;font-size:12px;color:#6b7280'><b>수집 매체 현황</b><br>" + esc(feed_report) + "</div>")
    P.append("<div style='margin-top:16px;font-size:11px;color:#9ca3af'>공시 원문: DART https://dart.fss.or.kr · KIND https://kind.krx.co.kr</div>")
    P.append("</div>")
    return "\n".join(P)

def feed_status_report():
    ok = [f["name"] for f in feeds_mod.all_feeds() if f["status"] == "ok"]
    verify = [f["name"] for f in feeds_mod.all_feeds() if f["status"] == "verify"]
    return ("정상연동 %d곳 · 검증대상 %d곳(check_feeds.py로 확정, 실패 시 네이버 우회). "
            "검증대상: %s") % (len(ok), len(verify), ", ".join(verify))

def send_email(subject, html):
    user = os.environ.get("GMAIL_USER", "").strip()
    pw = os.environ.get("GMAIL_APP_PW", "").replace(" ", "").strip()
    to = os.environ.get("MAIL_TO", user).strip()
    if not user or not pw:
        print("[mail] GMAIL_USER/GMAIL_APP_PW 미설정 -> 발송 생략(미리보기만)")
        return False
    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = user
    msg["To"] = to
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(user, pw)
        s.sendmail(user, [x.strip() for x in to.split(",") if x.strip()], msg.as_string())
    print("[mail] sent to", to)
    return True

def run(slot=None, now=None, dry=False):
    slot = slot or os.environ.get("RUN_SLOT") or detect_slot(now)
    start, end = compute_window(slot, now)
    store = load_store()
    window_items = [a for a in store.values() if in_window(a.get("published"), start, end)]
    listed = listed_mod.load_listed()
    matches = build_matches(window_items, listed)
    rows = disclosure.annotate(matches, listed)
    subject = "[공시성 보도] %s %d건 %s" % (
        {"morning": "오전", "afternoon1": "오후1", "afternoon2": "오후2"}[slot],
        len(rows), (end.strftime("%m/%d")))
    html = render_html(slot, start, end, rows, feed_status_report())
    if dry:
        return subject, html, rows
    send_email(subject, html)
    return subject, html, rows

if __name__ == "__main__":
    run()
