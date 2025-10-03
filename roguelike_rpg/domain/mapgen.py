# roguelike_rpg/domain/mapgen.py
"""
ダンジョンマップを生成するためのロジック
"""

from . import tile
from .game_map import GameMap


def generate_map(map_width: int, map_height: int) -> GameMap:
    """
    新しいゲームマップを生成する。
    現時点では、壁に囲まれた空の部屋を一つだけ生成する。

    Args:
        map_width (int): 生成するマップの幅。
        map_height (int): 生成するマップの高さ。

    Returns:
        GameMap: 生成されたゲームマップオブジェクト。
    """
    # 指定された幅と高さでGameMapを初期化
    dungeon = GameMap(map_width, map_height)

    # シンプルな長方形の部屋を作成
    # マップの端から1タイル内側に床を配置する
    room_x_start = 1
    room_y_start = 1
    room_x_end = map_width - 2
    room_y_end = map_height - 2

    # 部屋の中を床タイルで埋める
    # numpyのスライス機能を使って効率的にタイルを配置
    dungeon.tiles[room_x_start : room_x_end + 1, room_y_start : room_y_end + 1] = (
        tile.FLOOR_TILE
    )

    # TODO: より複雑なダンジョン生成アルゴリズム（例：複数の部屋と通路）を実装する

    return dungeon
