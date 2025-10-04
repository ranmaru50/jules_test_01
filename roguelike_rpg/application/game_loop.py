# roguelike_rpg/application/game_loop.py
"""
ゲームのメインループと状態管理
"""

from typing import Any

from roguelike_rpg.application.enemy_ai_service import process_enemy_turn
from roguelike_rpg.application.game_state import GameState
from roguelike_rpg.application.services import (
    descend_stairs,
    move_player,
    pickup_item,
    toggle_equipment,
    use_item,
)
from roguelike_rpg.domain.ecs.components import (
    ConsumableComponent,
    EnemyComponent,
    EquippableComponent,
    HealthComponent,
    InventoryComponent,
    PositionComponent,
)
from roguelike_rpg.domain.ecs.world import World
from roguelike_rpg.domain.factories import create_player
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
        """
        # 定数
        MAX_ENEMIES_PER_ROOM = 2
        MAX_ITEMS_PER_ROOM = 2
        ENEMY_DATA_PATH = "assets/enemies.json"
        ITEM_DATA_PATH = "assets/items.json"

        # ゲームの状態を保持する属性
        self.world = World()
        self.message_log = MessageLog()
        self.game_state = GameState.PLAYERS_TURN
        self.dungeon_level = 1
        self.kill_count = 0
        self.targeting_cursor: tuple[int, int] | None = None
        self.item_to_use: Any | None = None

        # データをロード
        self.enemy_data: dict[str, Any] = load_json_data(ENEMY_DATA_PATH)
        self.item_data: dict[str, Any] = load_json_data(ITEM_DATA_PATH)

        # マップを生成し、敵とアイテムを配置
        self.game_map, player_start_pos = generate_map(
            world=self.world,
            map_width=map_width,
            map_height=map_height,
            dungeon_level=self.dungeon_level,
            max_enemies_per_room=MAX_ENEMIES_PER_ROOM,
            max_items_per_room=MAX_ITEMS_PER_ROOM,
            enemy_data=self.enemy_data,
            item_data=self.item_data,
        )

        # プレイヤーをマップの安全な開始位置に配置
        self.player = create_player(
            self.world, player_start_pos[0], player_start_pos[1]
        )

        self.message_log.add_message("ダンジョンへようこそ！")

    def process_input(self, key: str) -> None:
        """現在のゲーム状態に基づいてプレイヤーの入力を処理する。"""
        if self.game_state == GameState.PLAYERS_TURN:
            self._handle_player_turn_input(key)
        elif self.game_state == GameState.SHOW_INVENTORY:
            self._handle_inventory_input(key)
        elif self.game_state == GameState.TARGETING:
            self._handle_targeting_input(key)

    def _handle_inventory_input(self, key: str) -> None:
        """インベントリ画面でのアクションを処理する。"""
        if key in ("i", "q"):
            self.game_state = GameState.PLAYERS_TURN
            self.message_log.add_message("インベントリを閉じた。")
            return

        try:
            item_index = ord(key) - ord("a")
        except TypeError:
            self.message_log.add_message("無効なキーです。")
            return

        inventory = self.world.get_component(self.player, InventoryComponent)
        if not inventory or not (0 <= item_index < len(inventory.items)):
            self.message_log.add_message("無効なアイテム選択です。")
            return

        item_entity = inventory.items[item_index]
        consumable = self.world.get_component(item_entity, ConsumableComponent)

        # ターゲット選択が必要なアイテムかチェック
        if consumable and consumable.effect.get("type") in [
            "damage",
            "confusion",
            "fireball",
        ]:
            self.start_targeting(item_entity)
            return

        # 通常のアイテム使用/装備
        logs = []
        action_taken = False
        if consumable:
            logs = use_item(self.world, self.player, item_entity)
            action_taken = True
        elif self.world.get_component(item_entity, EquippableComponent):
            logs = toggle_equipment(self.world, self.player, item_entity)
            action_taken = True
        else:
            self.message_log.add_message("このアイテムには特別な使い道がない。")

        for log in logs:
            self.message_log.add_message(log)

        if action_taken:
            self.game_state = GameState.ENEMY_TURN
            self.process_enemy_turns()

    def start_targeting(self, item_entity: Any) -> None:
        """ターゲット選択モードを開始する。"""
        self.game_state = GameState.TARGETING
        self.item_to_use = item_entity
        player_pos = self.world.get_component(self.player, PositionComponent)
        self.targeting_cursor = (player_pos.x, player_pos.y)
        self.message_log.add_message(
            "ターゲットを選択してください。[Enter]で決定, [q]でキャンセル。"
        )

    def _handle_player_turn_input(self, key: str) -> None:
        """プレイヤーのターン中のアクションを処理する。"""
        action_map = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
        action_taken = False
        logs = []

        if key in action_map:
            dx, dy = action_map[key]
            logs = move_player(self.world, self.player, self.game_map, dx, dy)
            action_taken = True
        elif key == "g":
            logs = pickup_item(self.world, self.player)
            # アイテムを拾えなかった場合はターンを消費しない
            if not (logs and "ここには何もない。" in logs[0]):
                action_taken = True
        elif key == ">":
            if descend_stairs(self.world, self.player):
                self.next_floor()
                # next_floorの中でターンがリセットされるので、ここでは何もしない
            else:
                self.message_log.add_message("ここには階段はない。")
        elif key == "i":
            self.game_state = GameState.SHOW_INVENTORY

        for log in logs:
            self.message_log.add_message(log)
            if log.startswith("VICTORY:"):
                self.game_state = GameState.VICTORY
                action_taken = False  # 勝利したので敵のターンは来ない
                break

        if action_taken:
            self.game_state = GameState.ENEMY_TURN
            self.process_enemy_turns()

    def _handle_targeting_input(self, key: str) -> None:
        """ターゲット選択モードでの入力を処理する。"""
        move_keys = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}

        if key in move_keys:
            dx, dy = move_keys[key]
            # カーソルがマップ範囲内にあるように制限
            new_x = max(0, min(self.game_map.width - 1, self.targeting_cursor[0] + dx))
            new_y = max(0, min(self.game_map.height - 1, self.targeting_cursor[1] + dy))
            self.targeting_cursor = (new_x, new_y)
        elif key == "":  # Enterキーで決定
            if self.item_to_use:
                logs = use_item(
                    self.world, self.player, self.item_to_use, self.targeting_cursor
                )
                for log in logs:
                    self.message_log.add_message(log)

                self.item_to_use = None
                self.targeting_cursor = None
                self.game_state = GameState.ENEMY_TURN
                self.process_enemy_turns()
        elif key == "q":
            self.game_state = GameState.PLAYERS_TURN
            self.item_to_use = None
            self.targeting_cursor = None
            self.message_log.add_message("ターゲット選択をキャンセルした。")

    def process_enemy_turns(self) -> None:
        """全ての敵のターンを処理し、プレイヤーのターンに戻す。"""
        enemies = list(self.world.get_entities_with(EnemyComponent))
        for enemy in enemies:
            enemy_health = self.world.get_component(enemy, HealthComponent)
            if enemy_health and enemy_health.current_hp > 0:
                enemy_action_logs = process_enemy_turn(
                    self.world, enemy, self.player, self.game_map
                )
                for log in enemy_action_logs:
                    self.message_log.add_message(log)

        self._cleanup_dead_entities()

        self.check_game_over()
        if self.game_state != GameState.GAME_OVER:
            self.game_state = GameState.PLAYERS_TURN

    def _cleanup_dead_entities(self) -> None:
        """HPが0以下のエンティティをワールドから削除し、キルカウントを更新する。"""
        dead_entities = []
        for entity in self.world.get_entities_with(HealthComponent):
            if self.world.get_component(entity, HealthComponent).current_hp <= 0:
                if entity != self.player:
                    dead_entities.append(entity)

        for entity in dead_entities:
            if self.world.get_component(entity, EnemyComponent):
                self.kill_count += 1
            self.world.delete_entity(entity)

    def check_game_over(self) -> None:
        """プレイヤーが死亡したかチェックし、ゲームの状態を更新する。"""
        player_health = self.world.get_component(self.player, HealthComponent)
        if player_health and player_health.current_hp <= 0:
            self.message_log.add_message("あなたは倒れた...")
            self.game_state = GameState.GAME_OVER

    def next_floor(self) -> None:
        """新しいフロアを生成し、ゲームの状態をリセットする。"""
        self.dungeon_level += 1
        self.message_log.add_message("あなたはより深い階層へと下りていった...")

        # プレイヤー以外のすべてのエンティティを削除
        for entity in list(self.world.get_entities_with(PositionComponent)):
            if entity != self.player:
                self.world.delete_entity(entity)

        # 新しいマップを生成（難易度上昇）
        max_enemies_per_room = 2 + self.dungeon_level // 2
        max_items_per_room = 2 + self.dungeon_level // 3

        self.game_map, player_start_pos = generate_map(
            world=self.world,
            map_width=self.game_map.width,
            map_height=self.game_map.height,
            dungeon_level=self.dungeon_level,
            max_enemies_per_room=max_enemies_per_room,
            max_items_per_room=max_items_per_room,
            enemy_data=self.enemy_data,
            item_data=self.item_data,
        )

        # プレイヤーを新しい位置に配置
        player_pos = self.world.get_component(self.player, PositionComponent)
        if player_pos:
            player_pos.x, player_pos.y = player_start_pos

        # ゲーム状態をプレイヤーのターンに戻す
        self.game_state = GameState.PLAYERS_TURN
