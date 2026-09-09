#!/bin/bash
# 매시간 실행: 경쟁률 수집 -> CSV 기록 -> 차트 데이터 갱신 -> GitHub 반영.
# stdout 에는 카카오톡으로 보낼 메시지만 나온다. 진행 상황/오류는 stderr.
set -o pipefail
cd "$(dirname "$0")" || exit 1

msg=$(python3 fetch_ratio.py --log)
rc=$?
if [ $rc -ne 0 ] || [ -z "$msg" ]; then
  echo "[세명대수시] 경쟁률 조회 실패 - 페이지 확인 필요"
  echo "fetch 실패 (exit $rc)" >&2
  exit 0
fi

echo "$msg"          # <- 카톡 본문

if [ -n "$(git status --porcelain data docs)" ]; then
  git add data docs >&2
  git -c user.email=ds2eye@gmail.com -c user.name=SMUDS-m \
      commit -q -m "데이터 갱신: $(date '+%Y-%m-%d %H:%M')" >&2 \
    && git push -q origin main >&2 \
    && echo "GitHub 반영 완료" >&2 \
    || echo "GitHub 반영 실패 - 다음 실행 때 함께 올라감" >&2
else
  echo "변경 없음 - 커밋 건너뜀" >&2
fi
exit 0
