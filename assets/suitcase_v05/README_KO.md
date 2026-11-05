# 하늘색 캐리어 v05 — 내부 수납 구조

FBX: suitcase_skyblue_cm.fbx (cm 단위, 닫힌 상태)
GLB: suitcase_skyblue.glb
닫힌 원본: suitcase_skyblue.blend
열린 검토 원본: suitcase_interior_open.blend

## 내부 추가 모델
- 양쪽 전체 벽면의 천 안감, 바닥 테두리 봉제선, 입구 파이핑과 스티치
- 본체 바닥의 패딩 레일 커버
- 벽면 앵커 4개에 연결된 X자 웨빙 벨트, 가장자리 바인딩
- 분리된 버클 프레임/삽입부/해제부, 벨트 길이 조절 부품
- 뚜껑의 별도 지퍼식 칸막이 패널
- 칸막이 둘레 지퍼 테이프/개별 이빨/슬라이더/당김고리
- 상단 다이아몬드 망사 포켓, 옆/밑 거싯, 포켓 지퍼
- 하단 수납 포켓 2개, 옆/밑 거싯, 입구 마감과 봉제선
- 작은 무지 케어 라벨
- 안감/벨트 직조 이미지 텍스처 2종과 UV. Blender 원본에는 미세 bump 추가.

뚜껑은 Lid_Hinge_OPEN_Z 로컬 Z -115도로 개방.
Interior_Divider_MOVE_WITH_LID는 뚜껑에 속한 칸막이 그룹이다.
칸막이는 별도 숨김/이동이 가능하지만 지퍼를 따라 실제로 접히는 천 시뮬레이션이나
자동 개폐 리깅은 포함하지 않는다. 지퍼 이빨은 시각적 디테일이다.
X자 벨트는 빈 캐리어 바닥에 내려놓은 형태. 짐을 채우는 장면에서는
짐 높이에 맞는 벨트 변형/애니메이션을 별도로 해야 한다.

## 검토
preview_open.png: 전체 개방 상태
preview_main_interior.png: 본체 내부
preview_lid_interior.png: 뚜껑 칸막이와 포켓

FBX 재가져오기에서 뚜껑 바퀴 추종을 검사한다.
장착 소켓과 케이스 연결도 이전 버전과 동일한 검사로 확인한다.
이는 Blender 내 검증이며 3ds Max / Unreal 직접 검증은 미수행.
Max에서 FBX 임포트 시 cm 단위 및 재질/이미지 경로를 확인한다.
안감 이미지는 textures 폴더에도 제공한다. Blender bump 노드는 Unreal에서
자동 재현되지 않을 수 있어 해당 이미지를 Bump/Normal 재질로 별도 연결해야 한다.
최종 언리얼용 LOD/콜리전, 스켈레탈 리그, nDisplay 투영 설정은 포함하지 않는다.

재생성: Blender 4.3.2에서 build_suitcase.py 실행 후 finish_portable.py 실행.

追加: 내부 하단에는 바퀴 장착부를 감싸는 천 패딩 커버를 추가했다.
finish_housing.py는 이번 제작 중 수정용 스크립트이며 재생성 시에는 실행하지 않는다
(build_suitcase.py에 이미 해당 수정이 포함되어 있다).
