# roguelike_rpg/domain/ecs/components.py
"""
基本的なコンポーネント群
"""

from dataclasses import dataclass

from .component import Component


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
