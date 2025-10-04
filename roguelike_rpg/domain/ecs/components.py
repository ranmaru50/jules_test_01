# roguelike_rpg/domain/ecs/components.py
"""
基本的なコンポーネント群
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from .component import Component
from .entity import Entity


@dataclass
class PositionComponent(Component):
    """
    エンティティの位置情報（x, y座標）を管理するコンポーネント。
    """

    x: int
    y: int


@dataclass
class RenderableComponent(Component):
    """
    エンティティの描画情報（文字、色）を管理するコンポーネント。
    """

    char: str
    fg: tuple[int, int, int]
    bg: tuple[int, int, int]


@dataclass
class PlayerComponent(Component):
    """
    このコンポーネントを持つエンティティがプレイヤーであることを示すマーカー。
    """

    pass


@dataclass
class StairsComponent(Component):
    """
    このコンポーネントを持つエンティティが次の階層への階段であることを示すマーカー。
    """

    pass


class EquipmentSlot(Enum):
    """装備部位を表す列挙型"""

    WEAPON = auto()
    ARMOR = auto()


@dataclass
class ItemComponent(Component):
    """
    このコンポーネントを持つエンティティがアイテムであることを示すマーカー。
    """

    pass


@dataclass
class ConsumableComponent(Component):
    """
    消費可能アイテムの特性を管理するコンポーネント。
    """

    effect: Dict[str, Any]  # 例: {"type": "heal", "amount": 10}


@dataclass
class EquippableComponent(Component):
    """
    装備可能アイテムの特性を管理するコンポーネント。
    """

    slot: EquipmentSlot
    power_bonus: int = 0
    defense_bonus: int = 0


@dataclass
class InventoryComponent(Component):
    """
    エンティティの持ち物を管理するコンポーネント。
    """

    items: List[Entity]


@dataclass
class EquipmentComponent(Component):
    """
    エンティティの装備状態を管理するコンポーネント。
    """

    slots: Dict[EquipmentSlot, Optional[Entity]]


@dataclass
class NameComponent(Component):
    """
    エンティティの名前を管理するコンポーネント。
    """

    name: str


@dataclass
class HealthComponent(Component):
    """
    エンティティのHP（体力）を管理するコンポーネント。
    """

    max_hp: int
    current_hp: int


@dataclass
class AttackPowerComponent(Component):
    """
    エンティティの攻撃力を管理するコンポーネント。
    """

    power: int


@dataclass
class DefenseComponent(Component):
    """
    エンティティの防御力を管理するコンポーネント。
    """

    defense: int


@dataclass
class EnemyComponent(Component):
    """
    このコンポーネントを持つエンティティが敵であることを示すマーカー。
    """

    pass
