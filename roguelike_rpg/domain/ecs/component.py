# roguelike_rpg/domain/ecs/component.py
"""
ECSのコンポーネント基底クラス
"""

from dataclasses import dataclass


@dataclass
class Component:
    """
    全てのコンポーネントの基底となるクラス。
    コンポーネントは純粋なデータコンテナであり、ロジックを持たない。
    """

    pass
