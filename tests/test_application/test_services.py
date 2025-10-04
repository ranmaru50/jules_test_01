# tests/test_application/test_services.py
"""
アプリケーションサービスのテスト
"""

from unittest.mock import Mock

import pytest

from roguelike_rpg.application.game_state import GameState
from roguelike_rpg.application.services import (
    attack,
    calculate_score,
    move_player,
    pickup_item,
    toggle_equipment,
    use_item,
)
from roguelike_rpg.domain.ecs.components import (
    AttackPowerComponent,
    ConfusionComponent,
    EnemyComponent,
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
    game_map = GameMap(width=20, height=20)
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
    potion = create_item(world, 5, 5, potion_data)
    dagger = create_item(world, 5, 6, dagger_data)
    return world, game_map, player, potion, dagger


@pytest.fixture
def scroll_setup(game_setup):
    """範囲効果アイテムのテスト用のセットアップ"""
    world, game_map, player = game_setup
    create_enemy(
        world,
        6,
        6,
        {
            "name": "Dummy1",
            "char": "d",
            "fg_color": [255, 0, 0],
            "max_hp": 10,
            "defense": 0,
            "power": 0,
        },
    )
    create_enemy(
        world,
        7,
        7,
        {
            "name": "Dummy2",
            "char": "d",
            "fg_color": [255, 0, 0],
            "max_hp": 10,
            "defense": 0,
            "power": 0,
        },
    )
    fireball_data = {
        "name": "火球の巻物",
        "char": "?",
        "fg_color": [255, 0, 0],
        "category": "consumable",
        "effect": {"type": "fireball", "radius": 2, "amount": 5},
    }
    confusion_data = {
        "name": "混乱の巻物",
        "char": "?",
        "fg_color": [207, 63, 255],
        "category": "consumable",
        "effect": {"type": "confusion", "duration": 5},
    }
    fireball_scroll = create_item(world, -1, -1, fireball_data)
    confusion_scroll = create_item(world, -1, -1, confusion_data)
    inventory = world.get_component(player, InventoryComponent)
    inventory.items.extend([fireball_scroll, confusion_scroll])
    return world, game_map, player, fireball_scroll, confusion_scroll


# --- 移動と攻撃のテスト ---
def test_move_player_successfully(game_setup):
    world, game_map, player = game_setup
    move_player(world, player, game_map, dx=0, dy=-1)
    player_pos = world.get_component(player, PositionComponent)
    assert player_pos.x == 5 and player_pos.y == 4


def test_move_player_into_wall_fails(game_setup):
    world, game_map, player = game_setup
    game_map.tiles[5, 4] = WALL_TILE
    move_player(world, player, game_map, dx=0, dy=-1)
    player_pos = world.get_component(player, PositionComponent)
    assert player_pos.x == 5 and player_pos.y == 5


def test_move_player_triggers_attack(combat_setup):
    world, game_map, player, _ = combat_setup
    logs = move_player(world, player, game_map, dx=0, dy=1)
    assert "ダメージを与えた" in logs[0]


def test_attack_deals_damage(combat_setup):
    world, _, player, enemy = combat_setup
    initial_hp = world.get_component(enemy, HealthComponent).current_hp
    attack(world, player, enemy)
    final_hp = world.get_component(enemy, HealthComponent).current_hp
    assert final_hp < initial_hp


# --- アイテム関連のテスト ---
def test_pickup_item(item_setup):
    world, _, player, potion, _ = item_setup
    logs = pickup_item(world, player)
    inventory = world.get_component(player, InventoryComponent)
    assert "回復ポーションを拾った" in logs[0]
    assert potion in inventory.items
    assert world.get_component(potion, PositionComponent) is None


def test_use_item_heals(item_setup):
    world, _, player, potion, _ = item_setup
    player_health = world.get_component(player, HealthComponent)
    player_health.current_hp = 20
    inventory = world.get_component(player, InventoryComponent)
    inventory.items.append(potion)
    logs = use_item(world, player, potion)
    assert "HPが5回復した" in logs[0]
    assert player_health.current_hp == 25
    assert potion not in inventory.items


def test_equip_item_adds_bonus(item_setup):
    world, _, player, _, dagger = item_setup
    inventory = world.get_component(player, InventoryComponent)
    inventory.items.append(dagger)
    power_before = world.get_component(player, AttackPowerComponent).power
    logs = toggle_equipment(world, player, dagger)
    power_after = world.get_component(player, AttackPowerComponent).power
    assert "ダガーを装備した" in logs[0]
    assert power_after == power_before + 2


def test_toggle_equipment(item_setup):
    world, _, player, _, dagger = item_setup
    inventory = world.get_component(player, InventoryComponent)
    equipment = world.get_component(player, EquipmentComponent)
    inventory.items.append(dagger)
    toggle_equipment(world, player, dagger)
    assert dagger not in inventory.items
    assert equipment.slots.get(EquipmentSlot.WEAPON) == dagger
    toggle_equipment(world, player, dagger)
    assert dagger in inventory.items
    assert equipment.slots.get(EquipmentSlot.WEAPON) is None


def test_use_item_confuses_enemy(scroll_setup):
    """混乱の巻物を使用すると、ターゲットの敵が混乱状態になることをテストする。"""
    world, _, player, _, confusion_scroll = scroll_setup
    target_enemy = next(iter(world.get_entities_with(EnemyComponent)))
    target_pos = world.get_component(target_enemy, PositionComponent)
    logs = use_item(
        world, player, confusion_scroll, target_xy=(target_pos.x, target_pos.y)
    )
    assert "混乱した！" in logs[0]
    assert world.get_component(target_enemy, ConfusionComponent) is not None
    assert world.get_component(target_enemy, ConfusionComponent).duration == 5


def test_use_item_fireball_damages_multiple_enemies(scroll_setup):
    """火球の巻物を使用すると、範囲内の複数の敵にダメージを与えることをテストする。"""
    world, _, player, fireball_scroll, _ = scroll_setup
    enemies = list(world.get_entities_with(EnemyComponent))
    initial_hps = {
        enemy: world.get_component(enemy, HealthComponent).current_hp
        for enemy in enemies
    }
    logs = use_item(world, player, fireball_scroll, target_xy=(6, 7))
    assert "火球が炸裂" in logs[0]
    for enemy in enemies:
        final_hp = world.get_component(enemy, HealthComponent).current_hp
        assert final_hp < initial_hps[enemy]


def test_calculate_score():
    """スコア計算が正しく行われることをテストする。"""
    # Arrange
    # GameLoopオブジェクトのモックを作成
    mock_game_loop = Mock()
    mock_game_loop.dungeon_level = 5
    mock_game_loop.kill_count = 10
    mock_game_loop.game_state = GameState.GAME_OVER

    # Act
    score = calculate_score(mock_game_loop)

    # Assert
    # (5 * 100) + (10 * 25) = 500 + 250 = 750
    assert score == 750

    # Arrange for victory
    mock_game_loop.game_state = GameState.VICTORY

    # Act for victory
    victory_score = calculate_score(mock_game_loop)

    # Assert for victory
    # 750 + 1000 (victory bonus) = 1750
    assert victory_score == 1750
