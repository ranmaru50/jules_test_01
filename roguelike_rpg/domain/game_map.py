# roguelike_rpg/domain/game_map.py
"""
ゲームマップの状態を管理するクラス
"""

from __future__ import annotations

import numpy as np

from .tile import WALL_TILE


class GameMap:
    """
    ゲームマップのタイル情報と、マップ上のエンティティを管理する。

    Attributes:
        width (int): マップの幅。
        height (int): マップの高さ。
        tiles (np.ndarray): マップのタイル情報を格納する2次元配列。
    """

    def __init__(self, width: int, height: int):
        # 引数の型を明示
        self.width = width
        self.height = height
        # 指定された幅と高さで、壁タイルで満たされた2次元配列を初期化
        self.tiles: np.ndarray[np.object_] = np.full(
            (width, height), fill_value=WALL_TILE, order="F"
        )

    def in_bounds(self, x: int, y: int) -> bool:
        """
        指定された座標がマップの範囲内にあるかを判定する。

        Args:
            x (int): チェックするx座標。
            y (int): チェックするy座標。

        Returns:
            bool: 座標がマップの範囲内であればTrue、そうでなければFalse。
        """
        # 座標が0以上かつ、マップの幅・高さ未満であるかを確認
        return 0 <= x < self.width and 0 <= y < self.height
