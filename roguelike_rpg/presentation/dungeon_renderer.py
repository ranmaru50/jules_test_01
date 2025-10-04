# roguelike_rpg/presentation/dungeon_renderer.py
"""
ダンジョンの描画を担当するレンダラー（Colorama対応）
"""

import os
from typing import TYPE_CHECKING, List

from colorama import Style, init

from roguelike_rpg.domain.ecs.components import (
    HealthComponent,
    ItemComponent,
    PositionComponent,
    RenderableComponent,
)

# Coloramaを初期化
init()

# 循環インポートを避けるための型チェック用ブロック
if TYPE_CHECKING:
    from roguelike_rpg.domain.ecs.world import Entity, World
    from roguelike_rpg.domain.game_map import GameMap
    from roguelike_rpg.domain.message_log import MessageLog


# 24-bitカラーをサポートするANSIエスケープシーケンスを生成するヘルパー
def rgb_fg(r, g, b):
    return f"\x1b[38;2;{r};{g};{b}m"


def rgb_bg(r, g, b):
    return f"\x1b[48;2;{r};{g};{b}m"


class DungeonRenderer:
    """
    ゲームマップ、エンティティ、UIをコンソールに描画する。
    Coloramaを使用して色付きで表示する。
    """

    def __init__(
        self,
        game_map: "GameMap",
        world: "World",
        message_log: "MessageLog",
        player_entity: "Entity",
        dungeon_level: int,
    ):
        self.game_map = game_map
        self.world = world
        self.message_log = message_log
        self.player_entity = player_entity
        self.dungeon_level = dungeon_level
        self.targeting_cursor: tuple[int, int] | None = None
        self.ui_height = 5

    def render(self) -> None:
        """現在のゲーム状態をコンソールに描画する。"""
        os.system("cls" if os.name == "nt" else "clear")

        # 1. 表示用のバッファをマップタイルで初期化
        # バッファは (char, fg_color, bg_color) のタプルを保持
        bg_color = (0, 0, 0)  # デフォルトの背景色
        display_buffer: List[List[tuple[str, tuple, tuple]]] = [
            [(tile.char, tile.color, bg_color) for tile in row]
            for row in self.game_map.tiles.T
        ]

        # 2. エンティティを描画バッファに上書き
        # アイテム -> キャラクターの順で描画
        entities_to_render = self.world.get_entities_with(
            PositionComponent, RenderableComponent
        )
        sorted_entities = sorted(
            entities_to_render,
            key=lambda e: (
                0 if self.world.get_component(e, ItemComponent) else 1,
                self.world.get_component(e, RenderableComponent).char != "@",
            ),
        )

        for entity in sorted_entities:
            health = self.world.get_component(entity, HealthComponent)
            if health and health.current_hp <= 0:
                continue  # 死んだキャラクターは描画しない

            pos = self.world.get_component(entity, PositionComponent)
            renderable = self.world.get_component(entity, RenderableComponent)
            if pos and renderable:
                display_buffer[pos.y][pos.x] = (
                    renderable.char,
                    renderable.fg,
                    renderable.bg,
                )

        # 3. ターゲットカーソルをハイライト
        if self.targeting_cursor:
            x, y = self.targeting_cursor
            char, fg, _ = display_buffer[y][x]
            display_buffer[y][x] = (char, fg, (0, 127, 127))  # 背景をシアンに

        # 4. バッファの内容を色付きでコンソールに出力
        output = ""
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                char, fg, bg = display_buffer[y][x]
                output += (
                    f"{rgb_fg(fg[0], fg[1], fg[2])}{rgb_bg(bg[0], bg[1], bg[2])}{char}"
                )
            output += Style.RESET_ALL + "\n"

        print(output.rstrip())

        # 5. UI部分の出力を生成
        ui_output = self.render_ui()
        print("=" * self.game_map.width)
        print(ui_output)
        print("\n[WASD] 移動, [g] 拾う, [i] インベントリ, [>] 階段, [q] 終了")

    def render_ui(self) -> str:
        """UI部分の描画内容を文字列として生成する。"""
        player_health = self.world.get_component(self.player_entity, HealthComponent)
        hp_bar = (
            f"HP: {player_health.current_hp:2}/{player_health.max_hp:2}"
            if player_health
            else "HP: N/A"
        )
        level_str = f"B{self.dungeon_level}F"
        ui_top_line = f"{hp_bar:<20} | {level_str:>8}"

        log_messages = self.message_log.get_latest_messages(self.ui_height - 1)

        ui_lines = [ui_top_line]
        ui_lines.extend(log_messages)

        while len(ui_lines) < self.ui_height:
            ui_lines.append("")

        return "\n".join(ui_lines)
