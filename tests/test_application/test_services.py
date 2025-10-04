# tests/test_application/test_services.py
"""
アプリケーションサービスのテスト
"""

import pytest

from roguelike_rpg.application.services import attack, move_player
from roguelike_rpg.domain.ecs.components import (
    DefenseComponent,
    HealthComponent,
    PositionComponent,
)
from roguelike_rpg.domain.ecs.world import World
from roguelike_rpg.domain.factories import create_enemy, create_player
from roguelike_rpg.domain.game_map import GameMap
from roguelike_rpg.domain.tile import FLOOR_TILE


@pytest.fixture
def game_setup():
    """テスト用の基本的なゲーム環境をセットアップするフィクスチャ"""
    world = World()
    game_map = GameMap(width=10, height=10)
    # 全面を床にする
    game_map.tiles[:, :] = FLOOR_TILE
    player = create_player(world, 5, 5)
    return world, game_map, player


@pytest.fixture
def combat_setup(game_setup):
    """戦闘シナリオ用のセットアップを行うフィクスチャ"""
    world, game_map, player = game_setup
    enemy_data = {
        "name": "Test Dummy",
        "char": "d",
        "fg_color": [255, 0, 0],
        "max_hp": 10,
        "defense": 2,
        "power": 5,
    }
    enemy = create_enemy(world, 5, 6, enemy_data)
    return world, game_map, player, enemy


def test_move_player_successfully(game_setup):
    """プレイヤーが空のタイルへ正常に移動できることをテストする。"""
    world, game_map, player = game_setup
    logs = move_player(world, player, game_map, dx=0, dy=-1)
    player_pos = world.get_component(player, PositionComponent)
    assert player_pos.x == 5
    assert player_pos.y == 4
    assert logs == []


def test_move_player_into_wall_fails(game_setup):
    """プレイヤーが壁へ移動できないことをテストする。"""
    world, game_map, player = game_setup
    game_map.tiles[5, 4] = game_map.tiles[0, 0].__class__(
        walkable=False, transparent=False, char="#", color=(255, 255, 255)
    )  # Wall
    logs = move_player(world, player, game_map, dx=0, dy=-1)
    player_pos = world.get_component(player, PositionComponent)
    assert player_pos.x == 5
    assert player_pos.y == 5
    assert logs == []


def test_move_player_triggers_attack(combat_setup):
    """プレイヤーが敵のいるタイルへ移動しようとすると攻撃が発生することをテストする。"""
    world, game_map, player, enemy = combat_setup
    logs = move_player(world, player, game_map, dx=0, dy=1)
    assert "ダメージを与えた" in logs[0]


def test_attack_deals_damage(combat_setup):
    """攻撃が正しくダメージを与えることをテストする。"""
    world, _, player, enemy = combat_setup
    # プレイヤーの攻撃力: 5, 敵の防御力: 2 -> ダメージ: 3
    initial_hp = world.get_component(enemy, HealthComponent).current_hp
    logs = attack(world, player, enemy)
    final_hp = world.get_component(enemy, HealthComponent).current_hp
    assert final_hp == initial_hp - 3
    assert "ダメージを与えた" in logs[0]


def test_attack_no_damage(combat_setup):
    """防御力が高すぎてダメージを与えられないケースをテストする。"""
    world, _, player, enemy = combat_setup
    # 敵の防御力をプレイヤーの攻撃力より高く設定
    world.get_component(enemy, DefenseComponent).defense = 10
    initial_hp = world.get_component(enemy, HealthComponent).current_hp
    logs = attack(world, player, enemy)
    final_hp = world.get_component(enemy, HealthComponent).current_hp
    assert final_hp == initial_hp
    assert "効かなかった" in logs[0]


def test_attack_kills_defender(combat_setup):
    """攻撃によって敵を倒すケースをテストする。"""
    world, _, player, enemy = combat_setup
    # 敵のHPを低く設定
    world.get_component(enemy, HealthComponent).current_hp = 2
    logs = attack(world, player, enemy)
    final_hp = world.get_component(enemy, HealthComponent).current_hp
    assert final_hp < 0
    assert "倒れた！" in logs[1]
