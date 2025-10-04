# roguelike_rpg/application/services.py
"""
アプリケーションサービス群
ドメインモデルを操作し、特定のユースケースを実現する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from roguelike_rpg.domain.ecs.components import (
    AttackPowerComponent,
    DefenseComponent,
    EnemyComponent,
    HealthComponent,
    NameComponent,
    PositionComponent,
)

if TYPE_CHECKING:
    from roguelike_rpg.domain.ecs.world import Entity, World
    from roguelike_rpg.domain.game_map import GameMap


def get_blocking_enemy_at(world: World, x: int, y: int) -> Entity | None:
    """指定された位置にいる、移動を妨げる敵エンティティを取得する。"""
    for entity in world.get_entities_with(PositionComponent, EnemyComponent):
        pos = world.get_component(entity, PositionComponent)
        if pos and pos.x == x and pos.y == y:
            return entity
    return None


def attack(world: World, attacker: Entity, defender: Entity) -> list[str]:
    """
    攻撃処理を行い、結果のログメッセージを返す。
    """
    logs = []
    attacker_name = world.get_component(attacker, NameComponent)
    defender_name = world.get_component(defender, NameComponent)
    attacker_power = world.get_component(attacker, AttackPowerComponent)
    defender_defense = world.get_component(defender, DefenseComponent)
    defender_health = world.get_component(defender, HealthComponent)

    if not (
        attacker_name
        and defender_name
        and attacker_power
        and defender_defense
        and defender_health
    ):
        return []  # 必要なコンポーネントがなければ攻撃は発生しない

    # ダメージ計算
    damage = attacker_power.power - defender_defense.defense

    if damage > 0:
        defender_health.current_hp -= damage
        logs.append(
            f"{attacker_name.name}は{defender_name.name}に{damage}のダメージを与えた！"
        )
        if defender_health.current_hp <= 0:
            logs.append(f"{defender_name.name}は倒れた！")
            # TODO: 死亡処理をここに実装（エンティティの削除など）
    else:
        logs.append(f"{attacker_name.name}の攻撃は{defender_name.name}に効かなかった。")

    return logs


def move_player(
    world: World, player: Entity, game_map: "GameMap", dx: int, dy: int
) -> list[str]:
    """
    プレイヤーエンティティを移動または攻撃させる。
    """
    logs = []
    # プレイヤーの位置コンポーネントを取得
    pos = world.get_component(player, PositionComponent)
    if not pos:
        return logs

    # 移動先の座標を計算
    dest_x = pos.x + dx
    dest_y = pos.y + dy

    # 移動先がマップの範囲外でないかチェック
    if not game_map.in_bounds(dest_x, dest_y):
        return logs

    # 移動先のタイルが歩行可能かチェック
    if not game_map.tiles[dest_x, dest_y].walkable:
        return logs

    # 移動先に敵エンティティがいないかチェック
    target_entity = get_blocking_enemy_at(world, dest_x, dest_y)
    if target_entity:
        # 敵がいる場合は攻撃する
        logs.extend(attack(world, player, target_entity))
    else:
        # 敵がいない場合は移動する
        pos.x = dest_x
        pos.y = dest_y

    return logs
