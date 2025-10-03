# roguelike_rpg/main.py
"""
ゲームのメインエントリーポイント
"""

from roguelike_rpg.application.game_loop import GameLoop
from roguelike_rpg.presentation.dungeon_renderer import DungeonRenderer

# 定数定義
MAP_WIDTH = 80
MAP_HEIGHT = 24


def main() -> None:
    """
    ゲームを初期化し、メインループを開始する。
    """
    # 1. ゲームループとレンダラーを初期化
    game_loop = GameLoop(MAP_WIDTH, MAP_HEIGHT)
    renderer = DungeonRenderer(game_loop.game_map, game_loop.world)

    # 2. アクションと移動量のマッピング
    # プレイヤーからの入力を、(dx, dy)の移動ベクトルに変換する
    action_map = {
        "w": (0, -1),  # 上
        "s": (0, 1),  # 下
        "a": (-1, 0),  # 左
        "d": (1, 0),  # 右
    }

    # 3. ゲームのメインループ
    while game_loop.running:
        # a. 画面を描画
        renderer.render()

        # b. ユーザーからの入力を待つ
        # FIXME: 現在はEnterキー入力が必要。よりインタラクティブな入力方式に改善する。
        action = input("> ").lower()

        # c. 入力を処理
        if action == "q":
            # 'q'が入力されたらゲームを終了
            game_loop.running = False
        elif action in action_map:
            # マップされたアクション（移動）を実行
            dx, dy = action_map[action]
            game_loop.handle_player_action(dx, dy)
        else:
            # 未定義のキーが入力された場合は何もしない
            print("無効なキーです。")


if __name__ == "__main__":
    main()
