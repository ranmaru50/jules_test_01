# roguelike_rpg/domain/factories.py
"""
エンティティを生成するためのファクトリ関数群
"""

from typing import Any

from .ecs.components import (
    AttackPowerComponent,
    ConsumableComponent,
    DefenseComponent,
    EnemyComponent,
    EquipmentComponent,
    EquipmentSlot,
    EquippableComponent,
    HealthComponent,
    InventoryComponent,
    ItemComponent,
    NameComponent,
    PlayerComponent,
    PositionComponent,
    RenderableComponent,
    StairsComponent,
    TreasureComponent,
)
from .ecs.world import Entity, World


def create_player(world: World, x: int, y: int) -> Entity:
    """
    プレイヤーエンティティを生成し、ワールドに追加する。
    戦闘、インベントリ、装備用のコンポーネントも併せて追加する。

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
        RenderableComponent(char="@", fg=(255, 255, 0), bg=(0, 0, 0)),
        HealthComponent(max_hp=30, current_hp=30),
        AttackPowerComponent(power=5),
        DefenseComponent(defense=2),
        InventoryComponent(items=[]),
        EquipmentComponent(slots={slot: None for slot in EquipmentSlot}),
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


def create_item(world: World, x: int, y: int, item_data: dict[str, Any]) -> Entity:
    """
    データに基づいてアイテムエンティティを生成し、ワールドに追加する。

    Args:
        world (World): エンティティを追加するワールドオブジェクト。
        x (int): アイテムの初期x座標。
        y (int): アイテムの初期y座標。
        item_data (dict[str, Any]): アイテムの特性を定義したデータ。

    Returns:
        Entity: 生成されたアイテムエンティティのID。
    """
    # 全てのアイテムに共通のコンポーネント
    item_components = [
        ItemComponent(),
        NameComponent(name=item_data["name"]),
        PositionComponent(x=x, y=y),
        RenderableComponent(
            char=item_data["char"], fg=tuple(item_data["fg_color"]), bg=(0, 0, 0)
        ),
    ]

    # アイテムのカテゴリに応じてコンポーネントを追加
    category = item_data.get("category")
    if category == "consumable":
        item_components.append(ConsumableComponent(effect=item_data["effect"]))
    elif category == "equipment":
        slot = EquipmentSlot[item_data["slot"].upper()]
        bonus = item_data.get("bonus", {})
        item_components.append(
            EquippableComponent(
                slot=slot,
                power_bonus=bonus.get("power", 0),
                defense_bonus=bonus.get("defense", 0),
                max_hp_bonus=bonus.get("max_hp", 0),
            )
        )
    elif category == "treasure":
        item_components.append(TreasureComponent())

    item = world.create_entity(*item_components)
    return item


def create_stairs(world: World, x: int, y: int) -> Entity:
    """
    下り階段エンティティを生成し、ワールドに追加する。

    Args:
        world (World): エンティティを追加するワールドオブジェクト。
        x (int): 階段のx座標。
        y (int): 階段のy座標。

    Returns:
        Entity: 生成された階段エンティティのID。
    """
    stairs_components = [
        StairsComponent(),
        NameComponent(name="下り階段"),
        PositionComponent(x=x, y=y),
        RenderableComponent(char=">", fg=(255, 255, 255), bg=(0, 0, 0)),  # 白い >
    ]
    stairs = world.create_entity(*stairs_components)
    return stairs
