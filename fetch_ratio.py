#!/usr/bin/env python3
"""세명대 2027 수시 경쟁률 페이지(uwayapply)에서 지정 학과 지원 현황을 추출한다.

사용법:
    python3 fetch_ratio.py            # 카톡 전송용 요약(200자 이내)
    python3 fetch_ratio.py --detail   # 전형별 상세 포함
    python3 fetch_ratio.py --log      # 요약 출력 + CSV 기록 + 차트 데이터 갱신
    python3 fetch_ratio.py --build    # 네트워크 없이 CSV -> docs/data.js 만 재생성
"""
import csv
import os
import re
import sys
import urllib.request
from datetime import datetime

URL = "https://ratio.uwayapply.com/Sl5Kclc6Yk1gJkpmJSY6Jko3ZlRm"

# (페이지상 학과명, 카톡 표기용 짧은 이름)
TARGETS = [
    ("AI컴퓨터학부", "AI컴퓨터"),
    ("스마트IT학부", "스마트IT"),
    ("전기전자공학과", "전기전자"),
    ("건축학과", "건축"),
    ("재난안전학과", "재난안전"),
    ("보건안전공학과", "보건안전"),
]

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "data", "ratio_history.csv")
SITE_DATA = os.path.join(BASE, "docs", "data.js")
CSV_HEADER = ["collected_at", "department", "capacity", "applicants", "applicants_extra"]

TAG = re.compile(r"<[^>]+>")
SECTION = re.compile(r'strTitleId_\w+"\s+class="bul">\s*(.*?)\s*경쟁률\s*현황', re.S)
ROW = re.compile(r"<tr[^>]*trFieldValue[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)


def fetch(url=URL):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("euc-kr", errors="replace")


def clean(cell):
    """셀에서 부제목(<br> 이후)과 태그를 제거한 텍스트."""
    cell = re.sub(r"<br>.*", "", cell, flags=re.S)
    return TAG.sub("", cell).replace("&nbsp;", " ").strip()


def parse(html):
    text = TAG.sub(" ", html)
    m = re.search(r"(\d{4})\D{1,2}\s*(\d{1,2})\D{1,2}\s*(\d{1,2})\D{1,3}\s*(\d{1,2})\s*시\s*(\d{1,2})", text)
    ts = "%d/%d %d:%02d" % tuple(int(m.group(i)) for i in (2, 3, 4, 5)) if m else "시각미확인"

    heads = list(SECTION.finditer(html))
    result = {name: [] for name, _ in TARGETS}
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(html)
        jeonhyeong = re.sub(r"\s+", "", h.group(1))
        for row in ROW.findall(html[h.end():end]):
            cells = [clean(c) for c in CELL.findall(row)]
            for name, _ in TARGETS:
                if name in cells:
                    j = cells.index(name)
                    mo_raw, ji_raw = (cells[j + 1: j + 3] + ["", ""])[:2]
                    mo = int(mo_raw) if mo_raw.isdigit() else None  # '2명 이내' 등 정원외
                    if ji_raw.isdigit():
                        result[name].append((jeonhyeong, mo, mo_raw, int(ji_raw)))
                    break
    return ts, result


def summarize(result):
    """학과별 (정원내 모집, 정원내 지원, 정원외 지원)."""
    out = {}
    for name, _ in TARGETS:
        mo = sum(r[1] for r in result[name] if r[1] is not None)
        ji_in = sum(r[3] for r in result[name] if r[1] is not None)
        ji_out = sum(r[3] for r in result[name] if r[1] is None)
        out[name] = (mo, ji_in, ji_out)
    return out


def build_message(ts, result):
    """카톡 200자 제한에 맞춘 요약. 형식: 학과 지원/모집 경쟁률 [+정원외지원]"""
    s = summarize(result)
    lines = ["[세명대수시] %s 기준 (지원/모집)" % ts]
    for name, short in TARGETS:
        mo, ji_in, ji_out = s[name]
        extra = " +%d" % ji_out if ji_out else ""
        lines.append("%s %d/%d %.2f%s" % (short, ji_in, mo, ji_in / mo if mo else 0, extra))
    lines.append("※+는 정원외 지원")
    msg = "\n".join(lines)
    return msg[:200]


# --- 이력 기록 -------------------------------------------------------------

def to_iso(ts, year=None):
    """페이지 기준시각 '9/9 16:20' -> '2026-09-09T16:20'."""
    m = re.match(r"(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})", ts)
    if not m:
        return None
    mo, d, h, mi = (int(g) for g in m.groups())
    return "%04d-%02d-%02dT%02d:%02d" % (year or datetime.now().year, mo, d, h, mi)


def read_history():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def log_history(ts, result):
    """한 시점을 CSV에 덧붙인다. 같은 기준시각이 이미 있으면 건너뛴다."""
    stamp = to_iso(ts)
    if stamp is None:
        return False
    if any(r["collected_at"] == stamp for r in read_history()):
        return False
    s = summarize(result)
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    fresh = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if fresh:
            w.writerow(CSV_HEADER)
        for name, _ in TARGETS:
            mo, ji_in, ji_out = s[name]
            w.writerow([stamp, name, mo, ji_in, ji_out])
    return True


def build_site():
    """CSV 전체를 docs/data.js 로 굽는다. GitHub Pages 차트가 읽는 파일."""
    order = [name for name, _ in TARGETS]
    by_ts = {}
    for r in read_history():
        by_ts.setdefault(r["collected_at"], {})[r["department"]] = r
    stamps = sorted(t for t, v in by_ts.items() if len(v) == len(order))
    caps = [int(by_ts[stamps[-1]][n]["capacity"]) for n in order] if stamps else [0] * len(order)

    out = ["// 자동 생성 파일 - fetch_ratio.py --build 로 갱신한다. 직접 고치지 말 것.",
           "const CHART = {",
           "  depts: [",
           ",\n".join('    { name: "%s", short: "%s", cap: %d }' % (n, s, c)
                      for (n, s), c in zip(TARGETS, caps)),
           "  ],",
           "  rows: ["]
    for t in stamps:
        out.append('    ["%s",[%s],[%s]],' % (
            t,
            ",".join(by_ts[t][n]["applicants"] for n in order),
            ",".join(by_ts[t][n]["applicants_extra"] for n in order)))
    out += ["  ]", "};", ""]

    os.makedirs(os.path.dirname(SITE_DATA), exist_ok=True)
    with open(SITE_DATA, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    return len(stamps)


def main():
    if "--build" in sys.argv:
        print("docs/data.js 갱신 - %d개 시점" % build_site())
        return

    ts, result = parse(fetch())
    print(build_message(ts, result))

    if "--log" in sys.argv:
        # 진단은 stderr 로 - stdout 은 카톡에 그대로 보낼 메시지만 남긴다.
        added = log_history(ts, result)
        sys.stderr.write("[log] %s · CSV %s · docs/data.js %d개 시점\n"
                         % (ts, "추가함" if added else "이미 있어 건너뜀", build_site()))

    if "--detail" in sys.argv:
        print("\n=== 전형별 상세 ===")
        for name, _ in TARGETS:
            print("\n[%s]" % name)
            for j, mo, mo_raw, ji in result[name]:
                ratio = "%.2f:1" % (ji / mo) if mo else "-"
                print("  %-34s 모집 %-8s 지원 %3d  %s" % (j, mo_raw, ji, ratio))


if __name__ == "__main__":
    main()
