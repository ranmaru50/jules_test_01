# roguelike_rpg/application/game_state.py
"""
ゲームの状態を定義する列挙型
"""

from enum import Enum, auto


class GameState(Enum):
    """
    ゲームの現在の状態を示す列挙型。
    この状態に応じて、プレイヤーの入力がどのように処理されるかが決まる。
    """

    PLAYERS_TURN = auto()  # プレイヤーの行動待ち
    ENEMY_TURN = auto()  # 敵の行動中
    SHOW_INVENTORY = auto()  # インベントリ表示中
    DROP_INVENTORY = auto()  # アイテムを捨てる選択中
    GAME_OVER = auto()  # ゲームオーバー画面
    # TODO: アイテム使用選択、レベルアップ画面などの状態を追加する
