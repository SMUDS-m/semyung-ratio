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
BREAKDOWN = os.path.join(BASE, "docs", "breakdown.js")
LASTYEAR = os.path.join(BASE, "docs", "lastyear.js")
CSV_HEADER = ["collected_at", "department", "capacity", "applicants", "applicants_extra",
              "capacity_general", "applicants_general"]

TAG = re.compile(r"<[^>]+>")
SECTION = re.compile(r'strTitleId_\w+"\s+class="bul">\s*(.*?)\s*경쟁률\s*현황', re.S)
ROW = re.compile(r"<tr[^>]*trFieldValue[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)


def fetch(url=URL):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("euc-kr", errors="replace")


def num(text):
    """'2,008' -> 2008. 숫자가 아니면(예: '3명 이내') None."""
    t = (text or "").replace(",", "").strip()
    return int(t) if t.isdigit() else None


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
                    mo = num(mo_raw)          # '2명 이내' 등 정원외는 None
                    ji = num(ji_raw)
                    if ji is not None:
                        result[name].append((jeonhyeong, mo, mo_raw, ji))
                    break
    return ts, result


# 전형명을 타일에 넣을 짧은 이름으로
SHORT_JEON = [
    ("SMU의료인재", "SMU의료"), ("지역인재(기회균형)", "지역인재(기회)"), ("지역인재(일반)", "지역인재"),
    ("사회배려자및봉사자", "사회배려"), ("특성화고교인재", "특성화고교"), ("인문계고교", "인문계고교"),
    ("면접우수자", "면접우수"), ("농어촌학생", "농어촌"), ("기초생활수급자", "기초생활"),
    ("특성화고교", "특성화고(외)"), ("일반", "일반"),
]


def short_jeon(name):
    for key, short in SHORT_JEON:
        if name.startswith(key):
            return short
    return re.sub(r"전형\(정원[내외]\)$", "", name)


def university_total(html):
    """맨 위 '전형별 경쟁률 현황' 요약표에서 대학 전체 수치를 합산한다.

    반환: (정원내 모집, 정원내 지원, 정원외 모집, 정원외 지원, [전형별 행])
    """
    heads = list(SECTION.finditer(html))
    if not heads or heads[0].group(1).strip() != "전형별":
        return None
    end = heads[1].start() if len(heads) > 1 else len(html)
    cap_in = app_in = cap_out = app_out = 0
    rows = []
    for row in ROW.findall(html[heads[0].end():end]):
        cells = [clean(c) for c in CELL.findall(row)]
        if len(cells) < 3:
            continue
        label = re.sub(r"^\[[^\]]*\]\s*", "", cells[0]).split(":")[0].strip()
        mo, ji = num(cells[1]), num(cells[2])
        if mo is None or ji is None:
            continue
        outside = "(정원외)" in label
        if outside:
            cap_out += mo; app_out += ji
        else:
            cap_in += mo; app_in += ji
        rows.append((short_jeon(label), mo, ji, outside))
    return cap_in, app_in, cap_out, app_out, rows


def build_breakdown(html, ts, result):
    """현재 시점의 대학 전체 + 학과별 전형내역을 docs/breakdown.js 로 굽는다."""
    uni = university_total(html)

    def js(v):
        return "null" if v is None else ('"%s"' % v if isinstance(v, str) else str(v))

    out = ["// 자동 생성 - fetch_ratio.py 실행 때마다 갱신. 현재 시점 스냅샷만 담는다.",
           "const BREAKDOWN = {", '  at: "%s",' % ts]
    if uni:
        ci, ai, co, ao, rows = uni
        out += ["  univ: {",
                "    capIn: %d, appIn: %d, capOut: %d, appOut: %d," % (ci, ai, co, ao),
                "    byType: [",
                ",\n".join('      { name: %s, cap: %d, app: %d, outside: %s }'
                            % (js(n), m, a, "true" if o else "false") for n, m, a, o in rows),
                "    ]", "  },"]
    out.append("  depts: {")
    parts = []
    for name, _ in TARGETS:
        rows = []
        for jeon, mo, mo_raw, ji in result[name]:
            outside = mo is None
            cap = mo
            if outside:
                # '6명 이내' 처럼 상한만 적힌 경우 그 숫자를 분모로 삼는다.
                m = re.search(r"(\d[\d,]*)\s*명", mo_raw or "")
                cap = num(m.group(1)) if m else None
            rows.append('      { name: %s, cap: %s, capRaw: %s, app: %d, outside: %s }'
                        % (js(short_jeon(jeon)), js(cap), js(mo_raw), ji,
                           "true" if outside else "false"))
        parts.append('    %s: [\n%s\n    ]' % (js(name), ",\n".join(rows)))
    out += [",\n".join(parts), "  }", "};", ""]

    os.makedirs(os.path.dirname(BREAKDOWN), exist_ok=True)
    with open(BREAKDOWN, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    return uni


def summarize(result):
    """학과별 (정원내 모집, 정원내 지원, 정원외 지원)."""
    out = {}
    for name, _ in TARGETS:
        mo = sum(r[1] for r in result[name] if r[1] is not None)
        ji_in = sum(r[3] for r in result[name] if r[1] is not None)
        ji_out = sum(r[3] for r in result[name] if r[1] is None)
        out[name] = (mo, ji_in, ji_out)
    return out


def general_only(result):
    """학생부교과 일반전형(정원내)만 추린 {학과: (모집, 지원)}.

    작년 공개 수치가 일반전형 단독이라, 같은 기준으로 비교하려면 이 값이 필요하다.
    """
    out = {}
    for name, _ in TARGETS:
        rows = [r for r in result[name] if r[0].startswith("일반전형") and r[1] is not None]
        out[name] = (sum(r[1] for r in rows), sum(r[3] for r in rows))
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
        g = general_only(result)
        for name, _ in TARGETS:
            mo, ji_in, ji_out = s[name]
            gmo, gji = g[name]
            w.writerow([stamp, name, mo, ji_in, ji_out, gmo, gji])
    return True


def build_site():
    """CSV 전체를 docs/data.js 로 굽는다. GitHub Pages 차트가 읽는 파일."""
    order = [name for name, _ in TARGETS]
    by_ts = {}
    for r in read_history():
        by_ts.setdefault(r["collected_at"], {})[r["department"]] = r
    stamps = sorted(t for t, v in by_ts.items() if len(v) == len(order))
    caps = [int(by_ts[stamps[-1]][n]["capacity"]) for n in order] if stamps else [0] * len(order)

    def gcap(n):
        """일반전형 모집인원 - 값이 있는 가장 최근 시점 기준."""
        for t in reversed(stamps):
            v = (by_ts[t][n].get("capacity_general") or "").strip()
            if v.isdigit() and int(v) > 0:
                return int(v)
        return 0

    gcaps = [gcap(n) for n in order]

    out = ["// 자동 생성 파일 - fetch_ratio.py --build 로 갱신한다. 직접 고치지 말 것.",
           "const CHART = {",
           "  depts: [",
           ",\n".join('    { name: "%s", short: "%s", cap: %d, capGen: %d }' % (n, s, c, gc)
                      for (n, s), c, gc in zip(TARGETS, caps, gcaps)),
           "  ],",
           "  // [기준시각, 정원내 지원, 정원외 지원, 일반전형 지원(없으면 null)]",
           "  rows: ["]
    for t in stamps:
        gen = []
        for n in order:
            v = (by_ts[t][n].get("applicants_general") or "").strip()
            gen.append(v if v.isdigit() else "null")
        out.append('    ["%s",[%s],[%s],[%s]],' % (
            t,
            ",".join(by_ts[t][n]["applicants"] for n in order),
            ",".join(by_ts[t][n]["applicants_extra"] for n in order),
            ",".join(gen)))
    out += ["  ]", "};", ""]

    os.makedirs(os.path.dirname(SITE_DATA), exist_ok=True)
    with open(SITE_DATA, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    return len(stamps)


def main():
    if "--build" in sys.argv:
        print("docs/data.js 갱신 - %d개 시점" % build_site())
        return

    html = fetch()
    ts, result = parse(html)
    print(build_message(ts, result))
    build_breakdown(html, ts, result)

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
