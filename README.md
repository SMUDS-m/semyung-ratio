# 세명대 2027학년도 수시 지원 현황 추이

유웨이 경쟁률 페이지를 **매시간 자동 수집**해서 6개 학과의 지원 현황 변화를 그래프로 보여줍니다.

## 📊 그래프 보기

**<https://SMUDS-m.github.io/semyung-ratio/>**

선 끝에 각 학과의 **최신 경쟁률 숫자**가 표시됩니다. 경쟁률 ↔ 지원자 수 전환, 학과별 선택, 시점별 상세 값(마우스 올리기), 표 보기를 지원합니다.

## 대상 학과

AI컴퓨터학부 · 스마트IT학부 · 전기전자공학과 · 건축학과 · 재난안전학과 · 보건안전공학과

## 데이터

| 파일 | 내용 |
|---|---|
| `data/ratio_history.csv` | 원본 시계열 (시점 × 학과) |
| `docs/data.js` | CSV에서 생성한 차트용 데이터 |
| `docs/index.html` | 차트 페이지 (의존성 없는 순수 HTML/SVG) |

CSV 컬럼: `collected_at`(페이지 기준시각, KST), `department`, `capacity`(정원내 모집인원), `applicants`(정원내 지원인원), `applicants_extra`(정원외 지원인원)

## 사용법

```
python3 fetch_ratio.py            # 현재 현황 요약 출력
python3 fetch_ratio.py --detail   # 전형별 상세까지
python3 fetch_ratio.py --log      # 요약 + CSV 기록 + docs/data.js 갱신
python3 fetch_ratio.py --build    # 네트워크 없이 CSV -> docs/data.js 재생성
```

`--log`는 같은 기준시각이 이미 CSV에 있으면 건너뛰므로 여러 번 실행해도 중복되지 않습니다.

## 산출 방식

- **경쟁률 = 정원내 지원인원 ÷ 정원내 모집인원.** 페이지의 10개 전형에 흩어진 값을 학과 단위로 합산합니다.
- 정원외 전형(농어촌학생·특성화고교·기초생활수급자)은 모집인원이 `N명 이내`로 표기돼 분모를 만들 수 없어, 지원자 수만 `applicants_extra`로 따로 집계하고 경쟁률에서는 제외합니다.
- 수집 시각은 실행 시각이 아니라 **페이지가 표시하는 기준시각**입니다. 대학 측이 주기적으로 갱신하므로 실시간보다 1~2시간 늦을 수 있습니다.

## ⚠️ 주의

비공식 자동 수집 자료입니다. 정확한 수치는 반드시 [공식 페이지](https://ratio.uwayapply.com/Sl5Kclc6Yk1gJkpmJSY6Jko3ZlRm)를 확인하세요.
