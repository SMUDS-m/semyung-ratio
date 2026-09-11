// 자동 생성 - fetch_ratio.py 실행 때마다 갱신. 현재 시점 스냅샷만 담는다.
const BREAKDOWN = {
  at: "9/11 15:50",
  univ: {
    capIn: 1379, appIn: 5721, capOut: 80, appOut: 463,
    byType: [
      { name: "일반", cap: 803, app: 3003, outside: false },
      { name: "인문계고교", cap: 265, app: 1126, outside: false },
      { name: "사회배려", cap: 26, app: 113, outside: false },
      { name: "지역인재", cap: 98, app: 464, outside: false },
      { name: "지역인재(기회)", cap: 4, app: 23, outside: false },
      { name: "특성화고교", cap: 57, app: 89, outside: false },
      { name: "면접우수", cap: 93, app: 582, outside: false },
      { name: "SMU의료", cap: 33, app: 321, outside: false },
      { name: "농어촌", cap: 35, app: 195, outside: true },
      { name: "특성화고(외)", cap: 10, app: 64, outside: true },
      { name: "기초생활", cap: 35, app: 204, outside: true }
    ]
  },
  depts: {
    "AI컴퓨터학부": [
      { name: "일반", cap: 42, capRaw: "42", app: 70, outside: false },
      { name: "인문계고교", cap: 10, capRaw: "10", app: 21, outside: false },
      { name: "지역인재", cap: 3, capRaw: "3", app: 4, outside: false },
      { name: "특성화고교", cap: 5, capRaw: "5", app: 3, outside: false },
      { name: "농어촌", cap: 6, capRaw: "6명 이내", app: 2, outside: true },
      { name: "특성화고(외)", cap: 6, capRaw: "6명 이내", app: 1, outside: true },
      { name: "기초생활", cap: 6, capRaw: "6명 이내", app: 3, outside: true }
    ],
    "스마트IT학부": [
      { name: "일반", cap: 24, capRaw: "24", app: 24, outside: false },
      { name: "사회배려", cap: 3, capRaw: "3", app: 8, outside: false },
      { name: "지역인재", cap: 3, capRaw: "3", app: 5, outside: false },
      { name: "농어촌", cap: 4, capRaw: "4명 이내", app: 0, outside: true },
      { name: "특성화고(외)", cap: 4, capRaw: "4명 이내", app: 1, outside: true },
      { name: "기초생활", cap: 4, capRaw: "4명 이내", app: 2, outside: true }
    ],
    "전기전자공학과": [
      { name: "일반", cap: 25, capRaw: "25", app: 120, outside: false },
      { name: "인문계고교", cap: 5, capRaw: "5", app: 53, outside: false },
      { name: "특성화고교", cap: 5, capRaw: "5", app: 13, outside: false },
      { name: "농어촌", cap: 4, capRaw: "4명 이내", app: 3, outside: true },
      { name: "특성화고(외)", cap: 4, capRaw: "4명 이내", app: 6, outside: true },
      { name: "기초생활", cap: 4, capRaw: "4명 이내", app: 4, outside: true }
    ],
    "건축학과": [
      { name: "일반", cap: 35, capRaw: "35", app: 86, outside: false },
      { name: "농어촌", cap: 3, capRaw: "3명 이내", app: 1, outside: true },
      { name: "특성화고(외)", cap: 3, capRaw: "3명 이내", app: 4, outside: true },
      { name: "기초생활", cap: 3, capRaw: "3명 이내", app: 4, outside: true }
    ],
    "재난안전학과": [
      { name: "일반", cap: 20, capRaw: "20", app: 61, outside: false },
      { name: "특성화고교", cap: 5, capRaw: "5", app: 1, outside: false },
      { name: "농어촌", cap: 2, capRaw: "2명 이내", app: 0, outside: true },
      { name: "특성화고(외)", cap: 2, capRaw: "2명 이내", app: 2, outside: true },
      { name: "기초생활", cap: 2, capRaw: "2명 이내", app: 1, outside: true }
    ],
    "보건안전공학과": [
      { name: "일반", cap: 20, capRaw: "20", app: 46, outside: false },
      { name: "지역인재", cap: 5, capRaw: "5", app: 13, outside: false },
      { name: "특성화고교", cap: 2, capRaw: "2", app: 3, outside: false },
      { name: "농어촌", cap: 2, capRaw: "2명 이내", app: 1, outside: true },
      { name: "특성화고(외)", cap: 2, capRaw: "2명 이내", app: 2, outside: true },
      { name: "기초생활", cap: 2, capRaw: "2명 이내", app: 1, outside: true }
    ]
  }
};
