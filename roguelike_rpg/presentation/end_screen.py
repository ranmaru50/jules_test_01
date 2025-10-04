# roguelike_rpg/presentation/end_screen.py
"""
ゲームの終了画面（勝利・ゲームオーバー）の描画を担当する。
"""

import os
from typing import TYPE_CHECKING

from roguelike_rpg.application.services import calculate_score

if TYPE_CHECKING:
    from roguelike_rpg.application.game_loop import GameLoop


def render_victory_screen(game_loop: "GameLoop") -> None:
    """
    勝利画面をコンソールに描画する。

    Args:
        game_loop (GameLoop): 現在のゲームループオブジェクト。
    """
    os.system("cls" if os.name == "nt" else "clear")
    score = calculate_score(game_loop)

    print("\n" * 5)
    print(" " * 20 + "***************************")
    print(" " * 20 + "*                         *")
    print(" " * 20 + "*        VICTORY!         *")
    print(" " * 20 + "*                         *")
    print(" " * 20 + "***************************")
    print("\n")
    print("      見事、あなたは地下20階に眠る「イェンダーの魔除け」を手に入れた！")
    print("\n")
    print(f"                      最終スコア: {score}")
    print("\n" * 5)


def render_game_over_screen(game_loop: "GameLoop") -> None:
    """
    ゲームオーバー画面をコンソールに描画する。

    Args:
        game_loop (GameLoop): 現在のゲームループオブジェクト。
    """
    os.system("cls" if os.name == "nt" else "clear")
    score = calculate_score(game_loop)

    print("\n" * 5)
    print(" " * 20 + "***************************")
    print(" " * 20 + "*                         *")
    print(" " * 20 + "*        GAME OVER        *")
    print(" " * 20 + "*                         *")
    print(" " * 20 + "***************************")
    print("\n")
    print("            あなたの冒険はここで終わった...")
    print("\n")
    print(f"                      最終スコア: {score}")
    print("\n" * 5)
