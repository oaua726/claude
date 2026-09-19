# 業務AI化ワークスペース

木の香の家・田中さんの業務効率化のためのSkill・チェックリスト・運用ルール置き場。
このリポジトリを開いてClaude Codeセッションを始めると、以下のSkillが自動で使える。

## Skill(呼び出し方)

| Skill | 呼び出し方 | やること |
|---|---|---|
| `/asa-brief` | 「朝ブリーフィングして」 | 要返信メール・待ち案件・迫る期限・今日の予定を1画面に整理(読み取り専用) |
| `/mail-draft` | 「◯◯さんに△△のメール作って」 | 定型6パターンのGmail下書き作成。**送信はしない** |
| `/kigen` | 「期限まとめて」 | メールから期限を抽出して一覧化。カレンダー登録は確認後 |

## 外部脳(Obsidian)

`obsidian/` がそのまま Obsidian の Vault。セッションを跨いで文脈・決定事項・ナレッジを保持する。

| フォルダ | 入れるもの |
|---|---|
| `obsidian/Daily/` | その日の作業内容・引き継ぎ事項 |
| `obsidian/Decision/` | 判断・決定とその理由 |
| `obsidian/Knowledge/` | 解決した課題・エラー対処法・手順 |
| `obsidian/Mistakes/` | ミスの内容と正しい対処法(再発防止) |

- ローカルでは Obsidian で `obsidian/` フォルダを Vault として開く
- Claude はセッション開始時に Vault を読み、作業中に自動で記録する。手順は [CLAUDE.md](CLAUDE.md)
- **記録はコミット・pushして初めて次のセッションに引き継がれる**

## ドキュメント

| ファイル | 内容 |
|---|---|
| [CLAUDE.md](CLAUDE.md) | 外部脳の読み取り・記録・ミス管理ルール(セッション開始時に自動で読まれる) |
| [docs/gyomu-map.md](docs/gyomu-map.md) | 業務マップ、自動化候補17個、優先順位 |
| [docs/checklists.md](docs/checklists.md) | 書類・送信前チェックリスト(申請/銀行/上棟/見積/引き継ぎ) |
| [docs/unyo-rule.md](docs/unyo-rule.md) | ファイル命名規則、毎日のルーチン、AIに任せる範囲の線引き |
| [docs/next-steps.md](docs/next-steps.md) | 次に作るものの仕様書(Notion案件DB、週次レビュー自動化) |

## 安全ルール(要約)

- AIは**下書きまで**。メール送信は必ず本人
- 既存ファイル・Notionページ・予定の変更/削除はAIにさせない
- カレンダー登録・Notion追加は都度確認してから
- 詳細は [docs/unyo-rule.md](docs/unyo-rule.md)

## その他

- `generate_stickers.py` — レトロフューチャー系ステッカー生成(個人制作)。`pip install -r requirements.txt` → `python generate_stickers.py` で `output/` に8枚生成
