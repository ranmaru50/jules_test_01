# roguelike_rpg/domain/factories.py
"""
エンティティを生成するためのファクトリ関数群
"""

from typing import Any

from .ecs.components import (
    AttackPowerComponent,
    DefenseComponent,
    EnemyComponent,
    HealthComponent,
    NameComponent,
    PlayerComponent,
    PositionComponent,
    RenderableComponent,
)
from .ecs.world import Entity, World


def create_player(world: World, x: int, y: int) -> Entity:
    """
    プレイヤーエンティティを生成し、ワールドに追加する。
    戦闘用のコンポーネントも併せて追加する。

    Args:
        world (World): エンティティを追加するワールドオブジェクト。
        x (int): プレイヤーの初期x座標。
        y (int): プレイヤーの初期y座標。

    Returns:
        Entity: 生成されたプレイヤーエンティティのID。
    """
    # プレイヤーに必要なコンポーネントを定義
    player_components = [
        PlayerComponent(),
        NameComponent(name="プレイヤー"),
        PositionComponent(x=x, y=y),
        RenderableComponent(char="@", fg=(255, 255, 0), bg=(0, 0, 0)),  # 黄色い@マーク
        HealthComponent(max_hp=30, current_hp=30),
        AttackPowerComponent(power=5),
        DefenseComponent(defense=2),
    ]

    # ワールドにコンポーネント群を渡してエンティティを生成
    player = world.create_entity(*player_components)

    return player


def create_enemy(world: World, x: int, y: int, enemy_data: dict[str, Any]) -> Entity:
    """
    データに基づいて敵エンティティを生成し、ワールドに追加する。

    Args:
        world (World): エンティティを追加するワールドオブジェクト。
        x (int): 敵の初期x座標。
        y (int): 敵の初期y座標。
        enemy_data (dict[str, Any]): 敵の特性を定義したデータ。

    Returns:
        Entity: 生成された敵エンティティのID。
    """
    # 敵に必要なコンポーネントをデータから生成
    enemy_components = [
        EnemyComponent(),
        NameComponent(name=enemy_data["name"]),
        PositionComponent(x=x, y=y),
        RenderableComponent(
            char=enemy_data["char"], fg=tuple(enemy_data["fg_color"]), bg=(0, 0, 0)
        ),
        HealthComponent(max_hp=enemy_data["max_hp"], current_hp=enemy_data["max_hp"]),
        AttackPowerComponent(power=enemy_data["power"]),
        DefenseComponent(defense=enemy_data["defense"]),
    ]

    # ワールドにコンポーネント群を渡してエンティティを生成
    enemy = world.create_entity(*enemy_components)

    return enemy
