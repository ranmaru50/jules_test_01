# roguelike_rpg/infrastructure/data_loader.py
"""
外部データファイル（JSONなど）を読み込むためのローダー
"""

import json
from pathlib import Path
from typing import Any


def load_json_data(file_path: Path | str) -> dict[str, Any]:
    """
    指定されたJSONファイルを読み込み、辞書として返す。

    Args:
        file_path (Path | str): 読み込むJSONファイルのパス。

    Returns:
        dict[str, Any]: JSONファイルの内容をパースした辞書。

    Raises:
        FileNotFoundError: 指定されたファイルが見つからない場合。
        json.JSONDecodeError: ファイルの内容が有効なJSONでない場合。
    """
    # Pathオブジェクトに変換
    path = Path(file_path)

    # ファイルを開いて読み込む
    with open(path, "r", encoding="utf-8") as f:
        # JSONをパースして返す
        data = json.load(f)
    return data
