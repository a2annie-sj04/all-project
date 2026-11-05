# 접힌 티셔츠 — 현실감 개선 검토본 v02

기존 여행 소품 전체의 완성 업데이트가 아니라 티셔츠 한 개의 방향 검토본이다.
실사 사진/스캔을 복제한 모델은 아니며 천 시뮬레이션 결과도 아니다.

변경:
- 두꺼운 사각 슬랩을 얇은 앞/뒤 몸판과 곡선 측면 봉합으로 교체
- 아래로 접힌 소매와 밑단, 비대칭 실루엣
- 목 주변 당김 주름, 가장자리의 압축 주름, 작은 원단 굴곡
- 매끈한 튜브 형태의 목둘레를 납작한 리브 원단 띠로 변경
- 얇은 가슴 포켓, 열린 윗단과 3면 봉제, 목 안쪽 원단 라벨
- 기본색/거칠기/탄젠트 노멀 이미지와 UV, Blender 재질의 sheen

크기 약 9.11 x 9.89 x 0.63cm. 기존 캐리어와 같은 미니어처 기준이다.
FBX 재가져오기로 부품/UV/텍스처 이미지/치수 검증을 통과했다.
Max와 Unreal 직접 실행 검증은 아직 하지 않았다.

TShirt_Folded_Realism_v02_cm.fbx: 교환용 모델
TShirt_Folded_Realism_v02.glb: 재질 포함 모델
TShirt_Folded_Realism_v02.blend: 편집 원본과 검토 촬영 장면
textures/: Cotton_BaseColor / Cotton_Normal / Cotton_Roughness
preview_overall.png: 전체
preview_fold_detail.png: 접힌 가장자리
preview_collar_detail.png: 목과 원단 확대

Unreal에서 Normal/Roughness는 sRGB를 끄고 용도에 맞게 연결한다.
스캔 기반 텍스처, 애니메이션/리그, 옷 펼침, 게임용 LOD/콜리전은 포함하지 않는다.
재생성: Blender 4.3.2에서 build_tshirt.py 실행.
