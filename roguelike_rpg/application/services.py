# roguelike_rpg/application/services.py
"""
アプリケーションサービス群
ドメインモデルを操作し、特定のユースケースを実現する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from roguelike_rpg.domain.ecs.components import (
    AttackPowerComponent,
    ConsumableComponent,
    DefenseComponent,
    EnemyComponent,
    EquipmentComponent,
    EquippableComponent,
    HealthComponent,
    InventoryComponent,
    ItemComponent,
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


def pickup_item(world: World, actor: Entity) -> list[str]:
    """
    アクタの足元にあるアイテムを拾い、インベントリに追加する。
    """
    logs = []
    actor_pos = world.get_component(actor, PositionComponent)
    inventory = world.get_component(actor, InventoryComponent)

    if not actor_pos or not inventory:
        return ["アイテムを拾えません。"]

    # アクタの足元にあるアイテムを探す
    item_to_pickup = None
    for item_entity in world.get_entities_with(ItemComponent, PositionComponent):
        item_pos = world.get_component(item_entity, PositionComponent)
        if item_pos and item_pos.x == actor_pos.x and item_pos.y == actor_pos.y:
            item_to_pickup = item_entity
            break

    if not item_to_pickup:
        logs.append("ここには何もない。")
        return logs

    # インベントリに追加
    inventory.items.append(item_to_pickup)
    # マップからアイテムを削除（PositionComponentを削除することで描画されなくなる）
    world.remove_component(item_to_pickup, PositionComponent)

    item_name = world.get_component(item_to_pickup, NameComponent)
    logs.append(f"{item_name.name}を拾った。")

    return logs


def use_item(world: World, user: Entity, item_entity: Entity) -> list[str]:
    """
    指定されたアイテムを使用し、効果を発動させる。
    """
    logs = []
    consumable = world.get_component(item_entity, ConsumableComponent)
    item_name = world.get_component(item_entity, NameComponent)

    if not consumable or not item_name:
        return ["このアイテムは使用できない。"]

    effect = consumable.effect
    effect_type = effect.get("type")

    # 効果の種類に応じて処理を分岐
    if effect_type == "heal":
        health = world.get_component(user, HealthComponent)
        if health:
            amount = effect.get("amount", 0)
            healed_amount = min(health.max_hp - health.current_hp, amount)
            if healed_amount > 0:
                health.current_hp += healed_amount
                logs.append(f"{item_name.name}を使い、HPが{healed_amount}回復した。")
            else:
                logs.append("HPは満タンだ。")
        else:
            logs.append("HPがない対象には使えない。")
    else:
        logs.append("このアイテムは何の効果ももたらさなかった。")

    # インベントリからアイテムを削除
    inventory = world.get_component(user, InventoryComponent)
    if inventory:
        inventory.items.remove(item_entity)
        # TODO: ワールドからエンティティそのものを削除する処理も必要

    return logs


def toggle_equipment(world: World, actor: Entity, item_entity: Entity) -> list[str]:
    """
    指定されたアイテムを装備、または装備解除する。
    """
    logs = []
    equippable = world.get_component(item_entity, EquippableComponent)
    equipment = world.get_component(actor, EquipmentComponent)
    inventory = world.get_component(actor, InventoryComponent)
    item_name = world.get_component(item_entity, NameComponent)

    if not equippable or not equipment or not inventory or not item_name:
        return ["このアイテムは装備できない。"]

    slot = equippable.slot

    # アイテムが現在装備されているかチェック
    if equipment.slots.get(slot) == item_entity:
        # --- 装備解除 ---
        equipment.slots[slot] = None
        inventory.items.append(item_entity)
        # ボーナスを削除
        actor_power = world.get_component(actor, AttackPowerComponent)
        actor_defense = world.get_component(actor, DefenseComponent)
        if actor_power:
            actor_power.power -= equippable.power_bonus
        if actor_defense:
            actor_defense.defense -= equippable.defense_bonus
        logs.append(f"{item_name.name}を外した。")
    else:
        # --- 装備 ---
        # 同じスロットに別のアイテムが装備されている場合は、まずそれを外す
        if equipment.slots.get(slot) is not None:
            currently_equipped_entity = equipment.slots[slot]
            logs.extend(toggle_equipment(world, actor, currently_equipped_entity))

        # 新しいアイテムを装備
        equipment.slots[slot] = item_entity
        inventory.items.remove(item_entity)
        # ボーナスを追加
        actor_power = world.get_component(actor, AttackPowerComponent)
        actor_defense = world.get_component(actor, DefenseComponent)
        if actor_power:
            actor_power.power += equippable.power_bonus
        if actor_defense:
            actor_defense.defense += equippable.defense_bonus
        logs.append(f"{item_name.name}を装備した。")

    return logs
