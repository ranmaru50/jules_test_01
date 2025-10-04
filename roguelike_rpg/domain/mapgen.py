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
    dungeon_level: int,
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

    # 敵とアイテムを配置
    place_enemies(world, max_enemies_per_room, enemy_data, spawnable_tiles)
    place_items(world, max_items_per_room, item_data, spawnable_tiles)

    # 最終フロアかどうかで階段か宝物を配置
    if dungeon_level == 20:
        place_treasure(world, item_data, spawnable_tiles)
    else:
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
    # 宝物を除くアイテムカテゴリのリストを作成
    item_categories = [key for key in item_data.keys() if key != "treasure"]

    if not item_categories:
        return

    for _ in range(number_of_items):
        if not spawnable_tiles:
            break

        # ランダムなカテゴリと、その中のランダムなアイテムを選択
        random_category_key = random.choice(item_categories)
        category_items = item_data[random_category_key]
        random_item_key = random.choice(list(category_items.keys()))
        item_to_place = category_items[random_item_key]

        x, y = random.choice(spawnable_tiles)
        spawnable_tiles.remove((x, y))

        create_item(world, x, y, item_to_place)


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


def place_treasure(
    world: World,
    item_data: dict[str, Any],
    spawnable_tiles: List[tuple[int, int]],
) -> None:
    """
    部屋のランダムな位置に宝物を配置する。
    """
    if not spawnable_tiles:
        return

    x, y = random.choice(spawnable_tiles)
    spawnable_tiles.remove((x, y))
    # 'treasure'カテゴリから'amulet_of_yendor'を探して配置
    treasure_data = item_data.get("treasure", {}).get("amulet_of_yendor")
    if treasure_data:
        create_item(world, x, y, treasure_data)
