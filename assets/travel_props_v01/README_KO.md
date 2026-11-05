# 캐리어 여행 소품 v01

캐리어 v05와 같은 cm 단위의 미니어처 소품이다. 실제 성인 의류/신발의
실측 크기가 아닌, 약 34cm 캐리어와 64 x 48cm 화면 구성에 맞춘 크기다.

## 파일
각 FBX/GLB는 원점 주변에 있는 소품 하나만 포함한다. 운동화는 좌우 별도 파일.
- Folded_TShirt_cm: 접힌 티셔츠, 목 구멍/리브 마감, 라벨, 가슴 포켓, 봉제선
- Folded_Pants_cm: 접힌 바지 층, 허리밴드, 벨트 고리, 단추/봉제선
- Sneaker_Left_cm / Sneaker_Right_cm: 발입구가 빈 갑피, 안감, 설포,
  아일렛, 교차 끈/매듭/고리, 중창/밑창/바닥 트레드, 힐 풀탭
- ToiletryPouch_cm: 패널 파이핑/봉제선, 지퍼 테이프/이빨/슬라이더/고리,
  양끝 고정부에 연결된 손잡이와 직조 라벨
- BaseballCap_cm: 안쪽이 빈 6패널 크라운, 밴드, 휘어진 챙, 봉제선,
  통기구 테두리, 상단 단추, 뒤쪽 조절 개구부/스트랩/버클

travel_props_studio.blend: 편집 가능한 전체 소품과 촬영 스튜디오.
packing_layout.blend: 기존 캐리어 v05 안에 소품을 배치한 수납 검토 장면.
asset_manifest.json: 각 소품의 최종 치수(cm).
textures/: 직조 기본색 이미지. Blender 파일에는 이미지도 패킹했다.
FBX에도 텍스처를 포함했으며, 가져오기 도구에 따라 재질 재연결이 필요할 수 있다.
Blender의 미세 bump는 Unreal 재질에서 별도로 구성해야 한다.

## 검토 이미지
preview_all.png: 전체 소품
preview_각소품이름.png: 각 소품 확대
preview_packing.png: 캐리어 수납 배치

## 검증 범위
validate_exports.py: FBX 6개를 다시 불러와 계층/메시/치수를 검사.
packing_check.py: 캐리어 내부의 보수적인 수납 범위와 소품 간 바운딩박스
겹침을 검사한다. 정밀 삼각형 충돌/천 시뮬레이션 검사가 아니다.
수납 검토 장면에서는 고정벨트를 임시로 숨겼다. 짐 위로 벨트를 채우는
애니메이션/변형은 포함하지 않았다. 원본 캐리어 파일은 수정하지 않는다.

정적 메시이며 자동 접힘/펼침, 천 시뮬레이션, 애니메이션 클립,
게임용 LOD/콜리전, 최종 nDisplay 투영 설정은 포함하지 않는다.
3ds Max/Unreal에서 직접 실행한 검증은 아직 하지 않았다.

## 재생성
Blender 4.3.2에서 이 폴더를 작업 경로로 사용한다.
1. blender -b -t 6 --python build_props.py
2. blender -b -t 6 --python refine_contacts.py
3. blender -b -t 6 --python refine_cloth.py
4. blender -b -t 6 --python refine_laces.py
5. blender -b -t 4 --python packing_check.py
6. blender -b -t 2 --python validate_exports.py
refine_contacts.py는 새로 생성한 원본에 한 번 적용하는 보정 단계다.
이미 보정된 원본에 반복 적용하지 않는다.
