# tests/test_domain/test_mapgen.py
"""
マップ生成ロジックのテスト
"""

import pytest

from roguelike_rpg.domain.ecs.world import World
from roguelike_rpg.domain.game_map import GameMap
from roguelike_rpg.domain.mapgen import generate_map
from roguelike_rpg.domain.tile import FLOOR_TILE, WALL_TILE


@pytest.fixture
def generated_map() -> GameMap:
    """
    テスト用のマップを生成するフィクスチャ
    """
    # generate_mapの新しいシグネチャに合わせて引数を追加
    world = World()
    enemy_data = {}  # このテストでは敵データは不要
    item_data = {}  # このテストではアイテムデータは不要
    game_map, _player_start_pos = generate_map(
        world=world,
        map_width=20,
        map_height=10,
        max_enemies_per_room=0,  # 敵は配置しない
        max_items_per_room=0,  # アイテムは配置しない
        enemy_data=enemy_data,
        item_data=item_data,
    )
    return game_map


def test_generate_map_creates_correct_size(generated_map: GameMap):
    """
    生成されたマップが正しいサイズを持つかテストする。
    """
    # Act & Assert
    assert generated_map.width == 20
    assert generated_map.height == 10


def test_generate_map_has_walls_on_border(generated_map: GameMap):
    """
    生成されたマップの外周が壁であるかテストする。
    """
    # Act & Assert
    # 上下の境界線
    for x in range(generated_map.width):
        assert generated_map.tiles[x, 0] is WALL_TILE
        assert generated_map.tiles[x, generated_map.height - 1] is WALL_TILE

    # 左右の境界線
    for y in range(generated_map.height):
        assert generated_map.tiles[0, y] is WALL_TILE
        assert generated_map.tiles[generated_map.width - 1, y] is WALL_TILE


def test_generate_map_has_floor_in_interior(generated_map: GameMap):
    """
    生成されたマップの内部が床であるかテストする。
    """
    # Act & Assert
    # 内部（境界線を除く）のタイルをチェック
    for x in range(1, generated_map.width - 1):
        for y in range(1, generated_map.height - 1):
            assert generated_map.tiles[x, y] is FLOOR_TILE
