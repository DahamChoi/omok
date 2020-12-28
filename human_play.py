# ====================
# 사람과 AI의 대전
# ====================

# 패키지 임포트
from omok import State
from pv_mcts import pv_mcts_action
from tensorflow.keras.models import load_model
from pathlib import Path
from threading import Thread
import tkinter as tk

# 흑돌 : False, 백돌 : True
FIRST_PLAY = False

# 베스트 플레이어 모델 로드
model = load_model('./model/best.h5')

# 게임 UI 정의
class GameUI(tk.Frame):
    # 초기화
    def __init__(self, master=None, model=None):
        tk.Frame.__init__(self, master)
        self.master.title('오목')

        # 게임 상태 생성
        self.state = State()

        # PV MCTS를 활용한 행동 선택을 따르는 함수 생성
        self.next_action = pv_mcts_action(model, 0.0)

        # 캔버스 생성
        self.c = tk.Canvas(self, width=600, height=600, highlightthickness=0)
        self.c.bind('<Button-1>', self.turn_of_human)
        self.c.pack()

        self.last_position = 999

        if FIRST_PLAY:
            # 그림 갱신
            self.on_draw()
        else:
            self.master.after(1, self.turn_of_ai)

    # 사람의 턴
    def turn_of_human(self, event):
        # 게임 종료 시
        if self.state.is_done():
            if FIRST_PLAY:
                self.state = State()
                self.on_draw()
            else:
                self.state = State()
                self.turn_of_ai()
                self.on_draw()
            return

        if FIRST_PLAY:
            # 선 수가 아닌 경우
            if not self.state.is_first_player():
                return
        else:
            if self.state.is_first_player():
                return

        # 클릭 위치를 행동으로 변환
        x = int(event.x / 40)
        y = int(event.y / 40)
        if x < 0 or 14 < x or y < 0 or 14 < y:  # 범위 외
            return
        action = x + y * 15

        # 합법적인 수가 아닌 경우
        if (action not in self.state.legal_actions()):
            return
 
        # 다음 상태 얻기
        self.state = self.state.next(action)
        self.on_draw()

        # AI의 턴
        self.master.after(1, self.turn_of_ai)

    # AI의 턴
    def turn_of_ai(self):
        # 게임 종료 시
        if self.state.is_done():
            return

        # 행동 얻기
        action = self.next_action(self.state)
        self.last_position = action

        # 다음 상태 얻기
        self.state = self.state.next(action)
        self.on_draw()

    # 돌 그리기
    def draw_piece(self, index, first_player):
        x = (index % 15) * 40 + 5
        y = int(index / 15) * 40 + 5

        if first_player:
            self.c.create_oval(x, y, x + 30, y + 30, width=2.0, outline='#FFFFFF')
        else:
            self.c.create_line(x, y, x + 30, y + 30, width=2.0, fill='#5D5D5D')
            self.c.create_line(x + 30, y, x, y + 30, width=2.0, fill='#5D5D5D')

    # 화면 갱신
    def on_draw(self):
        self.c.delete('all')
        self.c.create_rectangle(0, 0, 600, 600, width=0.0, fill='#00A0FF')
        
        for i in range(14):
            self.c.create_line((i + 1) * 40, 0, (i + 1) * 40, 600, width=2.0, fill='#0077BB')
            self.c.create_line(0, (i + 1) * 40, 600, (i + 1) * 40, width=2.0, fill='#0077BB')

        self.c.create_text(300,300,text="중앙")
        self.c.create_text(140,140,text="화점")
        self.c.create_text(460,140,text="화점")
        self.c.create_text(140,460,text="화점")
        self.c.create_text(460,460,text="화점")

        self.c.create_text((self.last_position % 15) * 40 + 20,(self.last_position / 15) * 40,text="마지막")

        for i in range(225):
            if self.state.pieces[i] == 1:
                self.draw_piece(i, self.state.is_first_player())
            if self.state.enemy_pieces[i] == 1:
                self.draw_piece(i, not self.state.is_first_player())


# 게임 UI 실행
f = GameUI(model=model)
f.pack()
f.mainloop()
