import os
import random
import sys
import math
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとん or 爆弾のRect
    戻り値：横方向・縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def create_bomb_properties() -> tuple[list[pg.Surface], list[float]]:
    """
    拡大する爆弾の画像リストと加速度リストを生成する関数

    Returns:
        tuple[list[pg.Surface], list[float]]: 爆弾画像のリストと加速度のリスト
    """
    bomb_imgs = []
    accs = [1 + 0.1 * i for i in range(10)]
    
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bomb_imgs.append(bb_img)
    
    return bomb_imgs, accs


def create_kokaton_images() -> dict[tuple[int, int], pg.Surface]:
    """
    こうかとんの向きに応じた画像を生成する関数

    Returns:
        dict[tuple[int, int], pg.Surface]: 移動量をキー、対応する画像をバリューとする辞書
    """
    kk_img = pg.image.load("fig/3.png")
    kk_img = pg.transform.rotozoom(kk_img, 0, 2.0)
    directions = {
        (0, -5): pg.transform.rotozoom(kk_img, 90, 1.0),
        (5, -5): pg.transform.rotozoom(kk_img, 45, 1.0),
        (5, 0): pg.transform.flip(kk_img, True, False),
        (5, 5): pg.transform.rotozoom(pg.transform.flip(kk_img, True, False), -45, 1.0),
        (0, 5): pg.transform.rotozoom(kk_img, -90, 1.0),
        (-5, 5): pg.transform.rotozoom(kk_img, -45, 1.0),
        (-5, 0): kk_img,
        (-5, -5): pg.transform.rotozoom(kk_img, 45, 1.0)
    }
    return directions


def calc_bomb_direction(bomb: pg.Rect, kokaton: pg.Rect) -> tuple[float, float]:
    """
    爆弾がこうかとんに近づく方向ベクトルを計算する関数

    Args:
        bomb (pg.Rect): 爆弾のRect
        kokaton (pg.Rect): こうかとんのRect

    Returns:
        tuple[float, float]: 正規化された方向ベクトル
    """
    dx = kokaton.centerx - bomb.centerx
    dy = kokaton.centery - bomb.centery
    distance = math.hypot(dx, dy)
    
    if distance < 300:  # 近すぎる場合は現在の方向を維持
        return None
    
    norm = math.sqrt(50)  # 速度のノルムを√50に設定
    return dx / distance * norm, dy / distance * norm


def game_over(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数

    Args:
        screen (pg.Surface): 描画対象の画面Surface

    Returns:
        None
    """
    screen.fill((0, 0, 0))
    
    sad_kokaton = pg.image.load("fig/8.png")
    sad_kokaton = pg.transform.rotozoom(sad_kokaton, 0, 2.0)
    screen.blit(sad_kokaton, ((WIDTH - sad_kokaton.get_width()) // 2, 100))
    
    font = pg.font.Font(None, 80)
    text = font.render("Game Over", True, (255, 0, 0))
    screen.blit(text, ((WIDTH - text.get_width()) // 2, 400))
    
    pg.display.update()
    pg.time.wait(5000)  # 5秒間表示


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 2.0)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 900, 400
    
    bomb_imgs, accs = create_bomb_properties()
    bb_img = bomb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5
    
    kk_imgs = create_kokaton_images()
    
    clock = pg.time.Clock()
    tmr = 0  #
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        
        screen.blit(bg_img, [0, 0])
        
        if kk_rct.colliderect(bb_rct):
            game_over(screen)
            return
        
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        
        if sum_mv != [0, 0]:
            kk_img = kk_imgs[tuple(sum_mv)]
        screen.blit(kk_img, kk_rct)
        
        # 爆弾の移動と表示
        acc = accs[min(tmr // 500, 9)]
        bb_img = bomb_imgs[min(tmr // 500, 9)]
        direction = calc_bomb_direction(bb_rct, kk_rct)
        if direction:
            vx, vy = direction
        vx *= acc
        vy *= acc
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct)
        
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
