# roguelike_rpg/presentation/dungeon_renderer.py
"""
ダンジョンの描画を担当するレンダラー
"""

import os
from typing import TYPE_CHECKING

from roguelike_rpg.domain.ecs.components import (
    HealthComponent,
    ItemComponent,
    PositionComponent,
    RenderableComponent,
)

# 循環インポートを避けるための型チェック用ブロック
if TYPE_CHECKING:
    from roguelike_rpg.domain.ecs.world import Entity, World
    from roguelike_rpg.domain.game_map import GameMap
    from roguelike_rpg.domain.message_log import MessageLog


class DungeonRenderer:
    """
    ゲームマップ、エンティティ、UIをコンソールに描画する。
    """

    def __init__(
        self,
        game_map: "GameMap",
        world: "World",
        message_log: "MessageLog",
        player_entity: "Entity",
    ):
        self.game_map = game_map
        self.world = world
        self.message_log = message_log
        self.player_entity = player_entity
        self.ui_height = 5  # UI領域の高さ

    def render(self) -> None:
        """
        現在のゲーム状態をコンソールに描画する。
        """
        # 1. 画面をクリア
        os.system("cls" if os.name == "nt" else "clear")

        # 2. 表示用のバッファをマップタイルで初期化
        display_buffer = [
            [self.game_map.tiles[x, y].char for x in range(self.game_map.width)]
            for y in range(self.game_map.height)
        ]

        # 3. 描画可能なエンティティを取得してバッファに上書き
        # まずアイテムを描画
        items_to_render = self.world.get_entities_with(
            ItemComponent, PositionComponent, RenderableComponent
        )
        for entity in items_to_render:
            pos = self.world.get_component(entity, PositionComponent)
            renderable = self.world.get_component(entity, RenderableComponent)
            if pos and renderable:
                display_buffer[pos.y][pos.x] = renderable.char

        # 次にキャラクター（HPを持つもの）を描画
        characters_to_render = self.world.get_entities_with(
            PositionComponent, RenderableComponent, HealthComponent
        )
        for entity in sorted(
            characters_to_render,
            key=lambda e: self.world.get_component(e, RenderableComponent).char != "@",
        ):  # プレイヤー(@)を最後に描画
            health = self.world.get_component(entity, HealthComponent)
            if health and health.current_hp > 0:
                pos = self.world.get_component(entity, PositionComponent)
                renderable = self.world.get_component(entity, RenderableComponent)
                if pos and renderable:
                    display_buffer[pos.y][pos.x] = renderable.char

        # 4. マップ部分の出力を生成
        map_output = "\n".join("".join(row) for row in display_buffer)

        # 5. UI部分の出力を生成
        ui_output = self.render_ui()

        # 6. 全てを結合して出力
        print(map_output)
        print("=" * self.game_map.width)  # 区切り線
        print(ui_output)
        print("\n[WASD] 移動, [g] 拾う, [i] インベントリ, [q] 終了")

    def render_ui(self) -> str:
        """UI部分の描画内容を文字列として生成する。"""
        # プレイヤーのHPバー
        player_health = self.world.get_component(self.player_entity, HealthComponent)
        hp_bar = (
            f"HP: {player_health.current_hp:2}/{player_health.max_hp:2}"
            if player_health
            else "HP: N/A"
        )

        # メッセージログ
        log_messages = self.message_log.get_latest_messages(
            self.ui_height - 1
        )  # HPバーの行を除いた分

        # UI文字列を組み立て
        ui_lines = [hp_bar]
        ui_lines.extend(log_messages)

        # 高さが足りない場合は空行で埋める
        while len(ui_lines) < self.ui_height:
            ui_lines.append("")

        return "\n".join(ui_lines)
