import math
import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:  # 練習3 こうかとんと爆弾が画面外に出ないための関数
    """
    引数:こうかとんRectか爆弾rect
    戻り値:判定結果タプル(横方向、縦方向)
    画面内ならTrue, 画面外ならFalse
    """
    yoko, tate= True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向にはみ出ていたら
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  #   縦方向にはみ出ていたら
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:  # 演習1
    """
    引数:表示先のスクリーン
    戻り値:なし
    こうかとんと爆弾が重なったらゲームオーバーの画面を表示し、5秒後にプログラムを終了
    """
    gameover_img = pg.Surface((WIDTH, HEIGHT))  # ゲームオーバー画面の作成
    pg.draw.rect(gameover_img, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    gameover_img.set_alpha(128)  #　ゲームオーバー画面の透明度
    

    fonto = pg.font.Font(None, 80)  # テキスト作成
    txt = fonto.render("Game Over",
                       True, (255, 255, 255))
    gameover_img.blit(txt, [400, 250])

    gameover_kk_img = pg.image.load("fig/8.png")  # こうかとんの画像描画
    gameover_kk_rct_L = gameover_kk_img.get_rect()
    gameover_kk_rct_L.center = 360,270
    gameover_kk_rct_R = gameover_kk_img.get_rect()
    gameover_kk_rct_R.center = 750,270
    gameover_img.blit(gameover_kk_img, gameover_kk_rct_L)
    gameover_img.blit(gameover_kk_img,gameover_kk_rct_R)
    
    screen.blit(gameover_img,[0,0])
    pg.display.update()
    time.sleep(5)

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:  # 演習2
    """
    引数なし
    戻り値:拡大リストと加速度リスト
    爆弾の拡大サイズリストbb_imgsと加速度リストbb_accsを作成する
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]  # 爆弾の速さのリスト
    for r in range(1,11):
        bb_img = pg.Surface((20*r, 20*r))  # 爆弾の大きさのリスト
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]: # 演習3
    """
    引数なし
    戻り値:移動量タプルと対応した画像の辞書
    こうかとんの移動量タプルに対応したこうかとんの画像を返す辞書
    """
    kk_img = pg.image.load("fig/3.png")
    kk_flip_img = pg.transform.flip(kk_img,True, False)  # 右向き用こうかとん画像
    kk_dict = {
        (0, 0): pg.transform.rotozoom(kk_img, 0, 0.9),       # その場
        (+5, 0): pg.transform.rotozoom(kk_flip_img, 0,0.9),    # 右
        (-5, 0): pg.transform.rotozoom(kk_img, 0, 0.9),      # 左(そのまま)
        (0, -5): pg.transform.rotozoom(kk_flip_img, 90, 1.0),    # 上
        (0, +5): pg.transform.rotozoom(kk_flip_img, -90, 1.0),     # 下
        (+5, -5): pg.transform.rotozoom(kk_flip_img, 45, 0.9),  # 右上
        (+5, +5): pg.transform.rotozoom(kk_flip_img, -45, 0.9),   # 右下
        (-5, -5): pg.transform.rotozoom(kk_img, -45, 0.9),   # 左上
        (-5, +5): pg.transform.rotozoom(kk_img, 45, 0.9),    # 左下
    }
    return kk_dict

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_img = pg.Surface((20,20))  # 練習2:爆弾作成
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()  # 爆弾Rect
    bb_rct.centerx = random.randint(0, WIDTH)  # 爆弾横座標
    bb_rct.centery = random.randint(0, HEIGHT)  # 爆弾縦座標
    vx, vy = +5, +5  # 爆弾の速度

    clock = pg.time.Clock()
    tmr = 0
    
    bb_imgs, bb_accs = init_bb_imgs()  # 爆弾の拡大、加速用のリストを取得する
    kk_imgs = get_kk_imgs()  # こうかとんの移動量タプルに対応した画像を返す辞書を取得

    while True:
        # ユーザーの入力やOSから送られるイベントを1つずつ取り出して処理する
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾の重なり判定
            gameover(screen)
            return  # ゲームオーバー

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():  # 練習1
            if key_lst[key]:
                sum_mv[0] += mv[0]  # 横方向の移動量を加算
                sum_mv[1] += mv[1]  # 縦方向の移動量を加算
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)
        avx = vx * bb_accs[min(tmr//500, 9)]  # 爆弾の横方向を加速する
        avy = vy * bb_accs[min(tmr//500, 9)]  # 爆弾の縦方向を加速する
        bb_img = bb_imgs[min(tmr//500, 9)]  # 爆弾の大きさを拡大していく
        bb_rct.move_ip(avx, avy)  #爆弾移動
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横方向にはみ出ていたら
            vx *= -1
        if not tate:  # 縦方向にはみ出ていたら
            vy *= -1
        
        kk_img = kk_imgs[tuple(sum_mv)]  # 移動方向に応じてこうかとん画像の切替
        
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
