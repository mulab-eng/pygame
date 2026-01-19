import pygame
import sys
import math
import random
import os

############################### ウィンドウの大きさ　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
WIDTH=800
HEIGHT=600

########################### 画像ファイルを読み込む
img_weapon = pygame.image.load("bullet.png")
img_weapon2 = pygame.image.load("bullet2.png")
img_robot = pygame.image.load("robot.png")
img_enemy = pygame.image.load("enemy.png")
img_bakuhatsu= pygame.image.load("bakuhatsu.png")
img_bakuhatsu2= pygame.image.load("bakuhatsu2.png")
img_wall = pygame.image.load("wall.png")
img_haikei=pygame.image.load("haikei.png")
img_start=pygame.image.load("start.png")
img_gameover=pygame.image.load("gameover.png")
img_high=pygame.image.load("high.png")

se_shot=None # 音声ファイル用変数
se_hit=None

############################### スコア
score=100

count=0
ta=0

written=0
switch=0

scorefile=open('score01.txt','r')
zenkaiscore_str = scorefile.read()
if len(zenkaiscore_str) < 1:
    zenkaiscore_str='-100'
zenkaiscore = int(zenkaiscore_str)
scorefile.close()

scorefile=open('score01.txt','w')

############################### 敵の弾の変数
e_msl_f=False
e_msl_x=300       # 弾のx座標
e_msl_y=300       # 弾のy座標
e_msl_theta=0   # 弾の角度

################################ 敵の変数
emy_x=200
emy_y=200
emy_vx=-40
emy_vy=-30
emy_theta=(5/4)*math.pi
emy_v=0
emy_omega=0.0

############################## ロボットの変数
xr=-200  # ロボットのx座標
yr=-210   # ロボットの y座標
vx= 40  # x方向の速度（初期値）
vy= 30  # y方向の速度
theta=0 # ロボットの角度の初期値[rad]
v=10   #[m/sec]  # 前進方向の速度
omega=-0.5 #[rad/sec]  # 回転の角速度

################################### 画面の更新
deltaT=1/30  # 画面更新の刻み時間 Δt
timer=0  # 時間を測る変数

# ゲームの開始，プレイ中，ゲームオーバーを管理する変数
idx=0  
########## ジョイスティック（ゲームパッド）の有無
Joys=0  #初期値は無し

######## 複数の弾を発射できるようにする ########
MISSILE_MAX = 100
msl_no = 0
msl_f = [False]*MISSILE_MAX
msl_x = [0]*MISSILE_MAX
msl_y = [0]*MISSILE_MAX
msl_theta=[0]*MISSILE_MAX  # 弾の角度
key_spc = 0
joy_b = 0

##################  壁の変数
w_xr=2*WIDTH #壁のx座標
w_yr=2*HEIGHT #壁のy座標
w_v=400 #壁の速さ
w_theta=0 #壁の角度
w_f=0 #壁のフラグ
w_size=0.25 #壁の縮尺
w_hp=2000 #壁の耐久値

##############################################   画像表示   ########################################################## 
def disp_str(screen, img, x, y, th, k):  # 画像を位置(x,y)，角度thで表示する関数．
                                        #  imgはファイル名，kは拡大縮小の倍率
    X= WIDTH*0.5 + x   # 座標変換
    Y= HEIGHT*0.5 - y # 座標変換
    th=th*180/math.pi # 座標変換
    TH=th # 座標変換
    img1 = pygame.transform.rotozoom(img, TH, k)  # 画像の回転と拡大縮小
    X = X - img1.get_width()/2    # 位置の微調整
    Y = Y - img1.get_height()/2   # 位置の微調整
    screen.blit(img1, [X, Y])     # 画像の表示
##############################################   画像表示   ########################################################## 
def disp_img(screen, img, x, y, th, k):  # 画像を位置(x,y)，角度thで表示する関数．
                                        #  imgはファイル名，kは拡大縮小の倍率
    X= WIDTH*0.5 + x   # 座標変換
    Y= HEIGHT*0.5 - y # 座標変換
    th=th*180/math.pi # 座標変換
    TH=th-90 # 座標変換
    img1 = pygame.transform.rotozoom(img, TH, k)  # 画像の回転と拡大縮小
    X = X - img1.get_width()/2    # 位置の微調整
    Y = Y - img1.get_height()/2   # 位置の微調整
    screen.blit(img1, [X, Y])     # 画像の表示

##############################################   弾   ########################################################## 
def set_missile(): # 弾の初期設定
    global xr, yr, vx, vy, theta, v, omega, deltaT, msl_no
    global msl_f, msl_x, msl_y, msl_theta
    if msl_f[msl_no] == False:  # 弾が存在しなければ
        msl_f[msl_no]= True     # 弾を存在させて
        msl_x[msl_no] = xr+20*math.cos(theta) # 弾の発射位置のx座標を計算（ロボットの近く）
        msl_y[msl_no] = yr+20*math.sin(theta) # 弾の発射位置のy座標を計算（ロボットの近く）
        msl_theta[msl_no]=theta  # 発射するときの弾の角度をロボットの角度と同じに設定
        msl_no = (msl_no+1)%MISSILE_MAX

def e_set_missile(): # 敵の弾の初期設定
    global emy_x, emy_y, emy_vx, emy_vy, emy_theta, emy_v, emy_omega, deltaT 
    global e_msl_f, e_msl_x, e_msl_y, e_msl_theta
    if e_msl_f == False:  # 敵の弾が存在しなければ
        e_msl_f= True     # 敵の弾を存在させて
        e_msl_x = emy_x+20*math.cos(emy_theta) # 敵の弾の発射位置のx座標を計算（ロボットの近く）
        e_msl_y = emy_y+20*math.sin(emy_theta) # 敵の弾の発射位置のy座標を計算（ロボットの近く）
        e_msl_theta=emy_theta  # 発射するときの敵の弾の角度を敵の角度と同じに設定

def move_missile(screen):  # 弾を動かす関数
    global xr, yr, vx, vy, theta, v, omega, deltaT 
    global msl_f, msl_x, msl_y, msl_theta
    for i in range(MISSILE_MAX):
        if msl_f[i] == True:
            msl_x[i] = msl_x[i]  + 15*math.cos(msl_theta[i]) # 弾のx座標を更新
            msl_y[i] = msl_y[i]  + 15*math.sin(msl_theta[i]) # 弾のy座標を更新
            if math.fabs(msl_x[i]) > WIDTH*0.5: # 弾のx座標の絶対値がウィンドウの半分を超えたら
                msl_f[i]=False # 弾はウィンドウから出るので存在しない（False）とする
            if math.fabs(msl_y[i]) > HEIGHT*0.5: # 弾のy座標の絶対値がウィンドウの半分を超えたら
                msl_f[i]=False # 弾はウィンドウから出るので存在しない（False）とする
            disp_img(screen, img_weapon, msl_x[i], msl_y[i], msl_theta[i], 0.05) # 弾の画像を位置と角度を指定して表示

def e_move_missile(screen):  # 敵の弾を動かす関数
    global emy_x, emy_y, emy_vx, emy_vy, emy_theta, emy_v, emy_omega, deltaT 
    global e_msl_f, e_msl_x, e_msl_y, e_msl_theta
    if e_msl_f == True:
        e_msl_x = e_msl_x  + 15*math.cos(e_msl_theta) # 弾のx座標を更新
        e_msl_y = e_msl_y  + 15*math.sin(e_msl_theta) # 弾のy座標を更新
        if math.fabs(e_msl_x) > WIDTH*0.5: # 弾のx座標の絶対値がウィンドウの半分を超えたら
            e_msl_f=False # 弾はウィンドウから出るので存在しない（False）とする
        if math.fabs(e_msl_y) > HEIGHT*0.5: # 弾のy座標の絶対値がウィンドウの半分を超えたら
            e_msl_f=False # 弾はウィンドウから出るので存在しない（False）とする
        disp_img(screen, img_weapon2, e_msl_x, e_msl_y, e_msl_theta, 0.15) # 弾の画像を位置と角度を指定して表示


##############################################   ロボット   ########################################################## 
def move_robot(screen):  # ロボットを動かす関数
    global xr, yr, vx, vy, theta, v, omega, deltaT, score, count
    vx=v*math.cos(theta)   # ロボットのx方向の速度
    vy=v*math.sin(theta)   # ロボットのy方向の速度
    thetadot=omega         # ロボットの角速度
    xr = xr + vx * deltaT   # ロボットのx座標を更新
    yoyu=30
    if xr > WIDTH*0.5-yoyu:
        xr= WIDTH*0.5-yoyu
    if xr < -WIDTH*0.5+yoyu:
        xr= -WIDTH*0.5+yoyu
    yr = yr + vy * deltaT   # ロボットのy座標を更新
    if yr > HEIGHT*0.5-yoyu:
        yr= HEIGHT*0.5-yoyu
    if yr < -HEIGHT*0.5+yoyu:
        yr= -HEIGHT*0.5+yoyu
    theta = theta + thetadot * deltaT  # ロボットの角度を更新
    disp_img(screen, img_robot, xr, yr, theta, 0.3) # ロボットの画像を位置と角度を指定して表示
    kyori2=(xr-e_msl_x)*(xr-e_msl_x)+(yr-e_msl_y)*(yr-e_msl_y)
    kyori=math.sqrt(kyori2)
    if kyori < 40:
        #敵の上に画像を表示
        disp_img(screen, img_bakuhatsu, xr, yr, theta, 0.25)
        score = score-1
        count = count +1
        
##############################################  敵 ########################################################## 
def move_enemy(screen):  # 敵を動かす関数
    global emy_x, emy_y, emy_vx, emy_vy, emy_theta, emy_v, emy_omega, deltaT, score, count
    emy_vx=emy_v*math.cos(emy_theta)   # 敵のx方向の速度
    emy_vy=emy_v*math.sin(emy_theta)   # 敵のy方向の速度
    # emy_thetadot=emy_omega         # 敵の角速度
    emy_x = emy_x + emy_vx * deltaT   # 敵のx座標を更新
    emy_y = emy_y + emy_vy * deltaT   # 敵のy座標を更新
    # emy_theta = emy_theta + emy_thetadot * deltaT  # 敵の角度を更新
    
    e_kyori2=(xr-emy_x)*(xr-emy_x)+(yr-emy_y)*(yr-emy_y)
    e_kyori=math.sqrt(e_kyori2)
    if e_kyori > 270:
        move = ["front","stop"]
        choice = random.choice(move)
        if timer%15==0:
            if choice=="front":
                emy_v=30
            if choice=="stop":
                emy_v=0
    if e_kyori < 270:
        emy_v=-40

    ahead_t= 2.2 # 予測時間(秒) 好みに応じて調整
    next_xr = xr + vx * ahead_t
    next_yr = yr + vy * ahead_t
    dx = next_xr - emy_x
    dy = next_yr - emy_y

    if emy_theta > 2*math.pi:
        emy_theta = emy_theta - 2*math.pi
    if emy_theta < 0:
        emy_theta = emy_theta + 2*math.pi
    r_thetarad=math.atan2(dy,dx)  # 敵からロボットへ引いたベクトルのラジアンの角度
    if r_thetarad < 0:
        r_thetarad = r_thetarad + 2*math.pi

    e=(emy_theta-r_thetarad+math.pi)%(2*math.pi)-math.pi
    gain=-1.0
    emy_thetadot=gain*e
    emy_theta = emy_theta + emy_thetadot * deltaT

    disp_img(screen, img_enemy, emy_x, emy_y, emy_theta, 0.15) # 敵の画像を位置と角度を指定して表示

    if emy_x > WIDTH*0.5:
        emy_x = WIDTH*0.5
    if emy_x < -WIDTH*0.5:
        emy_x = -WIDTH*0.5
    if emy_y > HEIGHT*0.5:
        emy_y = HEIGHT*0.5
    if emy_y < -HEIGHT*0.5:
        emy_y = -HEIGHT*0.5    

    for i in range(MISSILE_MAX):
        if msl_f[i] == True:
            kyori2=(emy_x-msl_x[i])*(emy_x-msl_x[i])+(emy_y-msl_y[i])*(emy_y-msl_y[i])
            kyori=math.sqrt(kyori2)
            if kyori < 40:
                count = count +1
                se_hit.play()
                #敵の上に画像を表示
                disp_img(screen, img_bakuhatsu2, emy_x, emy_y, emy_theta, 0.2)
                msl_f[i]=False
                kyori3 = (emy_x-xr)*(emy_x-xr)+(emy_y-yr)*(emy_y-yr) 
                kyori4 = math.sqrt(kyori3) 
                iscore=score + 1 
                if kyori4 > 100: 
                 score = score + 1 
                if kyori4 > 200: 
                 score = score + 1 
                if kyori4 > 400: 
                    score = score + 2
                if kyori4 > 500: 
                    score = score + 3
                if kyori4 >700: 
                    score = score + 5
                if kyori4 > 800: 
                    score = score + 500 

##############################################   壁   ########################################################## 
def move_wall(screen,timer): #壁を動かす関数
    global w_xr,w_yr,w_v,w_theta,w_hp,deltaT,w_f,w_size
    global emy_x, emy_y, xr, yr, score
    global e_msl_f,e_msl_x,e_msl_y
    if w_hp>0: #壁の耐久値がある状態で実行
        x_kyori=math.fabs(emy_x-xr) #ロボットと敵のx方向距離
        y_kyori=math.fabs(emy_y-yr) #ロボットと敵のy方向距離
        if x_kyori<200 and y_kyori<200: #両方向の距離が100未満で実行
            
            if x_kyori<y_kyori:
                if w_f==0:
                    w_v=400
                    w_xr=xr
                    w_theta=0
                    if yr>0:
                        w_yr=HEIGHT*0.5
                        w_f=1 
                    else:
                        w_yr=-HEIGHT*0.5
                        w_f=2 
    
            if x_kyori>y_kyori:
                if w_f==0:
                    w_v=400
                    w_yr=yr
                    w_theta=math.pi*0.5
                    if xr>0:
                        w_xr=WIDTH*0.5
                        w_f=3 
                    else:
                        w_xr=-WIDTH*0.5
                        w_f=4 
            
        sec = timer*deltaT #timerの時間を秒に直す
        interval=20 #壁が降ってくる間隔
        if sec%interval==0 and w_f==0:
            w_v=100
            if math.fabs(xr)<math.fabs(yr):
                w_xr=xr
                w_theta=0
                if yr>0:
                    w_yr=HEIGHT*0.5
                    w_f=1 
                else:
                    w_yr=-HEIGHT*0.5
                    w_f=2 
            if math.fabs(xr)>=math.fabs(yr):
                w_yr=yr
                w_theta=math.pi*0.5
                if xr>0:
                    w_xr=WIDTH*0.5
                    w_f=3 
                else:
                    w_xr=-WIDTH*0.5
                    w_f=4 

            

        if w_f==1: #画面の上端から壁が出てくる
                disp_img(screen, img_wall, w_xr, w_yr, w_theta, w_size)
                w_yr-=w_v*deltaT
        if w_f==2: #画面の下端から壁が出てくる 
                disp_img(screen, img_wall, w_xr, w_yr, w_theta, w_size)
                w_yr+=w_v*deltaT
        if w_f==3: #画面の右端から壁が出てくる 
                disp_img(screen, img_wall, w_xr, w_yr, w_theta, w_size)
                w_xr-=w_v*deltaT
        if w_f==4: #画面の左端から壁が出てくる
                disp_img(screen, img_wall, w_xr, w_yr, w_theta, w_size)
                w_xr+=w_v*deltaT


        if math.fabs(w_xr)>WIDTH*0.5 or math.fabs(w_yr)>HEIGHT*0.5:
            w_f=0 #壁が画面外に出た場合
            w_xr=2*WIDTH #x座標初期値
            w_yr=2*HEIGHT #y座標初期値


        for i in range(MISSILE_MAX):
            if msl_f[i] == True:
                kyori_r=(w_xr-msl_x[i])*(w_xr-msl_x[i])+(w_yr-msl_y[i])*(w_yr-msl_y[i])
                kyori_r=math.sqrt(kyori_r)
                if kyori_r < 100:
                    #壁の上に画像を表示
                    msl_f[i]=False
                    disp_img(screen, img_bakuhatsu, w_xr, w_yr, w_theta, 0.25)
                    w_hp-=1

        kyori_e=(e_msl_x-w_xr)*(e_msl_x-w_xr)+(e_msl_y-w_yr)*(e_msl_y-w_yr)
        kyori_e=math.sqrt(kyori_e)
        if kyori_e < 100:
                    #壁の上に画像を表示
                    e_msl_f=False
                    disp_img(screen, img_bakuhatsu, w_xr, w_yr, w_theta, 0.25)
                    w_hp-=1

def contact_wall(): #壁とロボットの接触
    global xr,yr,w_xr,w_yr, w_hp,w_size,w_theta,v,omega,w_f 
    w_width=img_wall.get_width()/2*w_size
    w_height=img_wall.get_height()/2*w_size
    if w_theta==0:
        w_height=img_wall.get_width()/2*w_size
        w_width=img_wall.get_height()/2*w_size

    xkyori=xr-w_xr
    ykyori=yr-w_yr
    
    if w_hp>0:
        if w_f==4 and 0<xkyori<=w_width and -w_height<=ykyori<=w_height: #画面の左端から出てきた壁の右面に接触
            xr=w_xr+w_width
        if w_f==3 and -w_width<=xkyori<0 and -w_height<=ykyori<=w_height: #画面の右端から出てきた壁の左面に接触
            xr=w_xr-w_width
        if w_f==2 and -w_width<=xkyori<=w_width and 0<ykyori<=w_height: #画面の下端から出てきた壁の上面に接触
            yr=w_yr+w_height
        if w_f==1 and -w_width<=xkyori<=w_width and -w_height<=ykyori<0: #画面の上端から出てきた壁の下面に接触
            yr=w_yr-w_height

##############################################   メイン  ########################################################## 
def main():
    global xr, yr, vx, vy, theta, v, omega, deltaT, timer, idx, key_spc, joy_b, count, ta, bgm, scorefile, score
    global se_shot, se_hit, written, zenkaiscore, switch
    pygame.init()
    pygame.joystick.init()
    pygame.display.set_caption("シューティングゲーム")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # ウィンドウのサイズ
    clock = pygame.time.Clock()  # 画面更新のためにクロックをつくっておく
    se_shot=pygame.mixer.Sound('shot.wav')
    se_hit=pygame.mixer.Sound('hit.wav')
    font = pygame.font.Font(None, 50) # 文字のフォントと大きさ
    font2 = pygame.font.Font(None, 140) # 文字のフォントと大きさ
    font3 = pygame.font.Font(None, 190) # 文字のフォントと大きさ
    pygame.mixer.music.load('bgm.wav')
    time_limit=40 #制限時間

    while True:
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  # ×が押されたら終了する
                pygame.quit()
                sys.exit()
        screen.fill((55, 55, 240))   # ウィンドウの内部に色を塗る
        try:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            joy_lr = joystick.get_axis(0)
            joy_ud = joystick.get_axis(1)
            joyL_lr = joystick.get_axis(2)
            joyL_ud = joystick.get_axis(3)
            jbtn1 = joystick.get_button(0)+joystick.get_button(1)+joystick.get_button(2)+joystick.get_button(3)
            jbtn2 = joystick.get_button(2) # Xボタン
            jbtn3 = joystick.get_button(4) # LB
            jbtn4 = joystick.get_button(5) # RB
            jbtn5 = joystick.get_button(7) # START
            jbtn6 = joystick.get_button(6)  # BACK
            jbtn7 = joystick.get_button(3)  # 黄色
            Joys=1
        except:
            Joys=0
        key=pygame.key.get_pressed()  # キーボードが押されたらそのキーをkeyとして記憶
        if idx==0:  # スタート
            screen.blit(img_start, [0, 0])
            if Joys == 1:  ###ゲームパッド
                sur = font.render('Press START button', True, (120,120,40)) # 色を指定して文字str(tmr)を画像surに置き換える
                disp_str(screen, sur, 0, 250, 0, 1.0)
                # screen.blit(sur, [0, 0])  # 座標を指定して画像を表示する
                if (key[pygame.K_SPACE]==True) or (jbtn5 !=0):
                    idx=1
                    pygame.mixer.music.play(-1)
            else:  ###キーボード
                sur = font.render('Press SPACE key', True, (120,120,40)) # 色を指定して文字str(tmr)を画像surに置き換える
                disp_str(screen, sur, 0, 250, 0, 1.0)
                # screen.blit(sur, [0, 0])  # 座標を指定して画像を表示する
                if key[pygame.K_SPACE]==True:
                    idx=1
                    pygame.mixer.music.play(-1)
        if idx==1:   # ゲームプレイ中
            timer=timer+1
            screen.blit(img_haikei, [0, 0])
            # 敵の弾の発射              
            if timer%10 ==1:
                e_set_missile() #弾の発射準備
            e_move_missile(screen) #発射された弾の移動と画像表示
            #壁の移動
            move_wall(screen,timer)
            contact_wall()

            # if jbtn1 != 0:
            #     random_number = random.randrange(1,100)
            #     if v > 25 and v <=250:
            #         if random_number %7 == 1:
            #             set_missile()
            #     if v > -201 and v <=25:
            #         if random_number %50 == 1:
            ##### 弾の発射 #######
            if Joys == 1:
                joy_b = (joy_b+1)*jbtn1
                key_spc = (key_spc+1)*key[pygame.K_SPACE]
            else:
                key_spc = (key_spc+1)*key[pygame.K_SPACE]
            if (joy_b%10 == 1 or key_spc%10 == 1):
                set_missile()
                se_shot.play()
            move_missile(screen) #発射された弾の移動と画像表示

            ####### ロボットの制御
            if Joys == 1:
                if jbtn4 != 0:  # RB
                    omega =  - 1.0
                if jbtn3 != 0:  # LB
                    omega =   1.0
                if joy_ud < -0.01:
                    v =  70
                    # omega = 0
                if joy_ud > 0.01:
                    v = -70
                    # omega = 0
                if joyL_ud < -0.01:
                    v =  70
                    # omega = 0
                if joyL_ud > 0.01:
                    v = -70
                    # omega = 0
                if joy_lr  > 0.01:
                    omega =  - 1.0    
                if joy_lr < -0.01:
                    omega =   1.0
                #### count による特殊処理
                if jbtn7 != 0:
                    if count > 100:
                        set_missile()
                        ta = ta+1
                        if ta> 100:
                            ta = 0
                            count=0
            #####  キーボード矢印キーでの操作
            if key[pygame.K_RIGHT]==True:
                    omega = - 1
            if key[pygame.K_LEFT]==True:
                    omega =   1
            if key[pygame.K_UP]==True:
                    v=  60
                    omega=0
            if key[pygame.K_DOWN]==True:
                    v=- 60
                    omega=0
            #### ロボットの停止       
            if Joys == 1:
                if (jbtn2 != 0) or (jbtn6 != 0): # ボタンXまたはBACKが押されたら
                    omega = 0
                    v=0
            if key[pygame.K_s]==True:  # キーボードでs
                    v=0
                    omega=0 
            move_robot(screen)  # ロボットの移動と画像表示
            # 敵の移動
            move_enemy(screen)
            time=timer*deltaT
            time=math.floor(time) #小数点以下切り捨て
            sur = font.render('Timer: '+str(time_limit-time), True, (120,120,40)) # 色を指定して文字str(tmr)を画像surに置き換える
            screen.blit(sur, [0, 0])  # 座標を指定して画像を表示する
            sur = font.render('Score: '+str(score), True, (0,0,0)) # 色を指定して文字str(tmr)を画像surに置き換える
            screen.blit(sur, [0, 30])  # 座標を指定して画像を表示する
            sur = font.render('count: '+str(count), True, (200,200,200)) # 色を指定して文字str(tmr)を画像surに置き換える
            screen.blit(sur, [600, 0])  # 座標を指定して画像を表示する
            if (time_limit-time) < 10:
                if switch == 0:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('bgm.wav')
                    pygame.mixer.music.play(-1)
                    switch=1
            if (time_limit-time) < 0:
                idx=2

        if idx==2:   # GAMEOVER表示   
            pygame.mixer.music.stop()

            # 最終スコアの表示

            if zenkaiscore < score:
                screen.blit(img_high, [0, 0])
                sur = font3.render(str(score), True, (255,200,255)) # 色を指定して文字str(tmr)を画像surに置き換える
                disp_str(screen, sur, 10, -45, 0, 1.0)
                # screen.blit(sur, [350, 250])  # 座標を指定して画像を表示する
                if written == 0:
                    scorefile.write(str(score))
                    written=1
            else:
                screen.blit(img_gameover, [0, 0])
                sur = font2.render('Score: '+str(score), True, (255,200,255)) # 色を指定して文字str(tmr)を画像surに置き換える
                disp_str(screen, sur, 0, -45, 0, 1.0)
                # screen.blit(sur, [105, 300])  # 座標を指定して画像を表示する
                if written == 0:
                    scorefile.write(str(zenkaiscore))
                    written=1
            scorefile.close()

        pygame.display.update()  
        clock.tick(30)  # 1秒間に30回，画面を更新

if __name__ == '__main__':
    main()