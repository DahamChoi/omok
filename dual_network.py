from tensorflow.keras.layers import Activation, Add, BatchNormalization, Conv2D, Dense, GlobalAveragePooling2D, Input
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
from tensorflow.keras import backend as K
import os

## 알파제로의 강화 학습 사이클
## 강화학습시작 -> 듀얼 네트워크 생성 -> 셀프 플레이 파트 -> 파라미터 갱신 파트 -> 신규 파라미터 평가 파트 -> 강화학습 완료
##                       └─────────────────────────── (CYCLE) ──────────────────────────┘

## 강화 학습 요소
## 목적     : 승리
## 에피소드 : 게임 종료 국면까지
## 상태     : 국면
## 행동     : 수를 던짐
## 보상     : 승리시 + 1 패배시 - 1
## 학습 방법: 몬테카틀로 트리 탐색 + ResNet + 셀프 플레이
## 파리미터 갱신 간격 : 매 에피소드마다

## 기본 용어
## 컨볼루셔널 레이어 : 보드맵을 압축시켜서 특징을 만드는 레이어
## ResNet : 숏컷 컨넥션이라 불리는 우회 경로를 추가시킨다. 이를 통해 컨볼루셔널 레이어에서 학습이 필요하지 않는 경우에는 우회시킨다.
## 플레인 아키텍쳐 : 동일 매수의 커널을 가진 컨볼루셔널 레이어를 나란히 2개 사용한 것
## 보틀렉 아키텍쳐 : 플레인 아키텍쳐에 4배의 크기를 가진 컨볼루셔널 레이어의 차원을 복원하기 위한 레이어

## 듀얼 네트워크 정책, 가치의 2개의 값을 출력해 낸다.
## ex틱택톡) 정책 : 다음 한 수의 확률 분포, 가치 : 현재 국면에서의 승리 예측

DN_FILTERS = 128            # 컨볼루셔널 레이어 커널 수 (오리지널 256)
DN_RESIDUAL_NUM = 16        # 레지듀얼 블록 수 (오리지널 19)
DN_INPUT_SHAPE = (15,15,2)    # 입력 형태
DN_OUTPUT_SIZE = 225          # 행동 수 (배치수 15x15)

## Conv2D(커널의 수, 커널 사이즈, 패딩, 바이오스 추가여부, 커널 가중치 행렬 초기화, 정규화)
def conv(filters):
    return Conv2D(filters, 3, padding='same', use_bias=False,
                    kernel_initializer='he_normal', kernel_regularizer=l2(0.0005))

## 레지듀얼 블록 생성
## 컨볼루셔널 레이어(3x3 커널 128매) -> BatchNormalization -> RELU
## 컨볼루셔널 레이어(3x3 커널 128매) -> BatchNormalization -> Add -> RELU
def residual_block():
    def f(x):
        sc = x
        x = conv(DN_FILTERS)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        x = Add()([x,sc])
        x = Activation('relu')(x)
        return x
    return f

## 듀얼네트워크 생성
def dual_network():
    ## 모델 생성이 완료된 경우 처리하지 않음
    if os.path.exists('./model/best.h5'):
        return
    
    ## 입력레이어
    input = Input(shape=DN_INPUT_SHAPE)

    ## 컨볼루셔널 레이어
    x = conv(DN_FILTERS)(input)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    ## 레지듀얼 블록 x 16
    for i in range(DN_RESIDUAL_NUM):
        x = residual_block()(x)

    ## 풀링 레이어
    x = GlobalAveragePooling2D()(x)

    ## 정책 출력
    p = Dense(DN_OUTPUT_SIZE, kernel_regularizer=l2(0.0005),
                activation='softmax',name='pi')(x)

    ## 가치 출력 
    v = Dense(1, kernel_regularizer=l2(0.005))(x)

    ## 모델 생성
    model = Model(inputs=input,outputs=[p,v])

    ## 모델 저장
    os.makedirs('./model/', exist_ok=True)
    model.save('./model/best.h5')           ## 베스트 플레이어 모델

    ## 모델 삭제
    K.clear_session()
    del model

if __name__ == '__main__':
    dual_network()