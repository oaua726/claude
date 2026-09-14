# 業務AI化ワークスペース

木の香の家・田中さんの業務効率化のためのSkill・チェックリスト・運用ルール置き場。
このリポジトリを開いてClaude Codeセッションを始めると、以下のSkillが自動で使える。

## Skill(呼び出し方)

| Skill | 呼び出し方 | やること |
|---|---|---|
| `/asa-brief` | 「朝ブリーフィングして」 | 要返信メール・待ち案件・迫る期限・今日の予定を1画面に整理(読み取り専用) |
| `/mail-draft` | 「◯◯さんに△△のメール作って」 | 定型6パターンのGmail下書き作成。**送信はしない** |
| `/kigen` | 「期限まとめて」 | メールから期限を抽出して一覧化。カレンダー登録は確認後 |

## ドキュメント

| ファイル | 内容 |
|---|---|
| [docs/gyomu-map.md](docs/gyomu-map.md) | 業務マップ、自動化候補16個、優先順位 |
| [docs/checklists.md](docs/checklists.md) | 書類・送信前チェックリスト(申請/銀行/上棟/見積/引き継ぎ) |
| [docs/unyo-rule.md](docs/unyo-rule.md) | ファイル命名規則、毎日のルーチン、AIに任せる範囲の線引き |
| [docs/next-steps.md](docs/next-steps.md) | 次に作るものの仕様書(Notion案件DB、週次レビュー自動化) |

## 安全ルール(要約)

- AIは**下書きまで**。メール送信は必ず本人
- 既存ファイル・Notionページ・予定の変更/削除はAIにさせない
- カレンダー登録・Notion追加は都度確認してから
- 詳細は [docs/unyo-rule.md](docs/unyo-rule.md)

## リポジトリ構成

```
.
├── .claude/skills/     Skill定義(Claude Codeが自動で読み込む)
│   ├── asa-brief/
│   ├── kigen/
│   └── mail-draft/     SKILL.md + templates.md(文例集)
├── docs/               業務マップ・チェックリスト・運用ルール・仕様書
└── README.md
```

このリポジトリは**業務用ドキュメントとSkillのみ**を置く。個人制作のスクリプトや
生成物(画像など)は含めない。認証情報(`.env`、各種トークンJSON)は
`.gitignore` 済みだが、そもそもコミットしないこと。
