"""
いわゆる迷路ってヤツ - 2 -

Python 3.13.0
pygame 2.6.1

IDE:VSCode Studio + Trae
Google Coad Assist + GPT-4.1

maze = 日本語訳：迷路/迷宮/困惑

"""
import pygame
import random

game_state = "title"

# --- 画面サイズ定義 ---
WIDTH = 800
HEIGHT = 600
TILE_SIZE = 15 # タイルのサイズ
MAZE_WIDTH = WIDTH // TILE_SIZE # //は整数除算
MAZE_HEIGHT = HEIGHT // TILE_SIZE
# TIME_LIMIT_SECONDS = 180 (念のため)

# --- 配色定義 ---
WHITE = (255, 255, 255)
DARK_GRAY = (100, 100, 100)
AQUA = (0, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
TOMATO = (255, 99, 71)
PALE_GREEN = (152, 251, 152)
AZURE = (240, 255, 255)
ORANGE = (255, 165, 0)

# --- 設定 --- 
BONUS_MOVE_INTERVAL = 5 # ボーナスアイテムの移動間隔
PLAYER_BLINK_DURATION_SECONDS = 3 # プレイヤーの点滅時間 (秒)
PLAYER_BLINK_INTERVAL_MS = 200 # プレイヤーの点滅間隔 (ミリ秒)
HELP_PENALTY_SECONDS = 3 # ヘルプ表示のペナルティ

# タイムボーナスの設定
BONUS_TYPES = [
    {"name": "Bonus10", "time": 10, "color": TOMATO, "count": 3}, # 10秒加算
    {"name": "Bonus30", "time": 30, "color": ORANGE, "count": 1}, # 30秒加算
    {"name": "Bonus60", "time": 60, "color": PALE_GREEN, "count": 1} # 60秒加算
    ]
# ゲームタイプの設定
GAME_TYPES = [
    {"name": "Type A: Normal", "id": "normal", "time_limit": 180}, # normal
    {"name": "Type B: Warp Gates", "id": "warp", "time_limit": 300}, # warp
    {"name": "Type C: Proximity Challenge", "id": "proximity", "time_limit": 180} # proximity
    ]

current_game_type_index = 0 # 初期は通常ゲーム
selected_game_type_on_title = 0 # タイトル画面で選択されたゲームタイプ

NUM_WARP_PORTALS = 3 # ワープポータルの数
warp_portals = []

VISIBILITY_RADIUS = 1 # 視界の半径

GAME_OVER_TIMEOUT_SECONDS = 5
GAME_WON_TIMEOUT_SECONDS = 5

# --- ゲームの状態変数 ---
title_screen_start_time = 0 # タイトル画面の開始時刻
demo_direction_timer = 0 # デモ時の移動方向のタイマー
game_over_start_time = 0 # ゲームオーバー画面の開始時刻
game_won_start_time = 0 # ゲームクリア画面の開始時刻
start_time = 0 # 経過時間計算のための開始時刻
demo_direction = (0, 0) # デモ時の移動方向
running = True
# remaining_time = TIME_LIMIT_SECONDS (念のため)
score = 0
game_won = False 
game_over = False
bonus_items = [] 

# --- 迷路の生成 ---
def generate_maze(width, height):
    """
    迷路を生成する関数
    
    Parameters:
    - width: 迷路の幅
    - height: 迷路の高さ
    
    Returns:
    - maze: 生成された迷路
    - start_x: スタート地点のx座標
    - start_y: スタート地点のy座標
    
    Raises:
    - None
    
    Note:
    - 迷路は2次元配列に格納される
    - スタート地点は(0, 0)
    - ゴール地点は(width - 1, height - 1)
    
    Example:
    maze, start_x, start_y = generate_maze(10, 10)
    print(maze)
    print(start_x, start_y)
    
    Output:
    [['Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall'],
     ['Wall', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Wall'],
     ['Wall', 'Path', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Path', 'Wall'],
     ['Wall', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Wall'],
     ['Wall', 'Path', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Path', 'Wall'],
     ['Wall', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Wall'],
     ['Wall', 'Path', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Path', 'Wall'],
     ['Wall', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Path', 'Wall'],
     ['Wall', 'Path', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Path', 'Wall'],
     ['Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall', 'Wall']]
    0 0
    """
    
    # 迷路の初期化
    maze = [['Wall' for _ in range(width)] for _ in range(height)] # 壁を埋める
    stack = [] 

    # スタート地点
    start_x, start_y = 0, 0 
    maze[start_y][start_x] = "Path" # スタート地点を通路にする
    stack.append((start_x, start_y)) # スタックに追加

    while stack: # スタックが空になるまで
        x, y = stack[-1] # 現在の座標
        neighbors = [] # 隣接する空き地

        # 隣接する空き地を探す
        # 上下左右
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            # 隣接する座標
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == "Wall": # 隣接する座標が壁なら
                neighbors.append((nx, ny)) # 隣接する空き地リストに追加

        if neighbors: # 隣接する空き地がある場合
            # random に次のセルを選択
            next_x, next_y = random.choice(neighbors)
            # 現在のセルと次のセルの間の壁を壊す
            maze[(y + next_y) // 2][(x + next_x) // 2] = "Path"
            # 次のセルを通路にする
            maze[next_y][next_x] = "Path"
            # 新しいセルをスタックに追加
            stack.append((next_x, next_y))
        else:
            # 行き止まりならスタックから戻る
            stack.pop()
            
    return maze, start_x, start_y # 迷路とスタート地点の座標を返す

# --- 迷路を描画する関数 ---
def draw_maze(screen, maze, player_x, player_y, visibility_radius):
    """
    迷路を描画する関数
    
    Parameters:
    - screen: 描画する画面
    - maze: 描画する迷路
    - player_x: プレイヤーのx座標
    - player_y: プレイヤーのy座標
    - visibility_radius: 視界の半径
    """
    for y, row in enumerate(maze): # 迷路を描画
        for x, cell in enumerate(row): 
            # プレイヤーからの距離の2乗を計算
            distance_sq = (x - player_x) ** 2 + (y - player_y) ** 2
            if distance_sq <= visibility_radius ** 2 or visibility_radius == max(MAZE_WIDTH, MAZE_HEIGHT): # 視界の半径の2乗と比較
                if cell == "Wall": # 壁は白
                    color = WHITE
                else: # 通路
                    color = DARK_GRAY # 視界内の道の色
                if cell == "Goal": # ゴールは赤
                    color = RED
                # セルを描画(ウインドウ外のセルは描写されない)
                pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

                
# --- プレイヤーのクラス ---
class Player:
    def __init__(self, x, y): # コンストラクタ
        self.x = x # x座標
        self.y = y # y座標
        self.is_blinking = False # ブリンキング(点滅)状態
        self.blink_end_time = 0 # ブリンキング終了時間

    # --- プレイヤーの移動 ---
    def move(self, dx, dy, maze): 
        """
        プレイヤーを移動
        
        Parameters:
        - dx: x方向の移動量
        - dy: y方向の移動量
        - maze: 迷路
        
        Returns:
        - None
        
        Raises:
        - None
        
        """
        # 新しい座標を計算
        new_x, new_y = self.x + dx, self.y + dy
        # 移動先が通路かゴールなら移動
        if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and (maze[new_y][new_x] == "Path" or maze[new_y][new_x] == "Goal"):
            self.x += dx 
            self.y += dy 

# --- ゲームの初期化 ---
def initialize_game():
    """
    ゲームを初期化

    Parameters:
        None
    
    Returns:
        _type_: _description_
    """
    
    pygame.init() # Pygame を初期化
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) # ウィンドウを作成
    pygame.display.set_caption('Maze Game') # ウィンドウのタイトル
    message_font = pygame.font.Font(None, 60) # メッセージのフォント
    score_font = pygame.font.Font(None, 36) # スコアのフォント
    title_font = pygame.font.Font(None, 72) # タイトルのフォント
    Instruction_font = pygame.font.Font(None, 36) # インストラクションのフォント
    clock = pygame.time.Clock() # クロック
    global title_screen_start_time # タイトル画面の開始時刻
    title_screen_start_time = pygame.time.get_ticks() # ゲーム開始時、タイトル画面なので時刻を記録
    return screen, message_font, score_font, title_font, Instruction_font, clock # 返却値

# --- ゲームの初期化 ---
screen, message_font, score_font, title_font, Instruction_font, clock = initialize_game()

# --- グローバル変数の初期化 ---
maze, player_start_x, player_start_y = generate_maze(MAZE_WIDTH, MAZE_HEIGHT) # 迷路を生成
player = Player(player_start_x, player_start_y) # プレイヤーを生成
goal_x, goal_y = MAZE_WIDTH - 1, MAZE_HEIGHT - 1 # ゴールの座標
maze[goal_y][goal_x] = "Goal" # 迷路のゴールを設定

# --- ゲームのメインループ ---
def game_loop():
    """
    ゲームのメインループ
    
    Parameters:
        None

    Returns:
        None
    
    Raises:
        None

    """
    global running # グローバル変数
    
    while running: 
        now = pygame.time.get_ticks() # 現在の時刻
        handle_events() # イベントの処理
        update_game_logic() # ゲームのロジックの更新
        render_game() # ゲームの描画
        clock.tick(30) # フレームレート = 30fps

# --- イベントの処理 ---
def handle_events():
    """
    イベント処理
    
    Parameters:
        None
    
    Returns:
        None
    
    Raises:
        None
    
    """
    global running
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # ウィンドウを閉じたらゲーム終了
            running = False
        elif event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_ESCAPE: # ESC を押したらゲームを終了
                running = False
            handle_keydown_events(event) # キー入力の処理

# --- キー入力の処理 ---
def handle_keydown_events(event):
    """
    キー入力の処理(プレイ以外)

    Parameters:
        event: pygame.event
    
    Returns:
        None
    
    Raises:
        None
    
    """    
    global game_state, title_screen_start_time, current_game_type_index, selected_game_type_on_title
    
    if game_state == "title": # タイトル画面
        if event.key == pygame.K_RETURN: # Enter を押したら
            current_game_type_index = selected_game_type_on_title # 選択されたゲームタイプのインデックス
            game_state = "playing" # プレイ画面に移行
            reset_game_state_for_playing() # リセット
        # タイトル画面で左右キーを押したらゲームタイプを切り替え
        elif event.key == pygame.K_LEFT:
            selected_game_type_on_title = (selected_game_type_on_title - 1)%len(GAME_TYPES)
        elif event.key == pygame.K_RIGHT:
            selected_game_type_on_title = (selected_game_type_on_title + 1)%len(GAME_TYPES)
    elif game_state == "playing": # プレイ画面
        handle_playing_keydown(event) # プレイ画面のキー入力
    elif game_state in ["game_won", "game_over"]: # ゲームクリア/ゲームオーバー
        if event.key == pygame.K_RETURN: # Enter を押したら
            if game_state == "game_won": # game won
                game_state = "title" # タイトル画面に移行
                title_screen_start_time = pygame.time.get_ticks() # タイトル画面の開始時刻
            else: # game over
                game_state = "playing"
                reset_game_state_for_playing() # game over => playing
    elif game_state == "demo": # デモ
        if event.key == pygame.K_RETURN: # Enter を押したら
            game_state = "title" # プレイ画面に移行
            title_screen_start_time = pygame.time.get_ticks()
        elif event.key == pygame.K_h: # H を押したら
            show_help_screen() # ヘルプ画面(maze全体)を表示

# --- プレイ中のキー入力の処理 ---
def handle_playing_keydown(event):
    """
    プレイ中のキー入力の処理
    """
    global player, maze, score, goal_x, goal_y, current_game_type_index
    
    if not game_won and not game_over: # ゲームクリア/ゲームオーバー以外
        dx, dy = 0, 0
        if event.key == pygame.K_LEFT:
            dx = -1 
            # player.move(-1, 0, maze)
        elif event.key == pygame.K_RIGHT:
            dx = 1
            # player.move(1, 0, maze)
        elif event.key == pygame.K_UP:
            dy = -1 
            # player.move(0, -1, maze)
        elif event.key == pygame.K_DOWN:
            dy = 1
            # player.move(0, 1, maze)
        elif event.key == pygame.K_h: # H を押したら
            show_help_screen() # ヘルプ画面を表示
            return # ヘルプ表示以降の処理を行わない

        if dx != 0 or dy != 0: # 移動キーが押されたら
            old_px, old_py = player.x, player.y # 移動前の座標

            original_dist_to_goal = -1
            game_id = GAME_TYPES[current_game_type_index]["id"]
            
            if game_id == "proximity":
                # 移動前のゴールまでの距離を計算(マンハッタン距離)
                original_dist_to_goal = abs(old_px - goal_x) + abs(old_py - goal_y)
                
            player.move(dx, dy, maze) # プレイヤーを移動

            # 実際にプレイヤーが移動したかを確認
            if player.x != old_px or player.y != old_py: # プレイヤーが実際に移動した場合
                if game_id == "proximity":
                    # 移動後のゴールまでの距離を計算
                    new_dist_to_goal = abs(player.x - goal_x) + abs(player.y - goal_y)
                    # 距離の変化分にスコアに加算(近づけばプラス、遠のけばマイナス)
                    score += (original_dist_to_goal - new_dist_to_goal)

# --- ヘルプ表示 ---
def show_help_screen():
    """
    ヘルプ画面を表示
    
    Parameters:
        None
    
    Returns:
        None
    
    Raises:
        None

    """
    global running, remaining_time, start_time
    
    temp_visibility = max(MAZE_WIDTH, MAZE_HEIGHT) # 視界の半径を最大値にする
    draw_maze(screen, maze, player.x, player.y, temp_visibility) # 迷路の描画
    pygame.display.flip() # 画面の更新
    penalty_start_time = pygame.time.get_ticks() # ペナルティの開始時刻
    temp_running_penalty = True # ペナルティ中
    while pygame.time.get_ticks() - penalty_start_time < 3000 and temp_running_penalty: # 3秒間ヘルプ画面を表示
        for p_event in pygame.event.get():
            if p_event.type == pygame.QUIT:
                running = False
                temp_running_penalty = False
                break
            if p_event.type == pygame.KEYDOWN and p_event.key == pygame.K_ESCAPE:
                running = False
                temp_running_penalty = False
                break
        if not running:
            break
    clock.tick(30)
    
    if running:
        # プレイ中のみペナルティを適用 
        if game_state == "playing":
            start_time -= HELP_PENALTY_SECONDS * 1000 # ペナルティとしてstart_timeを減らす
                        
# --- ゲームのロジックの更新 ---
def update_game_logic():
    """
    ゲームのロジックを更新
    
    parameters:
        None
    
    Returns:
        None
    
    Raises:
        None

    """
    global game_state, title_screen_start_time, game_over_start_time, game_won_start_time, current_game_type_index, selected_game_type_on_title
    
    if game_state == "title":
        # タイトル画面で5秒経過したらデモ画面へ
        if pygame.time.get_ticks() - title_screen_start_time > 5000: # 5000ms = 5秒
            current_game_type_index = selected_game_type_on_title
            game_state = "demo"
            reset_demo_state()
    elif game_state == "playing":
        update_playing_logic()
    elif game_state == "game_won":
        # ゲームクリア時に5秒経過したらタイトル画面へ
        if pygame.time.get_ticks() - game_won_start_time > GAME_WON_TIMEOUT_SECONDS * 1000:
            game_state = "title"
            title_screen_start_time = pygame.time.get_ticks()
    elif game_state == "game_over":
        # ゲームオーバー時に5秒経過したらタイトル画面へ
        if pygame.time.get_ticks() - game_over_start_time > GAME_OVER_TIMEOUT_SECONDS * 1000:
            game_state = "title"
            title_screen_start_time = pygame.time.get_ticks()
    elif game_state == "demo":
        update_demo_logic()

# --- プレイ中のロジックの更新 ---
def update_playing_logic():
    """
    プレイ中のロジックの更新
    
    Arguments:
        None
        
    Parameters:
        None
    
    Returns:
        None
    
    Raises:
        None

    """
    global game_won, game_over, start_time, remaining_time, game_state, game_over_start_time, score
    
    # 時間制限
    current_game_id = GAME_TYPES[current_game_type_index]["id"]
    # プレイヤーの点滅状態を更新
    if player.is_blinking and pygame.time.get_ticks() >= player.blink_end_time:
        player.is_blinking = False
    current_time_limit = GAME_TYPES[current_game_type_index]["time_limit"]
    
    if not game_won and not game_over: # ゲームクリアまたはゲームオーバーしていない場合
        elapsed_time_seconds = (pygame.time.get_ticks() - start_time) // 1000 # 経過時間
        current_remaining_time = current_time_limit - elapsed_time_seconds # 残り時間
        remaining_time = current_remaining_time # 残り時間
        if current_remaining_time <= 0: # 時間制限を超えた場合
            remaining_time = 0 # 残り時間を0に
            game_over = True # ゲームオーバー
            game_state = "game_over" # ゲームオーバー画面に移行
            game_over_start_time = pygame.time.get_ticks() # ゲームオーバー時の時刻を記録
        else:
            remaining_time = current_remaining_time 
        # handle_bonus_items() # ボーナスアイテムの処理
        # if GAME_TYPES[current_game_type_index]["id"] == "warp": # ワープ迷路の場合
        
        if current_game_id == "normal" or current_game_id == "warp":
            handle_bonus_items() # ボーナスアイテムの処理
            
        if current_game_id == "warp": # ワープ迷路の場合
            handle_warp_portal_collision() # ワープポータルの処理
        
        # 全ゲームタイプでゴール到達をチェック     
        check_goal_reached() # ゴールに到達したかどうかをチェック

# --- ボーナスアイテムの処理 ---
def handle_bonus_items():
    """
    ボーナスアイテムの処理
    
    ボーナスアイテムがプレイヤーと重なった場合、時間を加算する。
    ボーナスアイテムをランダムな場所に移動させる。
    ボーナスアイテムの移動タイミングを管理する。
    
    Parameters:
        None
    
    Returns:
        None
    
    Raises:
        None

    """
    global player, bonus_items, start_time, maze, goal_x, goal_y
    
    now_tick = pygame.time.get_ticks() # 現在の時刻
    
    # ボーナスアイテムをプレイヤーと重なった場合、時間を加算する。
    # コレクションしたアイテムを格納するリスト
    collected_items_to_move = []
    # ボーナスアイテムをチェック 
    for item in bonus_items: 
        if  player.x == item["x"] and player.y == item["y"]: # プレイヤーと重なった場合
            # ボーナスアイテムの時間を加算
            bonus_time_value = next(b["time"] for b in BONUS_TYPES if b["name"] == item["type"]) # ボーナスアイテムの時間を取得
            start_time += bonus_time_value * 1000 
            collected_items_to_move.append(item) # コレクションしたアイテムを格納
    
    # ボーナスアイテムをランダムな場所に移動させる。
    for item in collected_items_to_move:
        move_bonus_item(item, maze, player.x, player.y, goal_x, goal_y,bonus_items)
    
    # ボーナスアイテムの移動タイミングを管理
    update_bonus_item_movement(now_tick, maze, player, goal_x, goal_y, bonus_items)

# --- ボーナスアイテムの移動タイミングを管理 ---
def update_bonus_item_movement(now_tick, current_maze, current_player_obj, current_g_x, current_g_y, current_bonus_items):
    """
    ボーナスアイテムの移動タイミングを管理
    
    Parameters
    ----------
    now_tick : int
        現在の時刻
    current_maze : list
        現在の迷路の状態
    current_player_obj : Player
        現在のプレイヤーの状態
    current_g_x : int
        ゴールのx座標
    current_g_y : int
        ゴールのy座標
    current_bonus_items : list
        現在のボーナスアイテムの状態
    
    Returns
    -------
    None
    
    Raises
    ------
    None
    
    """
    for item in current_bonus_items: # すべてのボーナスアイテムに対して
        if "next_move_time" not in item: # 初めて移動する場合
            item["next_move_time"] = now_tick + BONUS_MOVE_INTERVAL * 1000 # 次の移動タイミングを設定
        if now_tick >= item.get("next_move_time", float("inf")): # 移動タイミングになった場合
            move_bonus_item(item, current_maze, current_player_obj.x, current_player_obj.y,current_g_x, current_g_y, current_bonus_items)
            # 次の移動タイミングを設定

# --- ボーナスアイテムを移動させる ---
def move_bonus_item(item_to_move, current_maze, player_x, player_y, goal_x, goal_y, current_bonus_items):
    """
    ボーナスアイテムをランダムな場所に移動させる
    
    Parameters
    ----------
    item_to_move : dict
        移動するアイテムの情報
    current_maze : list
        現在の迷路の状態
    player_x : int
        プレイヤーのx座標
    player_y : int
        プレイヤーのy座標
    goal_x : int
        ゴールのx座標
    goal_y : int
        ゴールのy座標
    current_bonus_items : list
        現在のボーナスアイテムのリスト
    """
    moved_successfully = False # 移動成功フラグ
    for _ in range(100): # 配置試行回数
        bx = random.randint(0, MAZE_WIDTH - 1) # x座標をランダムに生成
        by = random.randint(0, MAZE_HEIGHT - 1) # y座標をランダムに生成
        # ボーナスアイテムの配置場所をランダムに変更
        if current_maze[by][bx] == "Path" and\
            (bx != player_x or by != player_y) and\
            (bx != goal_x or by != goal_y):
            if all(not(other["x"] == bx and other["y"] == by) for other in current_bonus_items if other is not item_to_move):
                item_to_move["x"] = bx
                item_to_move["y"] = by
                moved_successfully = True # 移動成功
                break

    if moved_successfully: 
        # 移動に成功した場合
        item_to_move["next_move_time"] = pygame.time.get_ticks() + BONUS_MOVE_INTERVAL * 1000 # 次の移動タイミングを設定
    else:
        # 移動に失敗したときでも、再試行するように設定
        item_to_move["next_move_time"] = pygame.time.get_ticks() + 1000
        
# --- ゴールに到達したかどうかをチェック ---        
def check_goal_reached():
    """
    ゴールに到達したかどうかをチェック
    
    Returns:
        None
    
    Raises:
        None

    """
    global player,goal_x,goal_y, game_won, score, remaining_time, game_over, game_state, game_won_start_time
    
    if player.x == goal_x and player.y == goal_y: # ゴールに到達した場合
        game_won = True # クリア
        score += remaining_time # スコアを更新
        if score < 0: 
            score = 0
        # game_over = True # クリア時はゲームオーバーにしないのでコメントアウト
        game_state = "game_won" 
        game_won_start_time = pygame.time.get_ticks() # ゲームクリア時の時刻を記録

# --- デモ画面のロジック ---
def update_demo_logic():
    """
    デモ画面のロジックを更新
    
    Returns:
        None
    
    Raises:
        None

    """
    global player, demo_direction, demo_direction_timer, bonus_items, maze, goal_x, goal_y, current_game_type_index
    
    now_tick = pygame.time.get_ticks() # 現在の時刻 
    game_id_demo = GAME_TYPES[current_game_type_index]["id"]  
    
    # プレイヤーの点滅状態を更新
    if player.is_blinking and pygame.time.get_ticks() >= player.blink_end_time:
        player.is_blinking = False
    
    if pygame.time.get_ticks() - demo_direction_timer >= 1000: # 1秒ごとに移動方向をランダムに変更
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)] # 上下左右の方向
        random.shuffle(dirs) # リストをランダムに並べ替え
        moved_in_demo = False # 移動フラグ
        for dx_demo, dy_demo in dirs: # 各方向に移動
            nx, ny = player.x + dx_demo, player.y + dy_demo
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and maze[ny][nx] in ("Path", "Goal"): # 移動先が通路かゴールなら
                demo_direction = (dx_demo, dy_demo) # 移動方向を更新
                player.move(dx_demo, dy_demo, maze) # プレイヤーを移動
                moved_in_demo = True # 移動した
                break
        if not moved_in_demo: # 移動しなかった場合
            demo_direction = (0, 0) # 移動方向をリセット
        demo_direction_timer = pygame.time.get_ticks() # タイマーをリセット

        # Proximity 以外でのボーナスアイテム処理
        if game_id_demo != "proximity":
        # コレクションしたアイテムを格納するリスト
            demo_collected_items_to_move = []
                 
            for item in bonus_items: # ボーナスアイテムをチェック
                if  player.x == item["x"] and player.y == item["y"]: # コレクションした場合
                    demo_collected_items_to_move.append(item) # コレクションしたアイテムを格納
                    
            for item in demo_collected_items_to_move: # コレクションしたアイテムを移動
                move_bonus_item(item, maze, player.x, player.y, goal_x, goal_y,bonus_items) # ボーナスアイテムを移動
            update_bonus_item_movement(now_tick, maze, player, goal_x, goal_y, bonus_items) # ボーナスアイテムの移動を更新
            
            if game_id_demo == "warp": # ワープポータルゲームの場合
                handle_warp_portal_collision() # ワープポータルの衝突を処理
        
        if player.x == goal_x and player.y == goal_y: # ゴールに到達した場合
            reset_demo_state() # デモ画面をリセット

# --- ゲーム画面の描画 ---
def render_game():
    """
    ゲーム画面を描画する
    ※使用していない項目があるかも

    Args:
        None
    
    Returns:
        None
        
    """
    # 背景を塗りつぶす
    screen.fill(BLACK)
    # タイトル
    if game_state == "title":
        draw_title_screen(screen, title_font, Instruction_font, score_font, WIDTH, HEIGHT, WHITE, DARK_GRAY, selected_game_type_on_title) # 画面の描画
    # プレイ画面
    elif game_state == "playing":
        current_game_id_playing = GAME_TYPES[current_game_type_index]["id"]
        draw_playing_screen(screen, maze, player, VISIBILITY_RADIUS, bonus_items, TILE_SIZE, GREEN, score_font, remaining_time, AQUA, current_game_id_playing)
    # ゲームクリア画面
    elif game_state == "game_won":
        current_game_id_won = GAME_TYPES[current_game_type_index]["id"]
        draw_game_won_screen(screen, maze, player, VISIBILITY_RADIUS, TILE_SIZE, GREEN, message_font, score_font, score, WIDTH, HEIGHT, WHITE, Instruction_font, YELLOW, current_game_id_won)
    # ゲームオーバー/終了画面
    elif game_state == "game_over":
        current_game_id = GAME_TYPES[current_game_type_index]["id"]
        draw_game_over_screen(screen, maze, player, VISIBILITY_RADIUS, TILE_SIZE, GREEN, message_font, score_font, Instruction_font, WIDTH, HEIGHT, WHITE, RED, DARK_GRAY, BLACK, YELLOW, current_game_id)
    # デモ画面
    elif game_state == "demo":
        draw_demo_screen(screen, maze, player, VISIBILITY_RADIUS, bonus_items, TILE_SIZE, GREEN, score_font, WIDTH, AQUA, warp_portals)
    # 画面を更新
    pygame.display.flip()
    
# --- プレイ画面の描画 ---    
def draw_playing_screen(screen, maze, player, visibility_radius, bonus_items, TILE_SIZE, GREEN, score_font, remaining_time, AQUA, game_id):
    """
    ゲーム画面を描画
    ※使用されていない項目があるかも

    Parameters
    ----------
    screen : pygame.display
        描画対象の画面
    maze : 2d list
        迷路の状態
    player : Player object
        プレイヤーの状態
    visibility_radius : int
        視界の半径
    bonus_items : list
        ボーナスアイテムの状態
    TILE_SIZE : int
        1つのタイルのサイズ
    GREEN : tuple
        プレイヤーの色
    score_font : pygame.font.Font
        スコアのフォント
    remaining_time : int
        残りの時間
    AQUA : tuple
        ワープポータルの色
    game_id : str
        ゲームのID
    """
    # current_game_id = GAME_TYPES[current_game_type_index]["id"] # 念のため
    
    # 迷路の描画
    draw_maze(screen, maze, player.x, player.y, visibility_radius)

    # プレイヤーの描画(点滅状態を含む, 念のため)
    # pygame.draw.rect(screen, GREEN, (player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    should_draw_player = True
    if player.is_blinking:
        if(pygame.time.get_ticks() // PLAYER_BLINK_INTERVAL_MS) % 2 == 1: # 奇数版での間隔で不表示
            should_draw_player = False
    if should_draw_player:
        pygame.draw.rect(screen, GREEN, (player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # ボーナスアイテムの描画 (プロクシミティモード以外)
    # for item in bonus_items:
    if game_id != "proximity":
        for item in bonus_items:
            if item["active"]:
            # ボーナスアイテムの色を取得
                bonus_color = next((b["color"] for b in BONUS_TYPES if b["name"] == item["type"]), BLACK) # 見つからない場合は黒
            # ボーナスアイテムを描画
                pygame.draw.ellipse(screen, bonus_color, (item["x"] * TILE_SIZE, item["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    # ワープポータルの描画 (ワープモードのみ, 念のため)
    # if GAME_TYPES[current_game_type_index]["id"] == "warp":
        # draw_warp_portals(screen, warp_portals)    
    if game_id == "warp":
        draw_warp_portals(screen, warp_portals)
        
    # 残り時間を描画
    time_text = score_font.render(f"Time: {remaining_time}", True, WHITE)
    screen.blit(time_text, (10, 10))
    
    # スコアを描画(全モード共通)
    score_display_text = score_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_display_text, (10, 40))
    
# --- ゲームクリア画面の描画 ---
def draw_game_won_screen(screen, maze, player, VISIBILITY_RADIUS, TILE_SIZE, 
                         GREEN, message_font, score_font, score, WIDTH, HEIGHT, WHITE, Instruction_font, YELLOW, game_id):
    """
    ゲームクリア画面を描画

    Parameters
    ----------
    screen : pygame.display
        描画するための pygame.display オブジェクト
    maze : list of lists
        迷路の2次元配列
    player : Player
        プレイヤーのオブジェクト
    TILE_SIZE : int
        1つのタイルのサイズ
    GREEN : tuple of int
        プレイヤーの色
    message_font : pygame.font.Font
        メッセージのフォント
    score_font : pygame.font.Font
        スコアのフォント
    score : int
        スコア
    WIDTH : int
        画面の横幅
    HEIGHT : int
        画面の高さ
    WHITE : tuple of int
        白色
    Instruction_font : pygame.font.Font
        インストラクションのフォント
    YELLOW : tuple of int
        黄色
    game_id : str
        ゲームのID
    """
    # 迷路の描画
    draw_maze(screen, maze, player.x, player.y, max(MAZE_WIDTH, MAZE_HEIGHT))
    # プレイヤーの描画 (点滅状態を含む)
    # pygame.draw.rect(screen, GREEN, (player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    should_draw_player = True
    if player.is_blinking:
        if(pygame.time.get_ticks() // PLAYER_BLINK_INTERVAL_MS) % 2 == 1: # 奇数版での間隔で不表示
            should_draw_player = False
            
    if should_draw_player:
        pygame.draw.rect(screen, GREEN, (player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    # 縁取り線の設定
    outline_color = BLACK # 縁取り線の色
    outline_offset = 1 # 縁取り線の太さ (px)
    
    # ゲームクリアのテキスト(メイン)
    # win_text_content = "You Won!"
    if game_id == "proximity":
        win_text_content = "Challenge Clear!"
    else:
        win_text_content = "You Won!"
        
    # テキストのレンダリング
    win_text_main_surface = message_font.render(win_text_content, True, YELLOW)
    win_rect = win_text_main_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    
    # 縁取りテキストのレンダリング
    win_text_outline_surface = message_font.render(win_text_content, True, outline_color)
    
    # テキストの縁取りを描画
    for dx_outline in [-outline_offset, 0, outline_offset]:
        for dy_outline in [-outline_offset, 0, outline_offset]:
            if dy_outline == 0 and dx_outline == 0:
                continue # 中央の縁取りは描画しない
            screen.blit(win_text_outline_surface, (win_rect.left + dx_outline, win_rect.top + dy_outline))
    
    # メインテキストを描画
    screen.blit(win_text_main_surface, win_rect)
    
    # "Score: {score}" のテキスト
    score_text_content = f"Score: {score}"
    score_text_main_surface = score_font.render(score_text_content, True, WHITE)
    score_rect = score_text_main_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    score_text_outline_surface = score_font.render(score_text_content, True, outline_color)
    for dx_outline in [-outline_offset, 0, outline_offset]:
        for dy_outline in [-outline_offset, 0, outline_offset]:
            if dy_outline == 0 and dx_outline == 0:
                continue
            screen.blit(score_text_outline_surface, (score_rect.left + dx_outline, score_rect.top + dy_outline))
    screen.blit(score_text_main_surface, score_rect)
    
    # "Press Enter to Play, Again"のテキスト
    instruction_text_content = "Press Enter to Play, Again"
    instruction_text_main_surface = Instruction_font.render(instruction_text_content, True, YELLOW)
    instruction_rect = instruction_text_main_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    instruction_text_outline_surface = Instruction_font.render(instruction_text_content, True, outline_color)
    for dx_outline in [-outline_offset, 0, outline_offset]:
        for dy_outline in [-outline_offset, 0, outline_offset]:
            if dy_outline == 0 and dx_outline == 0:
                continue
            screen.blit(instruction_text_outline_surface, (instruction_rect.left + dx_outline, instruction_rect.top + dy_outline))
    screen.blit(instruction_text_main_surface, instruction_rect)
        
# --- ゲームオーバー画面の描画 ---
def draw_game_over_screen(
    screen, maze, player, visibility_radius, TILE_SIZE, GREEN, message_font,
    score_font, instruction_font, WIDTH, HEIGHT, WHITE, RED, DARK_GRAY, BLACK, YELLOW, game_id
    ):
    """
    ゲームオーバー画面を描画する
    
    Parameters
    ----------
    screen : pygame.display
        描画するための pygame.display オブジェクト
    maze : list of lists
        迷路の2次元配列
    player : Player object
        プレイヤーのオブジェクト
    visibility_radius : int
        プレイヤーの視界の半径
    TILE_SIZE : int
        1つのタイルのサイズ
    GREEN : tuple of int
        プレイヤーの色
    message_font : pygame.font.Font
        メッセージのフォント
    score_font : pygame.font.Font
        スコアのフォント
    instruction_font : pygame.font.Font
        インストラクションのフォント
    WIDTH : int
        画面の横幅
    HEIGHT : int
        画面の高さ
    WHITE : tuple of int
        白色
    RED : tuple of int
        赤色
    DARK_GRAY : tuple of int
        濃い灰色
    BLACK : tuple of int
        黒色
    YELLOW : tuple of int
        黄色
    game_id : int
        現在のゲームID
    """
    # 迷路の描画
    draw_maze(screen, maze, player.x, player.y, visibility_radius)
    # プレイヤーの描画
    pygame.draw.rect(screen, GREEN, (player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # メインメッセージの決定・描画
    if game_id == "proximity":
        main_message_text = "Finished!"
    else:
        main_message_text = "Game Over"
    game_over_text_render = message_font.render(main_message_text, True, RED)
    game_over_rect = game_over_text_render.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(game_over_text_render, game_over_rect)
    # スコアの描画
    score_text_render = score_font.render(f"Score: {score}", True, WHITE)
    score_rect = score_text_render.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(score_text_render, score_rect)
    # インストラクションの描画
    instruction_text_render = Instruction_font.render("Press Enter to Play, Again", True, YELLOW)
    instruction_rect = instruction_text_render.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(instruction_text_render, instruction_rect)
    
# --- デモ画面の描画 ---
def draw_demo_screen(
    screen, maze, player, visibility_radius, bonus_items, TILE_SIZE,
    GREEN, score_font, WIDTH, AQUA, current_warp_portals
):
    """
    ゲームデモ画面を描画

    Parameters
    ----------
    screen : pygame.display
        描画するための pygame.display オブジェクト
    maze : list of lists
        迷路の2次元配列
    player : Player
        プレイヤーのオブジェクト
    visibility_radius : int
        プレイヤーの視界の半径
    bonus_items : list of dict
        ボーナスアイテムのリスト
    TILE_SIZE : int
        1つのタイルのサイズ
    GREEN : tuple of int
        プレイヤーの色
    score_font : pygame.font.Font
        スコアのフォント
    WIDTH : int
        画面の横幅
    AQUA : tuple of int
        青色
    current_warp_portals : list of dict
        現在のワープポータルのリスト
    """
    
    game_id_demo_draw = GAME_TYPES[current_game_type_index]["id"] # デモ対象のゲームID
    
    # 迷路の描画
    draw_maze(screen, maze, player.x, player.y, visibility_radius)
    # プレイヤーの描画
    pygame.draw.rect(screen, GREEN, (player.x * TILE_SIZE, player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    # ボーナスアイテムの描画(Probabilityモード以外)
    # for item in bonus_items:
    #     bonus_color = next(b["color"] for b in BONUS_TYPES if b["name"] == item["type"])
    #     pygame.draw.ellipse(screen, bonus_color, (item["x"] * TILE_SIZE, item["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    if game_id_demo_draw != "proximity":
        for item in bonus_items:
            if item.get("active", True):
                # activeキーが存在し = True またはキーが存在しない場合にTrue として扱う
                bonus_color = next((b["color"] for b in BONUS_TYPES if b["name"] == item["type"]), BLACK)
                # 見つからない場合のデフォルト色
                pygame.draw.ellipse(screen, bonus_color, (item["x"] * TILE_SIZE, item["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))            
    
    # ワープポータルの描画(ワープモードのみ)
    # if GAME_TYPES[current_game_type_index]["id"] == "warp":
    #     draw_warp_portals(screen, current_warp_portals)
    if game_id_demo_draw == "warp":
        draw_warp_portals(screen, current_warp_portals)
    
    # メッセージの描画
    demo_text_render = score_font.render("Demo Mode", True, WHITE)
    demo_rect = demo_text_render.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    screen.blit(demo_text_render, demo_rect)
    
    # インストラクションの描画
    Instruction_text_render = Instruction_font.render("Press Enter to Title", True, AQUA)
    Instruction_rect = Instruction_text_render.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
    screen.blit(Instruction_text_render, Instruction_rect)
 
# --- タイトル画面の描画 ---
def draw_title_screen(
    screen, title_font,Instruction_font, score_font, 
    WIDTH, HEIGHT, WHITE, DARK_GRAY, current_gametype_idx
    ):
    """
    タイトル画面を描画

    Parameters
    ----------
    screen : pygame.display
        描画するための pygame.display オブジェクト
    title_font : pygame.font.Font
        タイトルのフォント
    Instruction_font : pygame.font.Font
        インストラクションのフォント
    score_font : pygame.font.Font
        スコアのフォント
    WIDTH : int
        画面の横幅
    HEIGHT : int
        画面の高さ
    WHITE : tuple of int
        白色
    DARK_GRAY : tuple of int
        濃い灰色
    current_gametype_idx : int
        現在のゲームタイプのインデックス
    """
    # タイトルy座標
    title_y = HEIGHT // 2 - 150 # タイトルのy座標
    title_text_render = title_font.render("Maze Game", True, WHITE) # タイトルを描画
    title_rect = title_text_render.get_rect(center=(WIDTH // 2, title_y)) # タイトルを中央に配置
    screen.blit(title_text_render, title_rect) # タイトルを描画
    # ゲームタイプy座標とステップ
    gametype_start_y = title_y + 80 # ゲームタイプのy座標
    game_type_step = 50 # ゲームタイプ間y座標の間隔
    for i, game_type in enumerate(GAME_TYPES): # ゲームタイプを描画
        text_color = YELLOW if i == current_gametype_idx else WHITE # 現在のゲームタイプの色
        type_text = Instruction_font.render(game_type["name"], True, text_color) # 辞書からnameの値を取得
        current_gametype_y = gametype_start_y + i * game_type_step # 現在のゲームタイプのy座標
        type_rect = type_text.get_rect(center=(WIDTH // 2, current_gametype_y)) # ゲームタイプを中央に配置
        screen.blit(type_text, type_rect) # ゲームタイプを描画
    # "Press Enter to Start"
    instruction_y = gametype_start_y + len(GAME_TYPES) * game_type_step + 60 # インストラクションのy座標
    instruction_text_render = Instruction_font.render("Press Enter to Start Game", True, WHITE) # インストラクションを描画
    instruction_rect_render = instruction_text_render.get_rect(center=(WIDTH // 2, instruction_y)) # インストラクションを中央に配置
    screen.blit(instruction_text_render, instruction_rect_render) # インストラクションを描画
    
    # クレジット
    credit_y = instruction_y + 50 # クレジットのy座標
    credit_text_render = score_font.render("Arrow keys to move, H to help, Esc to quit", True, DARK_GRAY)# クレジットを描画
    credit_rect_render = credit_text_render.get_rect(center=(WIDTH // 2, credit_y)) # クレジットを中央に配置
    screen.blit(credit_text_render, credit_rect_render) # クレジットを描画
    
# --- ボーナスアイテムの初期化 ---
def initialize_bonus_items():
    """
    ボーナスアイテムの初期化
    
    Parameters
    ----------
    None
    
    returns
    -------
    None
    """
    # main関数で初期化するため、グローバル変数にする
    global bonus_items, maze, player_start_x, player_start_y, goal_x, goal_y, player, current_game_type_index
    bonus_items.clear()
    
    # Proximityゲームタイプではボーナスアイテムを初期化しない
    if GAME_TYPES[current_game_type_index]["id"] == "proximity":
        return
    
    now = pygame.time.get_ticks() # 現在の時刻
    
    # ボーナスアイテムの配置
    for bonus_type_info in BONUS_TYPES: # ボーナスアイテムの種類を取得
        for _ in range(bonus_type_info.get("count", 0)): # ボーナスアイテムの数を取得
            placed_successfully = False # 配置成功フラグ
            for attempt in range(100): # 100回試行
                bx = random.randint(0, MAZE_WIDTH - 1) # x座標をランダムに生成
                by = random.randint(0, MAZE_HEIGHT - 1) # y座標をランダムに生成
                
                # ボーナスアイテムの配置
                # ボーナスアイテムの配置可能なマスかどうか(プレイヤーとゴールの座標を除く)
                if maze[by][bx] == "Path" and\
                    (bx != player_start_x or by != player_start_y) and\
                    (bx != goal_x or by != goal_y) and\
                    all(not (existing_item["x"] == bx and existing_item["y"] == by) for existing_item in bonus_items):
                    # ボーナスアイテムを追加
                    bonus_items.append({
                        "x": bx,
                        "y": by,
                        "type": bonus_type_info["name"],
                        "next_move_time": now + random.randint(1, BONUS_MOVE_INTERVAL) * 1000,
                        "active": True
                        })
                    # 配置成功フラグ
                    placed_successfully = True
                    break
                
            if not placed_successfully: # 配置に失敗した場合
                print(f"Failed to place bonus item for type {bonus_type_info['name']} after 100 attempts.")

# --- ワープ入口の初期化 ---
def initialize_warp_portals():
    """
    ワープ入口を初期化
    
    ワープ入口の配置を行う。ワープ入口の数は、NUM_WARP_PORTALSで指定される。
    ワープ入口は、迷路のPathセルに配置される。プレイヤーのスタート位置、ゴール位置、ボーナスアイテムの位置は避ける。
    
    Parameters
    ----------
    None
    
    returns
    -------
    None
    """
    global warp_portals, maze, player_start_x, player_start_y, goal_x, goal_y, current_game_type_index
    warp_portals.clear()
    # ワープモード以外では実行しない(Proximityモードも含む)
    if GAME_TYPES[current_game_type_index]["id"] != "warp":
        return

    occupied_coords = set([(player_start_x, player_start_y), (goal_x, goal_y)])
    # ボーナスアイテムの位置も避ける
    for item in bonus_items:
        occupied_coords.add((item["x"], item["y"]))

    for _ in range(NUM_WARP_PORTALS):
        placed_successfully = False
        for attempt in range(100): # 配置試行回数
            px = random.randint(0, MAZE_WIDTH - 1)
            py = random.randint(0, MAZE_HEIGHT - 1)
            if maze[py][px] == "Path" and (px, py) not in occupied_coords:
                # ワープ入口を新しく配置
                warp_portals.append({"x": px, "y": py})
                occupied_coords.add((px,py)) # 新しく配置したポータルの位置も占有リストに追加
                placed_successfully = True
                break
        if not placed_successfully:
            print(f"Failed to place a warp portal after 100 attempts.")

# --- ワープ入口の描画 ---
def draw_warp_portals(screen, current_warp_portals):
    """
    ワープ入口を描画
    
    Parameters
    ----------
    screen : pygame.display
        描画するための pygame.display オブジェクト
    current_warp_portals : list
        現在のワープ入口のリスト
    
    returns
    -------
    None
    """
    for portal in current_warp_portals: # ワープ入口を描画
        # 外側の矩形を描画
        pygame.draw.rect(screen, AQUA, (portal["x"] * TILE_SIZE, portal["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # 内側に少し小さい円を描画して入口っぽさを出す
        inner_radius = TILE_SIZE // 3
        # 内側の円を描画
        pygame.draw.circle(screen, BLACK, (portal["x"] * TILE_SIZE + TILE_SIZE // 2, portal["y"] * TILE_SIZE + TILE_SIZE // 2), inner_radius)

# --- ワープ処理 ---
def handle_warp_portal_collision():
    """
    ワープ入口の衝突処理
    
    Parameters
    ----------
    None
    
    returns
    -------
    None
    """
    global player, warp_portals, maze
    # ワープ入口にプレイヤーが衝突した場合
    for portal in warp_portals:
        if player.x == portal["x"] and player.y == portal["y"]:
            # ワープ可能な座標を探す
            possible_warp_spots = []
            for r_idx, row_val in enumerate(maze):
                for c_idx, cell_val in enumerate(row_val):
                    if cell_val == "Path" and not (c_idx == player.x and r_idx == player.y) and not (c_idx == goal_x and r_idx == goal_y) and not any(p["x"] == c_idx and p["y"] == r_idx for p in warp_portals if p is not portal):
                        possible_warp_spots.append((c_idx, r_idx))
            # ワープ可能な座標があったら、プレイヤーの座標をランダムに変更
            if possible_warp_spots:
                player.x, player.y = random.choice(possible_warp_spots)
                # 点滅開始
                player.is_blinking = True
                player.blink_end_time = pygame.time.get_ticks() + PLAYER_BLINK_DURATION_SECONDS * 1000
            break # 1フレームで1回だけワープ
                
# --- ゲーム状態のリセット ---
def reset_game_state_for_playing():
    """
    ゲーム状態のリセット
    
    Parameters
    ----------
    None
    
    returns
    -------
    None
    """
    global player, start_time, remaining_time, game_won, game_over, score, player_start_x, player_start_y
    global maze, goal_x, goal_y
    
    maze, player_start_x, player_start_y = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
    goal_x, goal_y = MAZE_WIDTH - 1, MAZE_HEIGHT - 1
    maze[goal_y][goal_x] = "Goal" # 迷路のコールを設定
    player.x = player_start_x
    player.y = player_start_y
    player.is_blinking = False # 点滅状態をリセット
    player.blink_end_time = 0 # 点滅終了時刻をリセット
    start_time = pygame.time.get_ticks()
    # 選択されたゲームタイプの制限時間
    remaining_time = GAME_TYPES[current_game_type_index]["time_limit"] 
    game_won = False
    game_over = False
    score = 0
    
    initialize_bonus_items() # ボーナスアイテム初期化
    initialize_warp_portals() # ワープポータル初期化

# --- デモ状態のリセット ---
def reset_demo_state():
    """
    デモ状態のリセット
    
    Parameters
    ----------
    None
    
    returns
    -------
    None
    """
    global player, demo_direction_timer, demo_direction, player_start_x, player_start_y
    global maze, goal_x, goal_y # 迷路とゴールもリセット時に再設定
    
    maze, player_start_x, player_start_y = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
    goal_x, goal_y = MAZE_WIDTH - 1, MAZE_HEIGHT - 1
    maze[goal_y][goal_x] = "Goal"
    player.x = player_start_x
    player.y = player_start_y
    player.is_blinking = False # 点滅状態をリセット
    player.blink_end_time = 0 # 点滅終了時刻をリセット
    demo_direction_timer = pygame.time.get_ticks()
    demo_direction = (0, 0)
    
    initialize_bonus_items()
    initialize_warp_portals() # デモでもワープポータルを初期化

# --- メインループ ---
def main():
    """
    メインループ
    
    Parameters
    ----------
    None
    
    returns
    -------
    None
    """
    global screen, message_font, score_font, title_font, Instruction_font, clock, player
    global maze, player_start_x, player_start_y, goal_x, goal_y # main関数で初期化するため、グローバル変数にする

    # --- ゲームの初期化 ---
    screen, message_font, score_font, title_font, Instruction_font, clock = initialize_game()

    # --- 迷路の生成 ---
    # MAZE_WIDTHなどは固定値なので直接迷路生成
    maze, player_start_x, player_start_y = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)

    # --- 迷路のゴールの設定 ---
    # 迷路データが空でないことを確認
    if MAZE_HEIGHT > 0 and MAZE_WIDTH > 0 and maze:
        goal_x, goal_y = MAZE_WIDTH - 1, MAZE_HEIGHT - 1
        maze[goal_y][goal_x] = "Goal" # 迷路のコールを設定
    
    # --- プレイヤーの生成 (念のため) ---
    # player = Player(player_start_x, player_start_y)

    # --- ゲームのメインループ ---
    game_loop()

# --- エントリーポイント ---
if __name__ == "__main__":
    main()
