# omok
오목 인공지능 제작 프로젝트

# 설명
- 이 프로젝트는 **"알파제로를 분석하며 배우는 인공지능"** 의 모델구조와 탐색 구조를 카피하여 다른 게임으로 적용시켜 실제로 머신러닝의 기술을 활용하고 모델을 발전시키는 경험을 쌓기 위해 시작한 프로젝트입니다.
- [Jpub/AlphaZero: <알파제로를 분석하며 배우는 인공지능> 리포지토리 (github.com)](https://github.com/Jpub/AlphaZero)
# 무엇이 다른가요?

## 변경
 - state.py -> omok.py : 게임보드의 판을 3X3에서 15X15로 확장, 탐색트리를 좀 더 쉽게 찾아낼 수 있게 오목의 기초 전략 입력(smart_legal_actions)
 -  pv_mcts.py : 데이터 or 탐색횟수가 부족했을 때 index 0의 값을 자주 탐색, 이를 해결하기 위해 0을 탐색했을 때 탐색횟수를 조정하게 수정
 - dual_network.py : DN_INPUT_SHAPE = (15,15,2)로 변경
 - huamn_play.py : 게임보드판을 오목판으로 수정, 선후공을 변수로 조정할 수 있게 설정
 
## 추가
- train_human_play.py :  **기보학습**추가 [Renju Offline](http://renjuoffline.com/main.php)에 올라와있는 최근 플레이 데이터 games.xml을 이용, xml Parse를 활용하여 순차적으로 탐색하여 History를 만드는 코드 작성

# 모델 학습 순서
1. TRAIN_HUMAN_PLAY (1회 실시 후 더이상은 불필요)
2. TRAIN_CYCLE
3. EVALUATE (2-3 LOOP)
