# roguelike_rpg/domain/message_log.py
"""
ゲーム内のメッセージログを管理する。
"""

from __future__ import annotations

from typing import Iterable, List


class MessageLog:
    """
    ゲーム内で発生したイベントのメッセージを時系列で管理する。

    Attributes:
        messages (List[str]): メッセージのリスト。
    """

    def __init__(self):
        self.messages: List[str] = []

    def add_message(self, message: str) -> None:
        """
        新しいメッセージをログに追加する。

        Args:
            message (str): ログに追加するメッセージ。
        """
        # TODO: メッセージに色やメタ情報を追加する
        self.messages.append(message)

    def get_latest_messages(self, count: int) -> Iterable[str]:
        """
        最新のメッセージを新しいものから順に指定された数だけ取得する。

        Args:
            count (int): 取得するメッセージの数。

        Returns:
            Iterable[str]: 最新のメッセージのイテラブル。
        """
        # リストの末尾から指定された数だけスライスして逆順にする
        return reversed(self.messages[-count:])
