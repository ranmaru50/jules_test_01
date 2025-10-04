# tests/test_application/test_services.py
"""
アプリケーションサービスのテスト
"""

import pytest

from roguelike_rpg.application.services import (
    attack,
    move_player,
    pickup_item,
    toggle_equipment,
    use_item,
)
from roguelike_rpg.domain.ecs.components import (
    AttackPowerComponent,
    EquipmentComponent,
    EquipmentSlot,
    HealthComponent,
    InventoryComponent,
    PositionComponent,
)
from roguelike_rpg.domain.ecs.world import World
from roguelike_rpg.domain.factories import create_enemy, create_item, create_player
from roguelike_rpg.domain.game_map import GameMap
from roguelike_rpg.domain.tile import FLOOR_TILE, WALL_TILE


@pytest.fixture
def game_setup():
    """テスト用の基本的なゲーム環境をセットアップするフィクスチャ"""
    world = World()
    game_map = GameMap(width=10, height=10)
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


@pytest.fixture
def item_setup(game_setup):
    """アイテム関連のテスト用のセットアップを行うフィクスチャ"""
    world, game_map, player = game_setup
    potion_data = {
        "name": "回復ポーション",
        "char": "!",
        "fg_color": [255, 0, 255],
        "category": "consumable",
        "effect": {"type": "heal", "amount": 5},
    }
    dagger_data = {
        "name": "ダガー",
        "char": "/",
        "fg_color": [0, 191, 255],
        "category": "equipment",
        "slot": "weapon",
        "bonus": {"power": 2},
    }

    potion = create_item(world, 5, 5, potion_data)  # Player's feet
    dagger = create_item(world, 5, 6, dagger_data)  # Next to player

    return world, game_map, player, potion, dagger


# --- 移動と攻撃のテスト ---
def test_move_player_successfully(game_setup):
    """プレイヤーが空のタイルへ正常に移動できることをテストする。"""
    world, game_map, player = game_setup
    move_player(world, player, game_map, dx=0, dy=-1)
    player_pos = world.get_component(player, PositionComponent)
    assert player_pos.x == 5 and player_pos.y == 4


def test_move_player_into_wall_fails(game_setup):
    """プレイヤーが壁へ移動できないことをテストする。"""
    world, game_map, player = game_setup
    game_map.tiles[5, 4] = WALL_TILE
    move_player(world, player, game_map, dx=0, dy=-1)
    player_pos = world.get_component(player, PositionComponent)
    assert player_pos.x == 5 and player_pos.y == 5


def test_move_player_triggers_attack(combat_setup):
    """プレイヤーが敵のいるタイルへ移動しようとすると攻撃が発生することをテストする。"""
    world, game_map, player, _ = combat_setup
    logs = move_player(world, player, game_map, dx=0, dy=1)
    assert "ダメージを与えた" in logs[0]


def test_attack_deals_damage(combat_setup):
    """攻撃が正しくダメージを与えることをテストする。"""
    world, _, player, enemy = combat_setup
    initial_hp = world.get_component(enemy, HealthComponent).current_hp
    attack(world, player, enemy)
    final_hp = world.get_component(enemy, HealthComponent).current_hp
    assert final_hp < initial_hp


# --- アイテム関連のテスト ---


def test_pickup_item(item_setup):
    """プレイヤーが足元のアイテムを拾えることをテストする。"""
    world, _, player, potion, _ = item_setup
    logs = pickup_item(world, player)
    inventory = world.get_component(player, InventoryComponent)
    assert "回復ポーションを拾った" in logs[0]
    assert potion in inventory.items
    assert world.get_component(potion, PositionComponent) is None


def test_use_item_heals(item_setup):
    """回復ポーションを使用するとHPが回復することをテストする。"""
    world, _, player, potion, _ = item_setup
    # HPを減らしておく
    player_health = world.get_component(player, HealthComponent)
    player_health.current_hp = 20
    # アイテムをインベントリに入れておく
    inventory = world.get_component(player, InventoryComponent)
    inventory.items.append(potion)

    logs = use_item(world, player, potion)

    assert "HPが5回復した" in logs[0]
    assert player_health.current_hp == 25
    assert potion not in inventory.items


def test_equip_item_adds_bonus(item_setup):
    """武器を装備すると攻撃力が上昇することをテストする。"""
    world, _, player, _, dagger = item_setup
    inventory = world.get_component(player, InventoryComponent)
    inventory.items.append(dagger)

    power_before = world.get_component(player, AttackPowerComponent).power
    logs = toggle_equipment(world, player, dagger)
    power_after = world.get_component(player, AttackPowerComponent).power

    assert "ダガーを装備した" in logs[0]
    assert power_after == power_before + 2


def test_toggle_equipment(item_setup):
    """装備の着脱が正しく行われることをテストする。"""
    world, _, player, _, dagger = item_setup
    inventory = world.get_component(player, InventoryComponent)
    equipment = world.get_component(player, EquipmentComponent)
    inventory.items.append(dagger)

    # 1. 装備
    toggle_equipment(world, player, dagger)
    assert dagger not in inventory.items
    assert equipment.slots.get(EquipmentSlot.WEAPON) == dagger

    # 2. 解除
    toggle_equipment(world, player, dagger)
    assert dagger in inventory.items
    assert equipment.slots.get(EquipmentSlot.WEAPON) is None
