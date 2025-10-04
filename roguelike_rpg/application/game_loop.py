# roguelike_rpg/application/game_loop.py
"""
ゲームのメインループと状態管理
"""

from typing import Any

from roguelike_rpg.application.enemy_ai_service import process_enemy_turn
from roguelike_rpg.application.services import move_player
from roguelike_rpg.domain.ecs.components import EnemyComponent, HealthComponent
from roguelike_rpg.domain.ecs.world import World
from roguelike_rpg.domain.factories import create_player
from roguelike_rpg.domain.game_map import GameMap
from roguelike_rpg.domain.mapgen import generate_map
from roguelike_rpg.domain.message_log import MessageLog
from roguelike_rpg.infrastructure.data_loader import load_json_data


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
        # 定数
        MAX_ENEMIES_PER_ROOM = 2
        ENEMY_DATA_PATH = "assets/enemies.json"

        # ゲームの状態を保持する属性
        self.world = World()
        self.message_log = MessageLog()

        # 敵データをロード
        self.enemy_data: dict[str, Any] = load_json_data(ENEMY_DATA_PATH)

        # マップを生成し、敵を配置
        self.game_map: GameMap = generate_map(
            world=self.world,
            map_width=map_width,
            map_height=map_height,
            max_enemies_per_room=MAX_ENEMIES_PER_ROOM,
            enemy_data=self.enemy_data,
        )

        # プレイヤーをマップの中央に配置
        player_x = map_width // 2
        player_y = map_height // 2
        self.player = create_player(self.world, player_x, player_y)

        # ゲームが実行中かどうかのフラグ
        self.running = True
        self.message_log.add_message("ダンジョンへようこそ！")

    def handle_player_action(self, dx: int, dy: int) -> None:
        """
        プレイヤーのアクションを処理し、その後、敵のターンを実行する。

        Args:
            dx (int): x軸方向の移動量。
            dy (int): y軸方向の移動量。
        """
        # プレイヤーの移動または攻撃
        player_action_logs = move_player(self.world, self.player, self.game_map, dx, dy)
        for log in player_action_logs:
            self.message_log.add_message(log)

        # プレイヤーが何かしらの行動をしたら、敵のターンに進む
        if player_action_logs or dx != 0 or dy != 0:
            self.process_enemy_turns()

        # ゲームの終了条件をチェック（プレイヤーの死亡）
        self.check_game_over()

    def process_enemy_turns(self) -> None:
        """全ての敵のターンを処理する。"""
        enemies = list(self.world.get_entities_with(EnemyComponent))
        for enemy in enemies:
            # 敵が生きているかチェック
            enemy_health = self.world.get_component(enemy, HealthComponent)
            if enemy_health and enemy_health.current_hp > 0:
                enemy_action_logs = process_enemy_turn(
                    self.world, enemy, self.player, self.game_map
                )
                for log in enemy_action_logs:
                    self.message_log.add_message(log)

    def check_game_over(self) -> None:
        """プレイヤーが死亡したかチェックし、ゲームを終了する。"""
        player_health = self.world.get_component(self.player, HealthComponent)
        if player_health and player_health.current_hp <= 0:
            self.message_log.add_message("あなたは倒れた...")
            self.running = False

    # TODO: HPが0になった敵をワールドから削除する処理を実装する
