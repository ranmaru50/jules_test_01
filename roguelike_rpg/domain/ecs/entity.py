# roguelike_rpg/domain/ecs/entity.py
"""
ECSのエンティティ型を定義する
"""

from typing import NewType

# エンティティは一意なIDを持つ。ここでは整数型として定義する。
Entity = NewType("Entity", int)
