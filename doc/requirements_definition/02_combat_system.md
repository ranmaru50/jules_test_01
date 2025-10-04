# 要件定義書: 02_敵の出現と戦闘システム

## 概要
この文書は、ローグライクRPG開発の第二のマイルストーンである「敵の出現と戦闘システム」の要件を定義する。

## 完了目標
-   マップ上に敵キャラクターが自動的に配置される。
-   プレイヤーは敵に攻撃でき、敵もプレイヤーに反撃してくる。
-   戦闘によってHPが0になったキャラクターはマップから取り除かれる。
-   戦闘に関する情報（ダメージ、ログ）が画面に表示される。

## 実行計画 (チェックリスト)
- [ ] **Infrastructure層**
    - [ ] `assets/` ディレクトリを作成する。
    - [ ] `assets/enemies.json` に、ゴブリンとオークの基本データを定義する。
    - [ ] `infrastructure`層をパッケージとして初期化する (`__init__.py`)。
    - [ ] `infrastructure/data_loader.py` にJSONファイルを読み込む機能を実装する。
- [ ] **Domain層**
    - [ ] 戦闘用コンポーネント (`HealthComponent`, `AttackPowerComponent`, `DefenseComponent`, `NameComponent`, `EnemyComponent`) を `ecs/components.py` に追加する。
    - [ ] `mapgen.py` に、マップの空きスペースに敵を配置するロジックを追加する。
    - [ ] `factories.py` に、データに基づいて敵エンティティを生成する `create_enemy` 関数を追加する。
- [ ] **Application層**
    - [ ] `GameLoop` が敵のデータをロードして保持するようにする。
    - [ ] プレイヤーの行動後に敵が行動する、基本的なターン制ロジックを `GameLoop` に導入する。
    - [ ] 攻撃とダメージ計算を行う `combat_service` を `application/services.py` に実装する。
    - [ ] `move_player` サービスを更新し、移動先に敵がいた場合は `combat_service` を呼び出すようにする。
    - [ ] プレイヤーを追跡するシンプルな敵AI (`enemy_ai_service`) を実装する。
- [ ] **Presentation層**
    - [ ] `DungeonRenderer` が敵をマップ上に描画するように更新する。
    - [ ] プレイヤーのHPやステータスを表示するUI領域を `DungeonRenderer` に追加する。
    - [ ] 戦闘ログを管理する `MessageLog` クラスを `domain` に追加し、`DungeonRenderer` で描画する。
- [ ] **テスト**
    - [ ] ダメージ計算ロジックをテストする。
    - [ ] 敵のAI（追跡ロジック）をテストする。
- [ ] **ドキュメント**
    - [ ] `README.md` に、戦闘の基本操作について追記する。