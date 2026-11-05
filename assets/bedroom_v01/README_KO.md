# 여행 출발 장면용 침실 v01

따뜻한 오크 바닥 / 세이지색 침구 / 린넨 커튼이 있는 침실 배경의 1차 검토 모델.
옷과 여행 소품 세트는 포함하지 않는다. 기존 캐리어는 별도 배치 검토 장면에만 넣었다.

## 주요 파일
- Bedroom_v01_cm.fbx: 3ds Max / Unreal 교환용 방 메시, cm 단위.
- Bedroom_v01.glb: 재질 포함 교환용.
- Bedroom_v01.blend: 편집 원본, 조명과 카메라, 화면 가이드 포함.
- Bedroom_with_case_reference.blend: 기존 캐리어 v05를 놓은 배치 검토 원본.
- textures/: 기본색/거칠기/탄젠트 노멀 이미지와 벽걸이 그림 그래픽.
- preview_room.png: 전체 방.
- preview_bed_detail.png: 침대와 주변 가구.
- preview_room_with_case.png: 캐리어 배치.
- display_left_256x192.png / display_right_256x192.png: 고정 관람 위치의 각 면 출력 참고.
- display_layout_reference.json: 화면 모서리, 관람 위치, Blender 카메라 수치.
- validation.json: 실제 수행한 검증 결과.

## 구성
Architecture: 마루 판재, 창 개구부가 있는 벽, 걸레받이/몰딩, 천장.
Bed_Assembly: 지지 다리/프레임, 매트리스, 헤드보드, 베개, 처진 이불과 접힌 커프.
Nightstand_Assembly: 협탁/서랍, 손잡이, 받침/기둥/갓/지지대가 분리된 조명.
Desk_Assembly / Chair_Assembly: 책상과 서랍, 의자, 노트와 머그컵.
Window_Assembly / Curtains_Assembly: 창틀/유리/창턱/손잡이, 주름 커튼/봉/링/클립.
Decor_Assembly / Plant_Assembly: 러그, 벽걸이 그림, 화분/줄기/곡면 잎.
가구는 별도 부모 그룹으로 묶었으며, 애니메이션이나 천 시뮬레이션은 포함하지 않는다.

## 화면과 크기
방의 가상 내부 바닥은 64 x 64cm, 벽 높이는 48cm.
일반 성인 침실 실측 크기가 아닌, 화면 안에 보일 가상 공간의 미니어처 좌표다.
침대 프레임은 36.5 x 42.5cm.
두 화면은 64 x 48cm씩 90도로 만난다.
왼쪽 면: (-64,0,0) ~ (0,0,48).
오른쪽 면: (0,0,0) ~ (0,64,48).
모서리 정면에서 수평거리 150cm, 눈높이 24cm를 가정했다.
각 면의 256 x 192 출력을 가로로 연결하면 512 x 192가 된다.
케이블/컨트롤러의 실제 면 순서와 좌우 반전은 현장에서 확인해야 한다.

Ceiling_Panel_DisplayOnly는 별도 천장이다. Blender 내부 검토 카메라에서는
hide_render=True로 두었고, 화면별 참고 출력 시에는 켠다. Unreal용 메시에는 포함된다.
화면별 카메라는 물리 화면 코너를 기준으로 한 off-axis 투영 참고이며,
직접 작성/검증한 Unreal nDisplay 설정 파일(.ndisplay)은 아니다.
JSON 좌표는 Blender의 오른손 Z-up 원본 좌표다. Unreal의 축 변환과 카메라 방향은
FBX 임포트 후 확인해야 한다. Unreal/실제 LED 화면에서의 실행 검증은 하지 않았다.

캐리어 배치 검토 장면은 원본 v05를 0.48배 균일 축소해 침대 위에 눕혔다.
가로·세로·두께 비율은 유지했다. 캐리어 원본 파일은 바꾸지 않았다.
전체 캐리어 개폐/이동 동선의 애니메이션 충돌 검사는 아직 하지 않았다.

## 가져오기
Max에서 시스템 단위 centimeters로 가져온다. 부품을 수정하려면 그룹 구조를 유지한다.
Unreal에서는 FBX Scene Import 또는 개별 메시/그룹 배치 방식으로 가져온다.
기본색은 sRGB, Normal과 Roughness는 Non-Color 용도로 설정한다.
Blender 조명/색관리와 Unreal 조명은 별도여서 엔진 내 라이팅 조정이 필요하다.
FBX는 방 메시만 포함하며, 조명과 카메라는 Blender 원본과 JSON을 참고한다.

## 검증
FBX 재가져오기로 부모 그룹/메시/침대 치수를 확인했다.
렌더에서 발견한 이불/매트리스 관통은 수정 후 평가 메시의 삼각형 교차 0건을 확인했다.
두 화면별 카메라는 각 화면의 세 모서리가 이미지의 해당 모서리에 투영되는지 검사했다.
전 가구의 정밀 충돌/구조 검증이나 최종 실사 품질 승인을 의미하지 않는다.

## 재생성
Blender 4.3.2에서 build_room.py 실행.
그다음 place_reference_case.py와 validate_room.py 실행.
캐리어 배치 재생성에는 ../suitcase_v05/suitcase_skyblue.blend가 필요하다.
add_ceiling.py는 초기 모델의 천장을 추가했던 보정 기록으로 재생성 시에는 필요 없다.
