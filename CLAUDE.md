# CLAUDE.md — 外部記憶（Obsidian）運用ルール

## 前提条件（役割定義）

あなたは私のアシスタントであり、このリポジトリの `vault/` フォルダ（Obsidian 保管庫）を**外部脳（外部記憶）として使用する**。
セッションをまたいだ記憶はこの Vault だけが持っている。Vault を読まずに作業を始めること・Vault に書かずに作業を終えることは、記憶喪失と同じ。

## 接続方式（MCP 優先・ファイル直接アクセスへフォールバック）

1. **mcp-obsidian のツール（`mcp__obsidian__*`）が利用可能なら、それを使って Vault を読み書きする**（Obsidian の Local REST API 経由）
2. MCP ツールが見つからない・接続エラーになる場合は、**標準の Read / Write / Edit / Glob / Grep で `vault/` 配下の Markdown を直接読み書きする**。ノートはただのファイルなので、これで完全に代替できる。フォールバックしたことを理由に読み書きを省略しないこと

## 読み取りルール（記憶の引き継ぎ）

**新しいセッションを開始したら、作業に入る前に必ず Vault の中身を確認しに行く。**

1. `vault/Daily/` の最新ノートを読み、前回の作業内容・未完了タスク・「次にやること」を把握する
2. `vault/Mistakes/` のノートに**全件**目を通し、同じミスを繰り返さないようにする
3. `vault/Decisions/` から今回のタスクに関連する決定事項・判断基準を確認し、それに従う
4. `vault/Knowledge/` から今回のタスクに関連する知見を確認する

確認した内容は最初の応答で簡潔に要約する（例:「前回は◯◯まで完了、今日は△△から再開します」）。

## 書き込みルール（自動記録）

以下の状況では、**指示を待たずに** Vault へ記録する。

| 状況 | 記録先 | 形式 |
| --- | --- | --- |
| ミスを指摘された／自分のミスに気づいて修正した | `vault/Mistakes/YYYY-MM-DD_要約.md` | `Mistakes/_template.md` に従う。「再発防止」を必ず書く |
| 新しい知見・問題の対処法を得た（調査に時間がかかったことなど） | `vault/Knowledge/テーマ.md` | `Knowledge/_template.md` に従う。既存ノートがあれば追記 |
| ユーザーと方針・ルール・好みを決めた | `vault/Decisions/YYYY-MM-DD_要約.md` | `Decisions/_template.md` に従う |
| セッション終了時・作業の区切り | `vault/Daily/YYYY-MM-DD.md` | `Daily/_template.md` に従う。同日ファイルがあれば追記 |

- ユーザーが「これは覚えておいて」と言ったら、内容に応じて上記のいずれかのフォルダに即座に記録する
- `_template.md` と各フォルダの `README.md` は運用ルールそのものなので、上書き・削除しない（ルール変更の指示があった場合のみ更新する）

## このリポジトリについて

- `vault/` — Obsidian 保管庫（外部記憶の本体）。詳細は `vault/HOME.md`
- `docs/SETUP.md` — この仕組みのセットアップ手順書
- `.mcp.json` — mcp-obsidian（Local REST API 連携）の設定。`OBSIDIAN_API_KEY` は環境変数で渡す
- `generate_stickers.py` / `output/` — 既存のステッカー生成スクリプト（外部記憶システムとは無関係）
