import random
import math

# 게임 상태
class State:
    # 초기화
    def __init__(self, pieces=None, enemy_pieces=None):
        # 돌 배치
        self.pieces = pieces if pieces != None else [0] * 225
        self.enemy_pieces = enemy_pieces if enemy_pieces != None else [0] * 225

    # 돌의 수 취득
    def piece_count(self, pieces):
        count = 0        
        for i in pieces:
            if i == 1:
                count +=  1
        return count

    # 패배 여부 확인
    def is_lose(self):
        # 돌 5개 연결 여부
        def is_comp(x, y, dx, dy):
            c = 0
            while True:
                if not(y >= 0 and y <= 14 and x >= 0 and x <= 14) or \
                    self.enemy_pieces[x+(y*15)] == 0:
                    break
                x, y = x+dx, y+dy
                c += 1
            return c

        for i in range(225):
            ix = i % 15
            iy = i // 15
            dist_list = [(1,0,-1,0),(0,1,0,-1),(1,1,-1,-1),(1,-1,-1,1)]
            for dx1,dy1,dx2,dy2 in dist_list:
                piece_count = is_comp(ix,iy,dx1,dy1) + is_comp(ix,iy,dx2,dy2) - 1
                if(self.is_first_player()):
                    if(piece_count >= 5):
                        return True
                else:
                    if(piece_count == 5):
                        return True
        return False

    # 무승부 여부 확인
    def is_draw(self):
        return self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces) == 225

    # 게임 종료 여부 확인
    def is_done(self):
        return self.is_lose() or self.is_draw()

    # 다음 상태 얻기
    def next(self, action):
        pieces = self.pieces.copy()
        pieces[action] = 1
        return State(self.enemy_pieces, pieces)

    def check_line_type(self,e_pieces,e_enemy_pieces,pos,dx,dy):
        pos_x = pos % 15
        pos_y = pos // 15

        empty_count = 0
        start_x = 0
        start_y = 0

        line_type = []

        if(e_pieces[pos] == 0 and e_enemy_pieces[pos] == 0):
            empty_count += 1

        # 시작점 잡기
        while True:
            pos_x = pos_x + dx
            pos_y = pos_y + dy
            dst_pos = pos_y * 15 + pos_x
            if(pos_x < 0 and pos_y < 0):
                start_x = 0
                start_y = 0
                break
            if(pos_x < 0):
                start_x = 0
                start_y = pos_y - dy
                break
            if(pos_y < 0):
                start_x = pos_x - dx
                start_y = 0
                break
            if(pos_x > 14 and pos_y > 14):
                start_x = 14
                start_y = 14
                break
            if(pos_x > 14):
                start_x = 14
                strat_y = pos_y - dy
                break
            if(pos_y > 14):
                start_x = pos_x - dx
                start_y = 14
                break

            if(e_pieces[dst_pos] == 0 and e_enemy_pieces[dst_pos] == 0):
                empty_count += 1
                if(empty_count >= 2):
                    start_x = pos_x - dx
                    start_y = pos_y - dy
                    break
            elif(e_enemy_pieces[dst_pos] == 1):
                start_x = pos_x - dx
                start_y = pos_y - dy
                break
            elif(e_pieces[dst_pos] == 1):
                empty_count = 0

        empty_count = 0
        dst_pos = start_y * 15 + start_x
        if(dst_pos < 0 or dst_pos >= 225):
            return line_type
        
        pos_x = dst_pos % 15
        pos_y = dst_pos // 15

        while True:
            if(e_pieces[dst_pos] == 0 and e_enemy_pieces[dst_pos] == 0):
                empty_count += 1
                if(empty_count >= 2):
                    break
                else:
                    line_type.append(0)
            elif(e_pieces[dst_pos] == 1):
                line_type.append(1)
                empty_count = 0
            elif(e_enemy_pieces[dst_pos] == 1):
                break

            pos_y = pos_y - dy
            pos_x = pos_x - dx
            dst_pos = pos_y * 15 + pos_x
            if(pos_x > 14 or pos_y > 14 or pos_x < 0 or pos_y < 0):
                break

        return line_type

    def check_line_type_three_three(self,line_type):
        three_three_line_type_1 = [0,1,1,1,0]
        three_three_line_type_2 = [0,1,0,1,1,0]
        three_three_line_type_3 = [0,1,1,0,1,0]

        if(line_type == three_three_line_type_1 or line_type == three_three_line_type_2 or line_type == three_three_line_type_3):
            return True
        else:
            return False

    def check_line_type_close_four(self,line_type):
        close_four_line_type_1 = [0,1,1,1,1]
        close_four_line_type_2 = [1,1,1,1,0]
        close_four_line_type_3 = [1,1,1,0,1]
        close_four_line_type_4 = [1,1,0,1,1]
        close_four_line_type_5 = [1,0,1,1,1]

        if(line_type == close_four_line_type_1 or line_type == close_four_line_type_2 or line_type == close_four_line_type_3 or\
            line_type == close_four_line_type_4 or line_type == close_four_line_type_5):
            return True
        else:
            return False

    def check_line_type_open_four(self,line_type):
        open_four_line_type_1 = [0,1,1,1,1,0]
        open_four_line_type_2 = [0,1,1,1,0,1,0]
        open_four_line_type_3 = [0,1,1,0,1,1,0]
        open_four_line_type_4 = [0,1,0,1,1,1,0]

        if(line_type == open_four_line_type_1 and line_type == open_four_line_type_2 or line_type == open_four_line_type_3 or\
            line_type == open_four_line_type_4):
            return True
        else:
            return False

    def check_line_count(self,x, y, dx, dy, pieces):
        c = 0
        while True:
            if not(y >= 0 and y <= 14 and x >= 0 and x <= 14) or \
                pieces[x+(y*15)] == 0:
                break
            x, y = x+dx, y+dy
            c += 1
        return c

    # 이길수있는 합법적인 수의 리스트 얻기
    def smart_legal_actions(self):
        actions = []

        default_legal_actions = self.legal_actions()

        dist_list = [(1,0,-1,0),(0,1,0,-1),(1,1,-1,-1),(1,-1,-1,1)]

        for i in range(225):
            if(i in default_legal_actions):
                # 5목을 만들 수 있는 상황이면 반드시 승리를 쟁취한다
                temp_pieces = self.pieces.copy()
                temp_pieces[i] = 1
                ix = i % 15
                iy = i // 15
                for dx1,dy1,dx2,dy2 in dist_list:
                    piece_count = self.check_line_count(ix,iy,dx1,dy1,temp_pieces) + self.check_line_count(ix,iy,dx2,dy2,temp_pieces) - 1
                    if(self.is_first_player()):
                        if(piece_count == 5):
                            actions.clear()
                            actions.append(i)
                            return actions
                    else:
                        if(piece_count >= 5):
                            actions.clear()
                            actions.append(i)
                            return actions
        
        for i in range(225):
            if(i in default_legal_actions):
                # case B-3 : 상대방이 i 액션을 했을때 5목을 만든다면 반드시 막는다
                temp_pieces = self.enemy_pieces.copy()
                temp_pieces[i] = 1
                ix = i % 15
                iy = i // 15
                for dx1,dy1,dx2,dy2 in dist_list:
                    piece_count = self.check_line_count(ix,iy,dx1,dy1,temp_pieces) + self.check_line_count(ix,iy,dx2,dy2,temp_pieces) - 1
                    if(not self.is_first_player()):
                        if(piece_count == 5):
                            actions.clear()
                            actions.append(i)
                            return actions
                    else:
                        if(piece_count >= 5):
                            actions.clear()
                            actions.append(i)
                            return actions

        for i in range(225):
            if(i in default_legal_actions):
                # case B-1-2 : 내가 열린4를 만들 수 있는 상황이라면 반드시 공격한다.
                temp_pieces = self.pieces.copy()
                temp_pieces[i] = 1

                win_open_four_type = [0,1,1,1,1,0]

                line_type_vertical = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,0)
                line_type_horizontal = self.check_line_type(temp_pieces,self.enemy_pieces,i,0,-1)
                line_type_digonal_1 = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,-1)
                line_type_digonal_2 = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,1)

                if((line_type_vertical == win_open_four_type) or (line_type_horizontal == win_open_four_type) or\
                    (line_type_digonal_1 == win_open_four_type) or (line_type_digonal_2 == win_open_four_type)):
                    actions.clear()
                    actions.append(i)
                    return actions

                # case B-1-4 : 내가 4-3을 만들 수 있다면 반드시 공격한다.
                if((self.check_line_type_close_four(line_type_vertical) or self.check_line_type_close_four(line_type_horizontal) or\
                    self.check_line_type_close_four(line_type_digonal_1) or self.check_line_type_close_four(line_type_digonal_2) or\
                    self.check_line_type_open_four(line_type_vertical) or self.check_line_type_open_four(line_type_horizontal) or\
                    self.check_line_type_open_four(line_type_digonal_1) or self.check_line_type_open_four(line_type_digonal_2)) and\
                    (self.check_line_type_three_three(line_type_vertical) or self.check_line_type_three_three(line_type_horizontal) or\
                    self.check_line_type_three_three(line_type_digonal_1) or self.check_line_type_three_three(line_type_digonal_2))):
                    actions.clear()
                    actions.append(i)
                    return actions

        isHaveOpenThree = False

        for i in range(225):
            if(i in default_legal_actions):
                # case B-1 : 열린3은 막는다
                line_type_vertical = self.check_line_type(self.enemy_pieces,self.pieces,i,-1,0)
                line_type_horizontal = self.check_line_type(self.enemy_pieces,self.pieces,i,0,-1)
                line_type_digonal_1 = self.check_line_type(self.enemy_pieces,self.pieces,i,-1,-1)
                line_type_digonal_2 = self.check_line_type(self.enemy_pieces,self.pieces,i,-1,1)

                if(self.check_line_type_three_three(line_type_vertical) or self.check_line_type_three_three(line_type_horizontal) or\
                    self.check_line_type_three_three(line_type_digonal_1) or self.check_line_type_three_three(line_type_digonal_2)):
                    actions.append(i)
                    isHaveOpenThree = True

                temp_pieces = self.enemy_pieces.copy()
                temp_pieces[i] = 1

                line_type_vertical = self.check_line_type(temp_pieces,self.pieces,i,-1,0)
                line_type_horizontal = self.check_line_type(temp_pieces,self.pieces,i,0,-1)
                line_type_digonal_1 = self.check_line_type(temp_pieces,self.pieces,i,-1,-1)
                line_type_digonal_2 = self.check_line_type(temp_pieces,self.pieces,i,-1,1)

                count = 0
                if(self.check_line_type_three_three(line_type_vertical)):
                    count += 1
                if(self.check_line_type_three_three(line_type_horizontal)):
                    count += 1
                if(self.check_line_type_three_three(line_type_digonal_1)):
                    count += 1
                if(self.check_line_type_three_three(line_type_digonal_2)):
                    count += 1

                # case B-2 : 내가 선공일때 상대방이 i 지점에 쌍삼을 만들 수 있다면 막는다.
                if(self.is_first_player()):
                    if(count >= 2):
                        actions.append(i)
                        isHaveOpenThree = True
                
                # case A : 상대방이 i 지점에 4:3을 만들 수 있다면 막는다.
                if((self.check_line_type_close_four(line_type_vertical) or self.check_line_type_close_four(line_type_horizontal) or\
                    self.check_line_type_close_four(line_type_digonal_1) or self.check_line_type_close_four(line_type_digonal_2) or\
                        self.check_line_type_open_four(line_type_vertical) or self.check_line_type_open_four(line_type_horizontal) or\
                            self.check_line_type_open_four(line_type_digonal_1) or self.check_line_type_open_four(line_type_digonal_2)) and\
                        count >= 1):
                    actions.append(i)
                    isHaveOpenThree = True

        for i in range(225):
            if((i in default_legal_actions) and isHaveOpenThree):
                # case B-3 : 내가 닫힌4를 만들 수 있는 상황이라면 상대방이 열린3or쌍삼이여도 공격할 수 있다.
                temp_pieces = self.pieces.copy()
                temp_pieces[i] = 1
                line_type_vertical = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,0)
                line_type_horizontal = self.check_line_type(temp_pieces,self.enemy_pieces,i,0,-1)
                line_type_digonal_1 = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,-1)
                line_type_digonal_2 = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,1)

                if(self.check_line_type_close_four(line_type_vertical) or self.check_line_type_close_four(line_type_horizontal) or\
                    self.check_line_type_close_four(line_type_digonal_1) or self.check_line_type_close_four(line_type_digonal_2)):
                    actions.append(i)        

        for i in range(225):
            if(i in default_legal_actions and len(actions) == 0):
                # case B-1-3 : 내가 후공일때 쌍삼을 만들 수 있다면 반드시 공격한다.
                if(not self.is_first_player()):
                    temp_pieces = self.pieces.copy()
                    temp_pieces[i] = 1

                    line_type_vertical = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,0)
                    line_type_horizontal = self.check_line_type(temp_pieces,self.enemy_pieces,i,0,-1)
                    line_type_digonal_1 = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,-1)
                    line_type_digonal_2 = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,1)

                    count = 0
                    if(self.check_line_type_three_three(line_type_vertical)):
                        count += 1
                    if(self.check_line_type_three_three(line_type_horizontal)):
                        count += 1
                    if(self.check_line_type_three_three(line_type_digonal_1)):
                        count += 1
                    if(self.check_line_type_three_three(line_type_digonal_2)):
                        count += 1

                    if(count >= 2):
                        actions.append(i)

        if len(actions) == 0:
            return default_legal_actions

        return actions

    # 합법적인 수의 리스트 얻기
    def legal_actions(self):

        actions = []
        for i in range(225):
            if self.is_first_player():
                if(self.pieces[i] == 0 and self.enemy_pieces[i] == 0):
                    temp_pieces = self.pieces.copy()
                    temp_pieces[i] = 1
                    
                    line_type_vertical = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,0)
                    line_type_horizontal = self.check_line_type(temp_pieces,self.enemy_pieces,i,0,-1)
                    line_type_digonal_1 = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,-1)
                    line_type_digonal_2 = self.check_line_type(temp_pieces,self.enemy_pieces,i,-1,1)

                    count_three_three = 0
                    if(self.check_line_type_three_three(line_type_vertical)):
                        count_three_three += 1
                    if(self.check_line_type_three_three(line_type_horizontal)):
                        count_three_three += 1
                    if(self.check_line_type_three_three(line_type_digonal_1)):
                        count_three_three += 1
                    if(self.check_line_type_three_three(line_type_digonal_2)):
                        count_three_three += 1

                    count_four_four = 0
                    if(self.check_line_type_close_four(line_type_vertical) or self.check_line_type_open_four(line_type_vertical)):
                        count_four_four += 1
                    if(self.check_line_type_close_four(line_type_horizontal) or self.check_line_type_open_four(line_type_horizontal)):
                        count_four_four += 1
                    if(self.check_line_type_close_four(line_type_digonal_1) or self.check_line_type_open_four(line_type_digonal_1)):
                        count_four_four += 1
                    if(self.check_line_type_close_four(line_type_digonal_2) or self.check_line_type_open_four(line_type_digonal_2)):
                        count_four_four += 1

                    if count_three_three < 2 and count_four_four < 2:
                        actions.append(i)
            else:
                if self.pieces[i] == 0 and self.enemy_pieces[i] == 0:
                    actions.append(i)
        return actions

    # 선 수 여부 확인
    def is_first_player(self):
        return self.piece_count(self.pieces) == self.piece_count(self.enemy_pieces)

    # 문자열 표시
    def __str__(self):
        ox = ('o', 'x') if self.is_first_player() else ('x', 'o')
        str = ''
        for i in range(225):
            if self.pieces[i] == 1:
                str += ox[0] + ' '
            elif self.enemy_pieces[i] == 1:
                str += ox[1] + ' '
            else:
                str += '- '
            if i % 15 == 14:
                str += '\n'
        return str

# 랜덤으로 행동 선택
def random_action(state):
    legal_actions = state.smart_legal_actions()
    return legal_actions[random.randint(0, len(legal_actions)-1)]

# 테스트
if __name__ == '__main__':
    state = State()
    while True:
        if state.is_done():
            break

        state = state.next(random_action(state))

        print(state)
        print()