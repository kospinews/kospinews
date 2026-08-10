# -*- coding: utf-8 -*-
# feeds.py
# 대상 신문 30개사 RSS 목록.
#   status "ok"     : 공식 RSS 확인/확정된 매체 (즉시 편입)
#   status "verify" : 후보 주소. check_feeds.py 로 살아있는지 검증 후 편입.
#                     죽어 있으면(naver=True) 네이버 언론사홈으로 자동 우회.
# category : 조간/석간 구분 (오전/오후 발송 강조용)

FEEDS = [
    # ---------- 중앙일간지 (조간) ----------
    {"name": "조선일보",   "url": "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml", "status": "ok",     "category": "조간", "naver_oid": "023"},
    {"name": "중앙일보",   "url": "https://rss.joins.com/joins_news_list.xml",                     "status": "verify", "category": "조간", "naver_oid": "025", "naver": True},
    {"name": "동아일보",   "url": "https://rss.donga.com/total.xml",                               "status": "ok",     "category": "조간", "naver_oid": "020"},
    {"name": "한겨레",     "url": "https://www.hani.co.kr/rss/",                                   "status": "ok",     "category": "조간", "naver_oid": "028"},
    {"name": "경향신문",   "url": "https://www.khan.co.kr/rss/rssdata/total_news.xml",             "status": "ok",     "category": "조간", "naver_oid": "032"},
    {"name": "국민일보",   "url": "https://www.kmib.co.kr/rss/data/kmibRssAll.xml",                "status": "ok",     "category": "조간", "naver_oid": "005"},
    {"name": "한국일보",   "url": "https://www.hankookilbo.com/rss/all",                           "status": "verify", "category": "조간", "naver_oid": "469", "naver": True},
    {"name": "세계일보",   "url": "https://www.segye.com/Articles/RSSList/segye_recent.xml",       "status": "ok",     "category": "조간", "naver_oid": "022"},
    {"name": "서울신문",   "url": "https://www.seoul.co.kr/xml/rss/rss_economy.xml",               "status": "ok",     "category": "조간", "naver_oid": "081"},
    {"name": "아시아투데이","url": "https://www.asiatoday.co.kr/rss/rss_all.xml",                   "status": "verify", "category": "조간", "naver_oid": "586", "naver": True},

    # ---------- 중앙경제지 (조간) ----------
    {"name": "매일경제",   "url": "https://www.mk.co.kr/rss/30000001/",                            "status": "ok",     "category": "조간", "naver_oid": "009"},
    {"name": "한국경제",   "url": "https://www.hankyung.com/feed/all-news",                        "status": "verify", "category": "조간", "naver_oid": "015"},
    {"name": "서울경제",   "url": "https://www.sedaily.com/RSS/Total.xml",                         "status": "ok",     "category": "조간", "naver_oid": "011"},
    {"name": "이데일리",   "url": "https://rss.edaily.co.kr/edaily_news.xml",                      "status": "ok",     "category": "조간", "naver_oid": "018"},
    {"name": "머니투데이", "url": "https://rss.mt.co.kr/mt_news.xml",                              "status": "ok",     "category": "조간", "naver_oid": "008"},
    {"name": "파이낸셜뉴스","url": "https://www.fnnews.com/rss/fn_realnews_all.xml",               "status": "ok",     "category": "조간", "naver_oid": "014"},
    {"name": "전자신문",   "url": "https://rss.etnews.com/Section901.xml",                         "status": "ok",     "category": "조간", "naver_oid": "030"},
    {"name": "아주경제",   "url": "https://www.ajunews.com/rss/economy.xml",                       "status": "ok",     "category": "조간", "naver_oid": "277"},
    {"name": "이투데이",   "url": "https://rss.etoday.co.kr/eto/etoday_news_all.xml",              "status": "ok",     "category": "조간", "naver_oid": "662"},
    {"name": "뉴스토마토", "url": "https://www.newstomato.com/rss/rss.aspx",                       "status": "verify", "category": "조간", "naver_oid": "204", "naver": True},

    # ---------- 석간지 ----------
    {"name": "문화일보",   "url": "https://www.munhwa.com/rss/total.xml",                          "status": "verify", "category": "석간", "naver_oid": "021", "naver": True},
    {"name": "아시아경제", "url": "https://www.asiae.co.kr/rss/all.htm",                           "status": "ok",     "category": "석간", "naver_oid": "277"},
    {"name": "헤럴드경제", "url": "https://biz.heraldcorp.com/rss/010000000000.xml",               "status": "ok",     "category": "석간", "naver_oid": "016"},
    {"name": "내일신문",   "url": "https://www.naeil.com/rss/all.xml",                             "status": "verify", "category": "석간", "naver_oid": "086", "naver": True},

    # ---------- 전문지/종합일간지 ----------
    {"name": "메트로경제", "url": "", "status": "verify", "category": "조간", "naver_oid": None},

    # ---------- 지방지(부산·울산·경남) ----------
    {"name": "부산일보",   "url": "https://www.busan.com/rss/allArticle.xml",                      "status": "verify", "category": "조간", "naver_oid": "082", "naver": True},
    {"name": "국제신문",   "url": "https://www.kookje.co.kr/rss/rss.xml",                          "status": "verify", "category": "조간", "naver_oid": "658", "naver": True},

    # ---------- 온라인 경제신문 ----------
    {"name": "서울파이낸스","url": "https://www.seoulfn.com/rss/allArticle.xml",                    "status": "verify", "category": "조간", "naver_oid": None},
    {"name": "한국증권신문","url": "https://www.ksdaily.co.kr/rss/allArticle.xml",                  "status": "verify", "category": "조간", "naver_oid": None},
    {"name": "디지털타임스","url": "http://www.dt.co.kr/rss/economy.xml",                           "status": "verify", "category": "조간", "naver_oid": "029", "naver": True},
]

def all_feeds():
    return FEEDS

def naver_fallback_feeds():
    # RSS 검증 실패 시 네이버 우회 대상
    return [f for f in FEEDS if f.get("naver")]
