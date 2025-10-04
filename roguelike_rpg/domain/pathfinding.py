# roguelike_rpg/domain/pathfinding.py
"""
A*（エースター）経路探索アルゴリズム
"""

from __future__ import annotations

import heapq
from typing import TYPE_CHECKING, Callable, List, Optional, Tuple

if TYPE_CHECKING:
    from .game_map import GameMap

# タプル (cost, x, y) を表す型エイリアス
Node = Tuple[float, int, int]


def astar(
    game_map: "GameMap",
    start: Tuple[int, int],
    end: Tuple[int, int],
    cost_func: Callable[[int, int], float],
) -> Optional[List[Tuple[int, int]]]:
    """
    A*アルゴリズムを用いて、startからendまでの最短経路を計算する。

    Args:
        game_map (GameMap): 経路探索を行う対象のマップ。
        start (Tuple[int, int]): 開始座標 (x, y)。
        end (Tuple[int, int]): 目的地の座標 (x, y)。
        cost_func (Callable[[int, int], float]): 指定された座標の移動コストを返す関数。
                                                歩行不可能な場合は無限大(float('inf'))を返す。

    Returns:
        Optional[List[Tuple[int, int]]]: 経路のリスト(startからend)。
                                        経路が見つからない場合はNone。
    """
    # 開いているノードの優先度付きキュー
    open_nodes: List[Node] = [(0, start[0], start[1])]
    # 閉じたノードのセット
    closed_nodes = set()
    # 経路を再構築するための辞書
    came_from = {}
    # g_score: スタートから各ノードまでの実際のコスト
    g_score = {start: 0}

    while open_nodes:
        # 最もf_scoreが低いノードを取り出す
        current_f, current_x, current_y = heapq.heappop(open_nodes)

        # 目的地に到達した場合、経路を再構築して返す
        if (current_x, current_y) == end:
            path = []
            curr = end
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            return path[::-1]

        closed_nodes.add((current_x, current_y))

        # 隣接ノードを探索 (8方向)
        for dx, dy in [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]:
            neighbor_x, neighbor_y = current_x + dx, current_y + dy

            if not game_map.in_bounds(neighbor_x, neighbor_y):
                continue

            if (neighbor_x, neighbor_y) in closed_nodes:
                continue

            move_cost = cost_func(neighbor_x, neighbor_y)
            if move_cost == float("inf"):
                continue

            # 新しいg_scoreを計算
            tentative_g_score = g_score[(current_x, current_y)] + move_cost

            if (neighbor_x, neighbor_y) not in g_score or tentative_g_score < g_score[
                (neighbor_x, neighbor_y)
            ]:
                # より良い経路が見つかった場合
                g_score[(neighbor_x, neighbor_y)] = tentative_g_score
                # f_score = g_score + heuristic
                heuristic_cost = max(
                    abs(neighbor_x - end[0]), abs(neighbor_y - end[1])
                )  # チェビシェフ距離
                f_score = tentative_g_score + heuristic_cost
                heapq.heappush(open_nodes, (f_score, neighbor_x, neighbor_y))
                came_from[(neighbor_x, neighbor_y)] = (current_x, current_y)

    # 経路が見つからなかった場合
    return None
