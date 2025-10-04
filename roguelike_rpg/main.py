# roguelike_rpg/main.py
"""
ゲームのメインエントリーポイント
"""

from roguelike_rpg.application.game_loop import GameLoop
from roguelike_rpg.application.game_state import GameState
from roguelike_rpg.presentation.dungeon_renderer import DungeonRenderer
from roguelike_rpg.presentation.end_screen import (
    render_game_over_screen,
    render_victory_screen,
)
from roguelike_rpg.presentation.inventory_screen import render_inventory_screen

# 定数定義
MAP_WIDTH = 80
MAP_HEIGHT = 20  # UI領域のために高さを調整
UI_HEIGHT = 5


def main() -> None:
    """
    ゲームを初期化し、メインループを開始する。
    """
    # 1. ゲームループとレンダラーを初期化
    game_loop = GameLoop(MAP_WIDTH, MAP_HEIGHT)
    renderer = DungeonRenderer(
        game_map=game_loop.game_map,
        world=game_loop.world,
        message_log=game_loop.message_log,
        player_entity=game_loop.player,
        dungeon_level=game_loop.dungeon_level,
    )
    renderer.ui_height = UI_HEIGHT

    # 2. ゲームのメインループ
    while True:
        # a. レンダラーの情報を最新の状態に更新
        renderer.dungeon_level = game_loop.dungeon_level
        renderer.targeting_cursor = game_loop.targeting_cursor

        # b. 現在のゲーム状態に応じて画面を描画
        if game_loop.game_state == GameState.VICTORY:
            render_victory_screen(game_loop)
            break  # ゲーム終了
        elif game_loop.game_state == GameState.GAME_OVER:
            render_game_over_screen(game_loop)
            break  # ゲーム終了
        elif game_loop.game_state == GameState.SHOW_INVENTORY:
            render_inventory_screen(world=game_loop.world, player=game_loop.player)
        else:  # PLAYERS_TURN, ENEMY_TURN
            renderer.render()

        # c. ユーザーからの入力を待つ
        # FIXME: 現在はEnterキー入力が必要。よりインタラクティブな入力方式に改善する。
        action = input("> ").lower()

        # d. 'q'が押されたらゲーム終了
        if action == "q" and game_loop.game_state == GameState.PLAYERS_TURN:
            break

        # e. GameLoopにキー入力を渡して処理させる
        game_loop.process_input(action)


if __name__ == "__main__":
    main()
