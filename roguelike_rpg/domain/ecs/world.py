# roguelike_rpg/domain/ecs/world.py
"""
ECSのワールドクラス
すべてのエンティティとコンポーネントを管理する。
"""

from __future__ import annotations

from typing import Iterable, Type, TypeVar

from .component import Component
from .entity import Entity

# 型変数TをComponentのサブクラスに制約
T = TypeVar("T", bound=Component)


class World:
    """
    エンティティとコンポーネントを管理するコンテナ。
    """

    def __init__(self):
        # 次に生成するエンティティID
        self._next_entity_id = 0
        # コンポーネントを格納する辞書
        # {ComponentType: {Entity: ComponentInstance}}
        self._components: dict[type[Component], dict[Entity, Component]] = {}

    def create_entity(self, *components: Component) -> Entity:
        """
        新しいエンティティを生成し、オプションでコンポーネントを追加する。

        Args:
            *components: エンティティに追加するコンポーネントの可変長引数。

        Returns:
            Entity: 新しく生成されたエンティティのID。
        """
        # 新しいエンティティIDを生成
        entity = Entity(self._next_entity_id)
        self._next_entity_id += 1
        # 指定されたコンポーネントをエンティティに追加
        for component in components:
            self.add_component(entity, component)
        return entity

    def add_component(self, entity: Entity, component: Component) -> None:
        """
        エンティティにコンポーネントを追加する。

        Args:
            entity (Entity): コンポーネントを追加する対象のエンティティ。
            component (Component): 追加するコンポーネントインスタンス。
        """
        component_type = type(component)
        # そのコンポーネント型の辞書がなければ初期化
        if component_type not in self._components:
            self._components[component_type] = {}
        # エンティティIDをキーとしてコンポーネントを格納
        self._components[component_type][entity] = component

    def get_component(self, entity: Entity, component_type: Type[T]) -> T | None:
        """
        指定したエンティティの特定の型のコンポーネントを取得する。

        Args:
            entity (Entity): コンポーネントを取得する対象のエンティティ。
            component_type (Type[T]): 取得したいコンポーネントの型。

        Returns:
            T | None: 見つかったコンポーネントインスタンス。見つからなければNone。
        """
        return self._components.get(component_type, {}).get(entity)

    def get_entities_with(self, *component_types: Type[Component]) -> Iterable[Entity]:
        """
        指定されたすべてのコンポーネント型を持つエンティティのジェネレータを返す。

        Args:
            *component_types: 検索条件となるコンポーネント型の可変長引数。

        Returns:
            Iterable[Entity]: 条件に一致するエンティティIDのイテラブル。
        """
        # 最初のコンポーネント型を持つエンティティの集合を取得
        try:
            entities = set(self._components[component_types[0]].keys())
        except (KeyError, IndexError):
            # 該当コンポーネントを持つエンティティが一つもなければ空を返す
            return

        # 残りのコンポーネント型についても集合をとり、積集合を計算
        for component_type in component_types[1:]:
            try:
                entities.intersection_update(self._components[component_type].keys())
            except KeyError:
                # 途中で該当エンティティがなくなれば空を返す
                return

        # 結果の集合に含まれるエンティティを順に返す
        yield from entities
