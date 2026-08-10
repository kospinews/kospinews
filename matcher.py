# -*- coding: utf-8 -*-
# matcher.py
# 회사명+키워드 정밀 매칭 필터.
# 목적: 단순 문자열 포함(in)으로 생기는 오탐(false positive) 제거.
#   - 한글 경계 판정: 회사명 앞뒤가 또 다른 한글이면 더 긴 단어의 일부 -> 제외 (한전 vs 한전료)
#   - 조사/사업접미 인정: 뒤에 조사(이/가/은/는/의...) 또는 사업접미(전자/증권/생명...)면 회사로 인정
#   - 모호사명 강화: 일반명사와 겹치는 짧은 사명은 사업접미가 있어야만 채택

# 사업접미(회사 정체성을 드러내는 꼬리표)
BIZ_SUFFIX = [
    "전자", "증권", "생명", "화학", "제약", "바이오", "건설", "重工業", "중공업",
    "제철", "홀딩스", "지주", "카드", "은행", "보험", "물산", "상사", "해운",
    "항공", "통신", "에너지", "전기", "정밀", "산업", "그룹", "제강", "百貨店",
    "백화점", "유통", "식품", "제과", "타이어", "전력", "가스", "조선",
]

# 조사
JOSA = ["이", "가", "은", "는", "을", "를", "의", "에", "와", "과", "도", "만", "로", "으로", "측", "사"]

# 일반명사와 겹치는 모호 사명(사업접미 없이는 채택 금지)
AMBIGUOUS = ["동양", "대한", "미래", "한국", "현대", "삼양", "무학", "한일", "고려", "신세계", "일신", "대성"]

def _is_hangul(ch):
    return "\uac00" <= ch <= "\ud7a3"

def company_hit(text, company):
    # 정밀 판정: text 안에서 company 가 '회사'로서 등장하는지
    if not text or not company:
        return False
    norm = company.replace("㈜", "").replace("(주)", "").replace("주식회사", "").strip()
    if not norm:
        return False
    start = 0
    ambiguous = norm in AMBIGUOUS
    while True:
        idx = text.find(norm, start)
        if idx == -1:
            return False
        prev = text[idx - 1] if idx > 0 else ""
        after = text[idx + len(norm):]
        nxt = after[0] if after else ""
        # 1) 앞 글자가 한글이면 더 긴 단어의 일부 -> skip
        if prev and _is_hangul(prev):
            start = idx + 1
            continue
        # 2) 사업접미가 바로 뒤에 붙으면 확실한 회사
        suffix_ok = any(after.startswith(s) for s in BIZ_SUFFIX)
        if suffix_ok:
            return True
        # 3) 모호사명은 사업접미가 없으면 채택 금지
        if ambiguous:
            start = idx + 1
            continue
        # 4) 뒤 글자가 한글인데 사업접미가 아니면(예: 한전료) 제외
        if nxt and _is_hangul(nxt):
            josa_ok = any(after.startswith(j) for j in JOSA)
            if not josa_ok:
                start = idx + 1
                continue
        # 5) 경계 OK (문장부호/공백/조사/문장끝) -> 회사로 인정
        return True

def match_article(text, company, keywords):
    # 회사명 정밀 매칭 + 키워드(단순 포함) 동시 충족 시 매칭 키워드 리스트 반환
    if not company_hit(text, company):
        return []
    return [k for k in keywords if k in text]
