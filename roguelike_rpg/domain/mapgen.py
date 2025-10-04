# roguelike_rpg/domain/mapgen.py
"""
ダンジョンマップを生成するためのロジック
"""

import random
from typing import Any, List, Tuple

from . import tile
from .ecs.world import World
from .factories import create_enemy, create_item, create_stairs
from .game_map import GameMap


def generate_map(
    world: World,
    map_width: int,
    map_height: int,
    max_enemies_per_room: int,
    max_items_per_room: int,
    enemy_data: dict[str, Any],
    item_data: dict[str, Any],
) -> Tuple[GameMap, Tuple[int, int]]:
    """
    新しいゲームマップを生成し、敵とアイテムを配置する。
    戻り値として、生成されたマップとプレイヤーの安全な開始座標を返す。
    """
    dungeon = GameMap(map_width, map_height)

    # シンプルな長方形の部屋を作成
    room_x_start = 1
    room_y_start = 1
    room_x_end = map_width - 2
    room_y_end = map_height - 2
    dungeon.tiles[room_x_start : room_x_end + 1, room_y_start : room_y_end + 1] = (
        tile.FLOOR_TILE
    )

    # 部屋の中の歩行可能なタイルを取得
    spawnable_tiles: List[tuple[int, int]] = []
    for x in range(room_x_start + 1, room_x_end):
        for y in range(room_y_start + 1, room_y_end):
            spawnable_tiles.append((x, y))

    # プレイヤーの開始位置を決定し、配置候補から削除
    player_start_pos = random.choice(spawnable_tiles)
    spawnable_tiles.remove(player_start_pos)

    # 敵とアイテム、階段を配置
    place_enemies(world, max_enemies_per_room, enemy_data, spawnable_tiles)
    place_items(world, max_items_per_room, item_data, spawnable_tiles)
    place_stairs(world, spawnable_tiles)

    # TODO: より複雑なダンジョン生成アルゴリズム（例：複数の部屋と通路）を実装する

    return dungeon, player_start_pos


def place_enemies(
    world: World,
    max_enemies_per_room: int,
    enemy_data: dict[str, Any],
    spawnable_tiles: List[tuple[int, int]],
) -> None:
    """
    部屋のランダムな位置に敵を配置する。配置したタイルはリストから削除される。
    """
    number_of_enemies = random.randint(0, max_enemies_per_room)
    enemy_types = list(enemy_data.keys())

    for _ in range(number_of_enemies):
        if not spawnable_tiles:
            break

        x, y = random.choice(spawnable_tiles)
        spawnable_tiles.remove((x, y))

        enemy_type_key = random.choice(enemy_types)
        create_enemy(world, x, y, enemy_data[enemy_type_key])


def place_items(
    world: World,
    max_items_per_room: int,
    item_data: dict[str, Any],
    spawnable_tiles: List[tuple[int, int]],
) -> None:
    """
    部屋のランダムな位置にアイテムを配置する。配置したタイルはリストから削除される。
    """
    number_of_items = random.randint(0, max_items_per_room)
    item_types = list(item_data.keys())

    for _ in range(number_of_items):
        if not spawnable_tiles:
            break

        x, y = random.choice(spawnable_tiles)
        spawnable_tiles.remove((x, y))

        item_type_key = random.choice(item_types)
        create_item(world, x, y, item_data[item_type_key])


def place_stairs(
    world: World,
    spawnable_tiles: List[tuple[int, int]],
) -> None:
    """
    部屋のランダムな位置に階段を配置する。
    """
    if not spawnable_tiles:
        return

    x, y = random.choice(spawnable_tiles)
    spawnable_tiles.remove((x, y))
    create_stairs(world, x, y)
