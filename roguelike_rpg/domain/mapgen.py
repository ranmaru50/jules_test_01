# roguelike_rpg/domain/mapgen.py
"""
ダンジョンマップを生成するためのロジック
"""

import random
from typing import Any

from . import tile
from .ecs.world import World
from .factories import create_enemy
from .game_map import GameMap


def generate_map(
    world: World,
    map_width: int,
    map_height: int,
    max_enemies_per_room: int,
    enemy_data: dict[str, Any],
) -> GameMap:
    """
    新しいゲームマップを生成し、敵を配置する。
    現時点では、壁に囲まれた空の部屋を一つだけ生成する。

    Args:
        world (World): エンティティを追加するワールドオブジェクト。
        map_width (int): 生成するマップの幅。
        map_height (int): 生成するマップの高さ。
        max_enemies_per_room (int): 1部屋に配置する敵の最大数。
        enemy_data (dict[str, Any]): 敵の種類と特性を定義したデータ。

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
    dungeon.tiles[room_x_start : room_x_end + 1, room_y_start : room_y_end + 1] = (
        tile.FLOOR_TILE
    )

    # 敵を配置する
    place_enemies(dungeon, world, max_enemies_per_room, enemy_data)

    # TODO: より複雑なダンジョン生成アルゴリズム（例：複数の部屋と通路）を実装する

    return dungeon


def place_enemies(
    dungeon: GameMap,
    world: World,
    max_enemies_per_room: int,
    enemy_data: dict[str, Any],
) -> None:
    """
    部屋のランダムな位置に敵を配置する。

    Args:
        dungeon (GameMap): 敵を配置する対象のマップ。
        world (World): エンティティを追加するワールドオブジェクト。
        max_enemies_per_room (int): 1部屋に配置する敵の最大数。
        enemy_data (dict[str, Any]): 敵の種類と特性を定義したデータ。
    """
    # 部屋の中の歩行可能なタイルを取得
    floor_tiles = []
    for x in range(1, dungeon.width - 1):
        for y in range(1, dungeon.height - 1):
            # TODO: プレイヤーの初期位置と重ならないようにする
            if dungeon.tiles[x, y] == tile.FLOOR_TILE:
                floor_tiles.append((x, y))

    # 配置する敵の数をランダムに決定
    number_of_enemies = random.randint(0, max_enemies_per_room)
    # 敵の種類リスト
    enemy_types = list(enemy_data.keys())

    for _ in range(number_of_enemies):
        if not floor_tiles:
            break  # 配置できる場所がなければ終了

        # ランダムな位置を選択
        x, y = random.choice(floor_tiles)
        # その位置を候補から削除（同じ場所には配置しない）
        floor_tiles.remove((x, y))

        # ランダムな敵の種類を選択
        enemy_type_key = random.choice(enemy_types)

        # 敵を生成
        create_enemy(world, x, y, enemy_data[enemy_type_key])
