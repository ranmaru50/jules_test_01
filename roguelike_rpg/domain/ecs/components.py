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
