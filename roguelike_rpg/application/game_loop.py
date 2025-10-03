# roguelike_rpg/application/game_loop.py
"""
ゲームのメインループと状態管理
"""

from roguelike_rpg.application.services import move_player
from roguelike_rpg.domain.ecs.world import World
from roguelike_rpg.domain.factories import create_player
from roguelike_rpg.domain.game_map import GameMap
from roguelike_rpg.domain.mapgen import generate_map


class GameLoop:
    """
    ゲームのメインループを管理し、ゲームの全体的な状態を保持する。
    """

    def __init__(self, map_width: int, map_height: int):
        """
        GameLoopのコンストラクタ。
        ゲームの初期状態（ワールド、マップ、プレイヤー）をセットアップする。

        Args:
            map_width (int): マップの幅。
            map_height (int): マップの高さ。
        """
        # ゲームの状態を保持する属性
        self.world = World()
        self.game_map: GameMap = generate_map(map_width, map_height)

        # プレイヤーをマップの中央に配置
        player_x = map_width // 2
        player_y = map_height // 2
        self.player = create_player(self.world, player_x, player_y)

        # ゲームが実行中かどうかのフラグ
        self.running = True

    def handle_player_action(self, dx: int, dy: int) -> None:
        """
        プレイヤーのアクション（移動）を処理する。

        Args:
            dx (int): x軸方向の移動量。
            dy (int): y軸方向の移動量。
        """
        # プレイヤーの移動サービスを呼び出す
        move_player(self.world, self.player, self.game_map, dx, dy)

        # TODO: プレイヤーの行動後に敵のターンを実行する
        # TODO: ゲームの終了条件をチェックする
        pass
