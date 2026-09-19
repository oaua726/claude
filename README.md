# 業務AI化ワークスペース

木の香の家・田中さんの業務効率化のためのSkill・チェックリスト・運用ルール置き場。
このリポジトリを開いてClaude Codeセッションを始めると、以下のSkillが自動で使える。

やり取りは**その場で1件ずつ**Notionの「外部脳」に記録され、セッションを跨いで蓄積される。
保存先がNotionなので**PC・iPad・スマホのどこからでも同じ記憶が使える**
(ルール: [CLAUDE.md](CLAUDE.md) / 構成とスマホ運用: [docs/gaibunou.md](docs/gaibunou.md))。

## Skill(呼び出し方)

| Skill | 呼び出し方 | やること |
|---|---|---|
| `/asa-brief` | 「朝ブリーフィングして」 | 要返信メール・待ち案件・迫る期限・今日の予定を1画面に整理(読み取り専用) |
| `/mail-draft` | 「◯◯さんに△△のメール作って」 | 定型6パターンのGmail下書き作成。**送信はしない** |
| `/kigen` | 「期限まとめて」 | メールから期限を抽出して一覧化。カレンダー登録は確認後 |
| `/kioku` | 「記録して」「前回どこまで?」 | 外部脳(Notion)へ高頻度記録/想起。指示・訂正・好みは**原文のまま**残す |

## ドキュメント

| ファイル | 内容 |
|---|---|
| [CLAUDE.md](CLAUDE.md) | 外部脳(Notion)の運用ルール(読み取り・自動記録・ミス管理) |
| [docs/gaibunou.md](docs/gaibunou.md) | 外部脳の構成、**スマホ・iPadでの使い方**、安全ルール |
| [docs/gyomu-map.md](docs/gyomu-map.md) | 業務マップ、自動化候補17個、優先順位 |
| [docs/checklists.md](docs/checklists.md) | 書類・送信前チェックリスト(申請/銀行/上棟/見積/引き継ぎ) |
| [docs/unyo-rule.md](docs/unyo-rule.md) | ファイル命名規則、毎日のルーチン、AIに任せる範囲の線引き |
| [docs/next-steps.md](docs/next-steps.md) | 次に作るものの仕様書(Notion案件DB、週次レビュー自動化) |

## 外部脳(Notion)

記録の本体: [セッション記録DB](https://www.notion.so/1e2c4dae328f4bfbbda6b521172fb2b4)(1件=1行)
親ページ: [外部脳](https://www.notion.so/377f6728bc1e8176b2cae224332401d5)

| デバイス | 起動方法 | できること |
|---|---|---|
| PC(Claude Code) | 自動、または `/kioku` | 記憶の読み書き＋全Skill |
| スマホ・iPad | **「外部脳モードで」と打つ** | 記憶の読み書き(Skillは使えない) |

- 記録は**セッション終了時ではなく、決定・指示・訂正が出た瞬間に1行ずつ**
- 粒度は「**指示・訂正・好みは原文のまま、作業内容は要約**」
- 種別(指示/決定/ナレッジ/ミス/作業/好み・文体/事実)・案件・重要度で絞って想起する
- 詳細とスマホ運用は [docs/gaibunou.md](docs/gaibunou.md)

## 安全ルール(要約)

- AIは**下書きまで**。メール送信は必ず本人
- 外部脳への書き込みは**追記のみ**。削除・選択肢の追加・DB/サブページ新設はしない
- 外部脳に残すのは施主名・金額まで。**電話番号・住所・口座情報・APIキーは書かない**
- 既存ファイル・Notionページ・予定の変更/削除はAIにさせない
- カレンダー登録・Notion追加は都度確認してから
- 詳細は [docs/unyo-rule.md](docs/unyo-rule.md)

## その他

- `generate_stickers.py` — レトロフューチャー系ステッカー生成(個人制作)。`pip install -r requirements.txt` → `python generate_stickers.py` で `output/` に8枚生成
