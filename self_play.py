from omok import State
from pv_mcts import pv_mcts_scores
from dual_network import DN_OUTPUT_SIZE
from datetime import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from pathlib import Path
import numpy as np
import pickle
import os

SP_GAME_COUNT = 1000      # 셀프 플레이를 수행할 게임 수 (오리지널 : 25,000)
SP_TEMPERATURE = 1.0    # 볼츠만 분포의 온도 파라미터

def first_player_value(ended_state):
    if ended_state.is_lose():
        return -1 if ended_state.is_first_player() else 1
    return 0

def write_data(history):
    now = datetime.now()
    os.makedirs('./data/',exist_ok=True)
    path = './data/{:04}{:02}{:02}{:02}{:02}{:02}.history'.format(
        now.year,now.month,now.day,now.hour,now.minute,now.second
    )
    with open(path,mode='wb') as f:
        pickle.dump(history, f)

# 게임 실행
def play(model):
    # 학습 데이터
    history = []

    # 상태 생성
    state = State()
    state.next(128)

    while True:
        # 게임 종료 시
        if state.is_done():
            break

        # 둘 수 있는 수의 확률 분포 얻기
        scores = pv_mcts_scores(model,state,SP_TEMPERATURE)

        # 학습 데이터에 상태와 정책 추가
        policies = [0] * DN_OUTPUT_SIZE
        for action, policy in zip(state.smart_legal_actions(), scores):
            policies[action] = policy
        history.append([[state.pieces, state.enemy_pieces], policies, None])

        # 행동 얻기
        action = np.random.choice(state.smart_legal_actions(), p = scores)

        # 다음 상태 얻기
        state = state.next(action)

    # 학습 데이터에 가치 추가
    value = first_player_value(state)
    for i in range(len(history)):
        history[i][2] = value
        value = -value
    return history

def self_play():
    history = []

    model = load_model('./model/best.h5')

    for i in range(SP_GAME_COUNT):
        h = play(model)
        history.extend(h)

        print('\rSelfPlay {}/{}'.format(i + 1, SP_GAME_COUNT, end=''))
    print('')

    write_data(history)

    K.clear_session()
    del model

if __name__ == '__main__':
    self_play()