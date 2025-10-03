# roguelike_rpg/domain/factories.py
"""
エンティティを生成するためのファクトリ関数群
"""

from .ecs.components import PlayerComponent, PositionComponent, RenderableComponent
from .ecs.world import Entity, World


def create_player(world: World, x: int, y: int) -> Entity:
    """
    プレイヤーエンティティを生成し、ワールドに追加する。

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
        PositionComponent(x=x, y=y),
        RenderableComponent(char="@", fg=(255, 255, 0), bg=(0, 0, 0)),  # 黄色い@マーク
    ]

    # ワールドにコンポーネント群を渡してエンティティを生成
    player = world.create_entity(*player_components)

    return player
