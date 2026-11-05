# 하늘색 캐리어 — 1차 모델링 초안

- `suitcase_skyblue_cm.fbx`: 3ds Max / Unreal 가져오기용, cm 기준.
- `suitcase_skyblue.blend`: 편집 가능한 Blender 원본. .max 파일은 아님.
- `suitcase_skyblue.glb`: 재질 포함 교환용.
- `preview_closed.png`, `preview_open.png`: 닫힘 / 열림 검토 이미지.
- `build_suitcase.py`: Blender 4.3에서 재생성: `blender -b -t 4 --python build_suitcase.py`.

## 구조와 조작

전체 높이 약 34.4cm, 폭 약 22cm, 두께 약 13cm의 임시 비율.
SUITCASE_ROOT_cm은 바닥 중심 기준. Body_Assembly와 Lid_Hinge_OPEN_Z로 분리.
뚜껑은 Lid_Hinge_OPEN_Z의 로컬 Z축을 0도에서 -115도로 회전하면 열린다.
TelescopicHandle_MOVE_Z의 로컬 Z 위치를 올려 인출식 손잡이를 연장한다.
Caster 부모는 방향 전환용이며 Wheel_Tire/Hub의 로컬 Z축은 차륜 축이다.
부품은 별도 메시이며 스켈레탈 리깅이나 애니메이션 클립은 포함하지 않는다.
내부는 패널과 테두리로 만든 빈 공간이며 안감과 고정 스트랩이 있다.

## 가져오기

3ds Max 시스템 단위를 centimeters로 설정하고 FBX를 가져온다.
Unreal에서는 초기 검토 시 Combine Meshes를 끈다. 개별 Static Mesh 임포트는
원본 부모/회전축 구성을 그대로 재현하지 않을 수 있으므로, Max에서 피벗을
확인하고 FBX Scene Import 또는 Blueprint 부품 배치를 사용한다.
실제 Max/Unreal 실행 검증은 아직 수행하지 않았다. 재질은 기본 PBR이며
프로시저럴 형상 중심의 초안이다. UV 기반 이미지 텍스처와 LOD, 콜리전은 미제작.
브랜드 로고는 없는 은색 명판으로 처리했다.

## 화면 기준

원본에만 DISPLAY_GUIDE_64x48cm_90deg 가이드와 관람 위치 마커가 포함된다.
두 수직 면은 90도, 관람 마커는 모서리에서 수평거리 150cm, 화면 중앙 높이 24cm.
이 가이드는 FBX/GLB에는 포함되지 않는다. 제품 검토 카메라는 설치 관람 카메라와
별도이며, 이 파일은 최종 nDisplay 설정이나 보정된 아나모픽 영상이 아니다.
실제 설치 높이가 정해지면 화면과 관람 마커를 함께 이동하고 눈높이를 재확인한다.

## v02 수정

직선 박스 조합을 연속된 라운드 사각 단면의 중공 쉘로 교체했다.
세로 리브의 끝을 둥글게 만들고, 얇은 이음선과 곡면 모서리 금속판을 적용했다.
앞쪽(y<0) 캐스터 두 개는 뚜껑에, 뒤쪽 두 개는 본체에 연결했다.
따라서 뚜껑을 열 때 앞쪽 바퀴 및 포크가 함께 움직인다.
FBX 재가져오기 후 뚜껑을 -115도 회전하여 바퀴 추종을 검증했다.
`validate.py`가 검증 절차이며 `validation.json`에 결과를 기록한다.
레퍼런스 사진/도안 기반의 근사 모델로, 실제 제품 CAD 치수 복제는 아니다.
개폐 애니메이션 클립, UV 이미지 텍스처, 실제 nDisplay 투영 검증은 포함하지 않는다.
