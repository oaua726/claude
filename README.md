# 業務AI化ワークスペース

木の香の家・田中さんの業務効率化のためのSkill・チェックリスト・運用ルール置き場。
このリポジトリを開いてClaude Codeセッションを始めると、以下のSkillが自動で使える。

セッションを跨いだ文脈・決定事項・ナレッジは、ローカルのObsidian Vaultに**外部記憶**として蓄積する
(ルール: [CLAUDE.md](CLAUDE.md) / セットアップ: [docs/obsidian-setup.md](docs/obsidian-setup.md))。

## Skill(呼び出し方)

| Skill | 呼び出し方 | やること |
|---|---|---|
| `/asa-brief` | 「朝ブリーフィングして」 | 要返信メール・待ち案件・迫る期限・今日の予定を1画面に整理(読み取り専用) |
| `/mail-draft` | 「◯◯さんに△△のメール作って」 | 定型6パターンのGmail下書き作成。**送信はしない** |
| `/kigen` | 「期限まとめて」 | メールから期限を抽出して一覧化。カレンダー登録は確認後 |
| `/kioku` | 「記録して」「前回どこまで?」 | Obsidianへ作業記録・決定・ナレッジ・ミスを追記/想起。**追記のみ** |

## ドキュメント

| ファイル | 内容 |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Obsidian外部記憶の運用ルール(読み取り・自動記録・ミス管理) |
| [docs/obsidian-setup.md](docs/obsidian-setup.md) | Obsidian接続のセットアップ手順(Local REST API + mcp-obsidian) |
| [docs/gyomu-map.md](docs/gyomu-map.md) | 業務マップ、自動化候補17個、優先順位 |
| [docs/checklists.md](docs/checklists.md) | 書類・送信前チェックリスト(申請/銀行/上棟/見積/引き継ぎ) |
| [docs/unyo-rule.md](docs/unyo-rule.md) | ファイル命名規則、毎日のルーチン、AIに任せる範囲の線引き |
| [docs/next-steps.md](docs/next-steps.md) | 次に作るものの仕様書(Notion案件DB、週次レビュー自動化) |

## 外部記憶(Obsidian)

| フォルダ | 入れるもの |
|---|---|
| `Daily/` | その日の作業記録・引き継ぎ |
| `Decision/` | 判断・決定とその理由 |
| `Knowledge/` | 解決した課題・手順・設定 |
| `Mistakes/` | ミスと正しい対処法(再発防止) |

- Vaultの雛形は [obsidian-vault-template/](obsidian-vault-template/)。中身をVaultルートにコピーして使う
- 案件別フォルダは作らない。案件はフロントマターの `project:` とタグで区別する
- **Obsidianアプリを起動していないと接続できない**(作業前に起動する)

## 安全ルール(要約)

- AIは**下書きまで**。メール送信は必ず本人
- Obsidianへの書き込みは**追記のみ**。既存記述の削除・上書きはしない
- パスワード・口座情報・APIキーはVaultにも書かない
- 既存ファイル・Notionページ・予定の変更/削除はAIにさせない
- カレンダー登録・Notion追加は都度確認してから
- 詳細は [docs/unyo-rule.md](docs/unyo-rule.md)

## その他

- `generate_stickers.py` — レトロフューチャー系ステッカー生成(個人制作)。`pip install -r requirements.txt` → `python generate_stickers.py` で `output/` に8枚生成
