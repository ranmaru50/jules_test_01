# roguelike_rpg/application/enemy_ai_service.py
"""
敵AIの行動を決定するアプリケーションサービス
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from roguelike_rpg.application.services import attack, get_blocking_enemy_at
from roguelike_rpg.domain.ecs.components import (
    ConfusionComponent,
    NameComponent,
    PositionComponent,
)
from roguelike_rpg.domain.pathfinding import astar

if TYPE_CHECKING:
    from roguelike_rpg.domain.ecs.world import Entity, World
    from roguelike_rpg.domain.game_map import GameMap


def process_enemy_turn(
    world: "World", enemy: "Entity", player: "Entity", game_map: "GameMap"
) -> list[str]:
    """
    一体の敵のターンを処理し、行動を実行する。
    混乱している場合は、ランダムに移動する。
    """
    logs = []
    enemy_pos = world.get_component(enemy, PositionComponent)
    player_pos = world.get_component(player, PositionComponent)
    enemy_name = world.get_component(enemy, NameComponent)

    if not enemy_pos or not player_pos or not enemy_name:
        return logs

    # 混乱状態の処理
    confusion = world.get_component(enemy, ConfusionComponent)
    if confusion:
        confusion.duration -= 1
        if confusion.duration <= 0:
            world.remove_component(enemy, ConfusionComponent)
            logs.append(f"{enemy_name.name}は正気に戻った！")
            return logs
        else:
            # ランダムな方向に移動
            dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
            dest_x, dest_y = enemy_pos.x + dx, enemy_pos.y + dy
            if (
                game_map.in_bounds(dest_x, dest_y)
                and game_map.tiles[dest_x, dest_y].walkable
            ):
                if not get_blocking_enemy_at(world, dest_x, dest_y):
                    enemy_pos.x = dest_x
                    enemy_pos.y = dest_y
            logs.append(f"{enemy_name.name}は混乱してよろめいている。")
            return logs

    # 通常のAI処理
    # 視界の範囲
    SIGHT_RADIUS = 8
    # プレイヤーとの距離を計算（チェビシェフ距離）
    distance = max(abs(enemy_pos.x - player_pos.x), abs(enemy_pos.y - player_pos.y))

    # プレイヤーが視界外なら何もしない
    if distance > SIGHT_RADIUS:
        return logs

    # プレイヤーが隣接している場合、攻撃する
    if distance <= 1.5:  # 8方向隣接
        logs.extend(attack(world, enemy, player))
        return logs

    # プレイヤーが視界内にいる場合、追跡する
    # A*でプレイヤーへの経路を探索
    path = astar(
        game_map,
        start=(enemy_pos.x, enemy_pos.y),
        end=(player_pos.x, player_pos.y),
        # 移動コスト：歩けるなら1、無理なら無限大
        cost_func=lambda x, y: 1.0 if game_map.tiles[x, y].walkable else float("inf"),
    )

    # 経路が見つかり、移動可能な場合
    if path and len(path) > 1:
        next_x, next_y = path[1]  # 経路の次のステップ

        # 次のステップに他の敵がいないか確認
        if get_blocking_enemy_at(world, next_x, next_y):
            # 誰かがいるなら、このターンは待機
            return logs

        # 誰もいなければ移動する
        enemy_pos.x = next_x
        enemy_pos.y = next_y

    return logs
