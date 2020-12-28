from omok import State
from pv_mcts import pv_mcts_scores
from dual_network import DN_OUTPUT_SIZE
from datetime import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from pathlib import Path
import numpy as np
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, dump, ElementTree
import pickle
import os

human_play_database = []
winner_play_database = []

def human_play_data_xml_parse():
    xml_file = 'games.xml'
    doc = ET.parse(xml_file)
    root = doc.getroot()

    for board in root.iter('board'):
        human_play_database.append(board.text)

    index = 0
    for winner in root.iter('winner'):
        if(winner.text == 'black'):
            winner_play_database.append(1)
        elif(winner.text == 'white'):
            winner_play_database.append(-1)
        else:
            winner_play_database.append(0)
        index += 1

class HumanPlay:

    def __init__(self,index):
        if(len(human_play_database) <= index):
            return None
        
        self.humanplay_str = human_play_database[index]
        self.humanplay_str = self.humanplay_str.split(' ')
        self.depth = 0

    def pv_human_action(self):
        if(len(self.humanplay_str) <= self.depth):
            return None
        else:
            action_str = self.humanplay_str[self.depth]
            px = self.get_vertical_index_by_alpha(action_str[0])
            try:
                py = 15 - int(action_str[1:])
            except ValueError:
                return None

            action = (py * 15) + px
            self.depth += 1

            return action

    def get_vertical_index_by_alpha(self,alpha):
        vertical_index_array = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o']
        index = 0
        for i in vertical_index_array:
            if(i == alpha):
                return index
                break
            index += 1
        return None

def write_data(history):
    now = datetime.now()
    os.makedirs('./data/',exist_ok=True)
    path = './data/{:04}{:02}{:02}{:02}{:02}{:02}.history'.format(
        now.year,now.month,now.day,now.hour,now.minute,now.second
    )
    with open(path,mode='wb') as f:
        pickle.dump(history, f)

# 게임 실행
def play(human,index):
    # 학습 데이터
    history = []

    # 상태 생성
    state = State()

    while True:
        # 게임 종료 시
        if state.is_done():
            break

        # 둘 수 있는 수의 확률 분포 얻기
        action = human.pv_human_action()
        if(action == None):
            break

        # 학습 데이터에 상태와 정책 추가
        policies = [0] * DN_OUTPUT_SIZE
        policies[action] = 1
        history.append([[state.pieces, state.enemy_pieces], policies, None])

        # 다음 상태 얻기
        state = state.next(action)

    # 학습 데이터에 가치 추가
    value = winner_play_database[index]
    
    for i in range(len(history)):
        history[i][2] = value
        value = -value

    return history

def self_play(start_index):
    history = []
    human_play_data_xml_parse()

    index = start_index

    while True:
        human = HumanPlay(index)
        if(human == None or index-1 >= (start_index + 5000)):
            break
        
        h = play(human,index)
        if(h != None):
            history.extend(h)

        index += 1

        print('\HumanPlay {}/{}'.format(index + 1, len(human_play_database), end=''))
    print('')

    write_data(history)

if __name__ == '__main__':
    self_play(10000)