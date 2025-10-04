# tests/test_application/test_enemy_ai_service.py
"""
敵AIサービスのテスト
"""

import math

import pytest

from roguelike_rpg.application.enemy_ai_service import process_enemy_turn
from roguelike_rpg.domain.ecs.components import HealthComponent, PositionComponent
from roguelike_rpg.domain.ecs.world import World
from roguelike_rpg.domain.factories import create_enemy, create_player
from roguelike_rpg.domain.game_map import GameMap
from roguelike_rpg.domain.tile import FLOOR_TILE, WALL_TILE


@pytest.fixture
def ai_setup():
    """AIテスト用の環境をセットアップするフィクスチャ"""
    world = World()
    game_map = GameMap(width=20, height=20)
    game_map.tiles[:, :] = FLOOR_TILE
    player = create_player(world, 10, 10)
    enemy_data = {
        "name": "Goblin",
        "char": "g",
        "fg_color": [0, 255, 0],
        "max_hp": 10,
        "defense": 0,
        "power": 3,
    }
    enemy = create_enemy(world, 10, 5, enemy_data)
    return world, game_map, player, enemy


def test_enemy_does_nothing_if_player_out_of_sight(ai_setup):
    """プレイヤーが視界外の場合、敵が何もしないことをテストする。"""
    world, game_map, player, enemy = ai_setup
    # プレイヤーを視界外(SIGHT_RADIUS=8)に移動
    player_pos = world.get_component(player, PositionComponent)
    player_pos.x, player_pos.y = 0, 0

    enemy_pos_before = world.get_component(enemy, PositionComponent)
    enemy_x_before, enemy_y_before = enemy_pos_before.x, enemy_pos_before.y

    logs = process_enemy_turn(world, enemy, player, game_map)

    enemy_pos_after = world.get_component(enemy, PositionComponent)
    assert enemy_pos_after.x == enemy_x_before
    assert enemy_pos_after.y == enemy_y_before
    assert not logs


def test_enemy_moves_towards_player_if_in_sight(ai_setup):
    """プレイヤーが視界内の場合、敵がプレイヤーに近づくことをテストする。"""
    world, game_map, player, enemy = ai_setup
    enemy_pos_before = world.get_component(enemy, PositionComponent)
    player_pos = world.get_component(player, PositionComponent)

    # AI処理前の距離を計算
    dist_before = math.sqrt(
        (enemy_pos_before.x - player_pos.x) ** 2
        + (enemy_pos_before.y - player_pos.y) ** 2
    )

    logs = process_enemy_turn(world, enemy, player, game_map)

    enemy_pos_after = world.get_component(enemy, PositionComponent)
    # AI処理後の距離を計算
    dist_after = math.sqrt(
        (enemy_pos_after.x - player_pos.x) ** 2
        + (enemy_pos_after.y - player_pos.y) ** 2
    )

    # 距離が縮まっていることを確認
    assert dist_after < dist_before
    assert not logs


def test_enemy_attacks_if_player_is_adjacent(ai_setup):
    """プレイヤーが隣接している場合、敵が攻撃することをテストする。"""
    world, game_map, player, enemy = ai_setup
    # 敵をプレイヤーの隣に移動
    enemy_pos = world.get_component(enemy, PositionComponent)
    enemy_pos.x, enemy_pos.y = 10, 9

    player_health_before = world.get_component(player, HealthComponent).current_hp
    logs = process_enemy_turn(world, enemy, player, game_map)
    player_health_after = world.get_component(player, HealthComponent).current_hp

    assert player_health_after < player_health_before
    assert "ダメージを与えた" in logs[0]


def test_enemy_waits_if_path_is_blocked(ai_setup):
    """経路が完全に塞がれている場合、敵が待機することをテストする。"""
    world, game_map, player, enemy = ai_setup
    enemy_pos = world.get_component(enemy, PositionComponent)

    # 敵の周囲を壁で囲む
    x, y = enemy_pos.x, enemy_pos.y
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            game_map.tiles[x + dx, y + dy] = WALL_TILE

    enemy_x_before, enemy_y_before = x, y
    logs = process_enemy_turn(world, enemy, player, game_map)

    enemy_pos_after = world.get_component(enemy, PositionComponent)
    assert enemy_pos_after.x == enemy_x_before
    assert enemy_pos_after.y == enemy_y_before
    assert not logs
