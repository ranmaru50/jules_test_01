# roguelike_rpg/domain/tile.py
"""
マップタイルに関する定義
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tile:
    """
    マップ上の1タイルを表す不変のオブジェクト（値オブジェクト）。
    歩行可能か、視線を透過するかといったゲームロジック上の特性と、
    基本的な見た目の情報を保持する。

    Attributes:
        walkable (bool): このタイルが歩行可能かどうか。
        transparent (bool): このタイルが視線を透過するかどうか。
        char (str): タイルを表す文字。
        color (tuple[int, int, int]): タイルの文字色 (R, G, B)。
    """

    walkable: bool
    transparent: bool
    char: str
    color: tuple[int, int, int]


# 床タイルの定義
# 歩行可能で、視線も通す
FLOOR_TILE = Tile(walkable=True, transparent=True, char=".", color=(150, 150, 150))

# 壁タイルの定義
# 歩行不可能で、視線も遮る
WALL_TILE = Tile(walkable=False, transparent=False, char="#", color=(220, 220, 220))
