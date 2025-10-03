# roguelike_rpg/presentation/dungeon_renderer.py
"""
ダンジョンの描画を担当するレンダラー
"""

import os

from roguelike_rpg.domain.ecs.components import PositionComponent, RenderableComponent
from roguelike_rpg.domain.ecs.world import World
from roguelike_rpg.domain.game_map import GameMap


class DungeonRenderer:
    """
    ゲームマップとエンティティをコンソールに描画する。
    """

    def __init__(self, game_map: GameMap, world: World):
        self.game_map = game_map
        self.world = world

    def render(self) -> None:
        """
        現在のゲーム状態をコンソールに描画する。
        """
        # 1. 画面をクリア
        # OSに応じて 'cls' または 'clear' コマンドを実行
        os.system("cls" if os.name == "nt" else "clear")

        # 2. 表示用のバッファをマップタイルで初期化
        # numpy配列をPythonのリストのリストに変換
        display_buffer = [
            [self.game_map.tiles[x, y].char for x in range(self.game_map.width)]
            for y in range(self.game_map.height)
        ]

        # 3. 描画可能なエンティティを取得してバッファに上書き
        # PositionComponentとRenderableComponentの両方を持つエンティティを検索
        entities_to_render = self.world.get_entities_with(
            PositionComponent, RenderableComponent
        )
        for entity in entities_to_render:
            pos = self.world.get_component(entity, PositionComponent)
            renderable = self.world.get_component(entity, RenderableComponent)
            # エンティティが位置と描画情報を持っていればバッファを更新
            if pos and renderable:
                display_buffer[pos.y][pos.x] = renderable.char

        # 4. バッファの内容をコンソールに出力
        # 各行を結合して一度にprintすることで、描画のちらつきを抑える
        output = "\n".join("".join(row) for row in display_buffer)
        print(output)
        print("\n[WASD] 移動, [Q] 終了")
