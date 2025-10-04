# roguelike_rpg/presentation/inventory_screen.py
"""
インベントリ画面の描画を担当する。
"""

import os
from typing import TYPE_CHECKING

from roguelike_rpg.domain.ecs.components import (
    EquipmentComponent,
    InventoryComponent,
    NameComponent,
)

if TYPE_CHECKING:
    from roguelike_rpg.domain.ecs.world import Entity, World


def render_inventory_screen(world: "World", player: "Entity") -> None:
    """
    インベントリ画面をコンソールに描画する。

    Args:
        world (World): 現在のECSワールド。
        player (Entity): プレイヤーエンティティ。
    """
    # 1. 画面をクリア
    os.system("cls" if os.name == "nt" else "clear")

    # 2. タイトルを表示
    print("--- インベントリ ---")
    print()

    # 3. プレイヤーのインベントリと装備を取得
    inventory = world.get_component(player, InventoryComponent)
    equipment = world.get_component(player, EquipmentComponent)

    if not inventory or not inventory.items:
        print("持ち物はありません。")
    else:
        # 4. 所持アイテムをリスト表示
        for index, item_entity in enumerate(inventory.items):
            item_name = world.get_component(item_entity, NameComponent)
            name_str = item_name.name if item_name else "名無しのアイテム"

            # 装備中かどうかをチェック
            is_equipped = False
            if equipment:
                for slot, equipped_item in equipment.slots.items():
                    if equipped_item == item_entity:
                        is_equipped = True
                        break

            # (装備中) のサフィックスを追加
            suffix = " (装備中)" if is_equipped else ""

            # アルファベット(a, b, c...)でアイテムを選択できるようにインデックスを表示
            print(f"({chr(ord('a') + index)}) {name_str}{suffix}")

    # 5. 操作方法を表示
    print("\n--------------------")
    print("[a-z] アイテムを選択, [i/q] 閉じる")
    print()
