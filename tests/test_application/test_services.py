# tests/test_application/test_services.py
"""
アプリケーションサービスのテスト
"""

import pytest

from roguelike_rpg.application.services import move_player
from roguelike_rpg.domain.ecs.components import PositionComponent
from roguelike_rpg.domain.ecs.world import World
from roguelike_rpg.domain.factories import create_player
from roguelike_rpg.domain.game_map import GameMap


@pytest.fixture
def game_setup():
    """
    テスト用のゲーム環境（World, GameMap, Player）をセットアップするフィクスチャ
    """
    world = World()
    # 5x5の小さなマップを作成
    # 中央(2,2)のみ床で、他は壁
    game_map = GameMap(width=5, height=5)
    game_map.tiles[2, 2] = game_map.tiles[0, 0].__class__(
        walkable=True, transparent=True, char=".", color=(255, 255, 255)
    )  # Floor
    # プレイヤーを中央(2,2)に配置
    player = create_player(world, 2, 2)
    return world, game_map, player


def test_move_player_successfully(game_setup):
    """
    プレイヤーが歩行可能なタイルへ移動できることをテストする。
    """
    # Arrange
    world, game_map, player = game_setup
    # (2,2) -> (2,1)への移動を試みる (上へ)
    # ただし、テストマップでは(2,2)しか歩けないので、(2,3)に床を追加する
    game_map.tiles[2, 3] = game_map.tiles[0, 0].__class__(
        walkable=True, transparent=True, char=".", color=(255, 255, 255)
    )

    # Act
    result = move_player(world, player, game_map, dx=0, dy=1)  # (2,2) -> (2,3)

    # Assert
    assert result is True
    player_pos = world.get_component(player, PositionComponent)
    assert player_pos.x == 2
    assert player_pos.y == 3


def test_move_player_into_wall_fails(game_setup):
    """
    プレイヤーが壁（歩行不可能なタイル）へ移動できないことをテストする。
    """
    # Arrange
    world, game_map, player = game_setup
    # (2,2) -> (1,2)への移動を試みる (左、壁)

    # Act
    result = move_player(world, player, game_map, dx=-1, dy=0)

    # Assert
    assert result is False
    player_pos = world.get_component(player, PositionComponent)
    # プレイヤーの位置が変わっていないことを確認
    assert player_pos.x == 2
    assert player_pos.y == 2


def test_move_player_out_of_bounds_fails(game_setup):
    """
    プレイヤーがマップの範囲外へ移動できないことをテストする。
    """
    # Arrange
    world, game_map, player = game_setup
    # (2,2)にいるプレイヤーを(4,4)に移動させてから、さらに範囲外(5,4)への移動を試みる
    player_pos = world.get_component(player, PositionComponent)
    player_pos.x, player_pos.y = 4, 4

    # Act
    result = move_player(world, player, game_map, dx=1, dy=0)

    # Assert
    assert result is False
    # プレイヤーの位置が変わっていないことを確認
    assert player_pos.x == 4
    assert player_pos.y == 4
