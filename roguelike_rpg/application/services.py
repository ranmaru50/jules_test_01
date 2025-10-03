# roguelike_rpg/application/services.py
"""
アプリケーションサービス群
ドメインモデルを操作し、特定のユースケースを実現する。
"""

from roguelike_rpg.domain.ecs.components import PositionComponent
from roguelike_rpg.domain.ecs.world import Entity, World
from roguelike_rpg.domain.game_map import GameMap


def move_player(
    world: World, player: Entity, game_map: GameMap, dx: int, dy: int
) -> bool:
    """
    プレイヤーエンティティを移動させる。

    Args:
        world (World): 現在のECSワールド。
        player (Entity): 移動させるプレイヤーエンティティ。
        game_map (GameMap): 現在のゲームマップ。
        dx (int): x軸方向の移動量。
        dy (int): y軸方向の移動量。

    Returns:
        bool: 移動が成功したかどうか。
    """
    # プレイヤーの位置コンポーネントを取得
    pos = world.get_component(player, PositionComponent)
    if not pos:
        # プレイヤーが位置情報を持たない場合は何もしない
        return False

    # 移動先の座標を計算
    dest_x = pos.x + dx
    dest_y = pos.y + dy

    # 移動先がマップの範囲外でないかチェック
    if not game_map.in_bounds(dest_x, dest_y):
        return False

    # 移動先のタイルが歩行可能かチェック
    if not game_map.tiles[dest_x, dest_y].walkable:
        return False

    # TODO: 移動先に敵エンティティがいないかチェックする

    # 位置コンポーネントを更新
    pos.x = dest_x
    pos.y = dest_y

    return True
