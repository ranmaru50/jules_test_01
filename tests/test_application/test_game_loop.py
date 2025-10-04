# tests/test_application/test_game_loop.py
"""
GameLoopクラスの統合的なテスト
"""

from unittest.mock import MagicMock, patch

import pytest

from roguelike_rpg.application.game_loop import GameLoop
from roguelike_rpg.domain.ecs.components import (
    EnemyComponent,
    HealthComponent,
    InventoryComponent,
    ItemComponent,
    StairsComponent,
)


@pytest.fixture
def game_loop_setup():
    """
    テスト用のGameLoopインスタンスをセットアップするフィクスチャ。
    敵とアイテムが必ず1つは生成されるようにrandomをモック化する。
    """
    with patch("roguelike_rpg.domain.mapgen.random.randint", return_value=1):
        game_loop = GameLoop(map_width=50, map_height=30)
    return game_loop


def test_next_floor_resets_map_and_entities(game_loop_setup):
    """
    next_floorがプレイヤーの状態を維持しつつ、マップとエンティティをリセットすることをテストする。
    """
    # Arrange
    game_loop = game_loop_setup
    player = game_loop.player
    world = game_loop.world

    # 初期状態のスナップショット
    initial_hp = world.get_component(player, HealthComponent).current_hp
    initial_inventory_size = len(world.get_component(player, InventoryComponent).items)
    initial_enemies = list(world.get_entities_with(EnemyComponent))
    initial_items = list(world.get_entities_with(ItemComponent))
    initial_stairs = list(world.get_entities_with(StairsComponent))

    # Act
    with patch("roguelike_rpg.domain.mapgen.random.randint", return_value=1):
        game_loop.next_floor()

    # Assert
    # 階層レベルが上がっている
    assert game_loop.dungeon_level == 2

    # プレイヤーのステータスは維持されている
    assert world.get_component(player, HealthComponent).current_hp == initial_hp
    assert (
        len(world.get_component(player, InventoryComponent).items)
        == initial_inventory_size
    )

    # 古いエンティティは存在しない
    for entity in initial_enemies + initial_items + initial_stairs:
        assert world.get_component(entity, HealthComponent) is None
        assert world.get_component(entity, ItemComponent) is None
        assert world.get_component(entity, StairsComponent) is None

    # 新しいエンティティが生成されている
    assert len(list(world.get_entities_with(EnemyComponent))) > 0
    assert len(list(world.get_entities_with(StairsComponent))) == 1


@patch("roguelike_rpg.application.game_loop.generate_map")
def test_next_floor_increases_difficulty(mock_generate_map):
    """
    next_floorを呼び出すと、難易度（最大敵数）が上昇することをテストする。
    """
    # Arrange
    # generate_mapのモックが (map, start_pos) のタプルを返すように設定
    mock_generate_map.return_value = (MagicMock(), (0, 0))
    game_loop = GameLoop(map_width=50, map_height=30)

    # Act & Assert
    game_loop.next_floor()
    args, kwargs = mock_generate_map.call_args
    assert kwargs["max_enemies_per_room"] == 3  # B2F

    game_loop.next_floor()
    args, kwargs = mock_generate_map.call_args
    assert kwargs["max_enemies_per_room"] == 3  # B3F

    game_loop.next_floor()
    args, kwargs = mock_generate_map.call_args
    assert kwargs["max_enemies_per_room"] == 4  # B4F


def test_dead_enemies_are_cleaned_up(game_loop_setup):
    """
    HPが0になった敵がターン終了時にクリーンアップされることをテストする。
    """
    # Arrange
    game_loop = game_loop_setup
    world = game_loop.world

    enemy_to_kill = next(iter(world.get_entities_with(EnemyComponent)), None)
    assert enemy_to_kill is not None, "前提条件：テストマップに敵が存在しません"

    # 敵のHPを0にする
    enemy_health = world.get_component(enemy_to_kill, HealthComponent)
    enemy_health.current_hp = 0

    # Act
    game_loop.process_enemy_turns()

    # Assert
    assert world.get_component(enemy_to_kill, HealthComponent) is None
    assert world.get_component(enemy_to_kill, EnemyComponent) is None
