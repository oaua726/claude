---
name: kioku
description: Obsidian外部記憶への記録・想起。作業内容をDaily/Decision/Knowledge/Mistakesに分類してObsidian Vaultへ追記する。「記録して」「Obsidianに書いといて」「今日の分まとめて」「前回どこまでやったか思い出して」「/kioku」で起動。追記のみで既存記述の削除・上書きはしない。
---

# 記憶 (kioku)

ObsidianVaultを外部記憶として読み書きする。分類ルールとVault構成は `CLAUDE.md` が正。
接続手順は `docs/obsidian-setup.md`。**Obsidianアプリが起動していないと接続できない。**

このSkillは**追記専用**。既存ノートの削除・全文置換は行わない。

---

## モードA: 記録する(既定)

「記録して」「Obsidianに書いといて」「今日の分まとめて」等で起動。

### 1. 書くことを分類する

今回のセッションで発生した事柄を、以下に振り分ける。**該当なしのカテゴリは作らない。**

| 分類 | 該当するもの | 保存先 |
|---|---|---|
| Daily | その日やったこと、次やること、引き継ぎ | `Daily/YYYY-MM-DD.md` |
| Decision | 選んだ・決めた・方針を変えた | `Decision/YYYYMMDD_件名.md` |
| Knowledge | 課題/エラーを解決した、手順が固まった | `Knowledge/テーマ名.md` |
| Mistake | ミスをした、指示と違って指摘・修正を受けた | `Mistakes/YYYYMMDD_ミスの要約.md` |

書かないもの: 未確定の推測、単なる会話の要約、**パスワード・口座情報・APIキー等の秘匿情報**。

### 2. 既存ノートを確認する

- `obsidian_get_file_contents` で保存先の存在を確認する
- Knowledgeは `obsidian_simple_search` で**同テーマの既存ノートを探し、あれば追記して育てる**(新規乱立させない)
- Daily は同日ファイルがあれば追記

### 3. 書く

- **新規作成**: `obsidian_put_content`。`obsidian-vault-template/_templates/` の対応テンプレートの構成に従う
- **既存へ追記**: `obsidian_append_content`(既定)。特定セクションに入れるなら `obsidian_patch_content`
- **`obsidian_put_content` を既存ファイルに使わない**(全文置換=記憶の破壊)

フロントマターは必ず付ける:

```yaml
---
type: daily | decision | knowledge | mistake
date: YYYY-MM-DD
project: ◯◯様邸        # 案件に紐づかないなら 全体
tags: [案件/◯◯様邸, 申請]
---
```

Daily から Decision/Knowledge/Mistakes へ `[[ノート名]]` で相互リンクを張る。

### 4. 報告する

どのノートに何を書いたかを、必ずこの形式で報告する。

```
記録しました:
- Daily/2026-09-19.md (追記) — 本日の作業3件・引き継ぎ2件
- Decision/20260919_見積の版管理方法.md (新規) — 旧版をold/に退避すると決めた理由
- Mistakes/20260919_宛先の敬称漏れ.md (新規) — 再発防止チェック付き
```

---

## モードB: 思い出す

「前回どこまでやったか」「◯◯様邸の経緯教えて」等で起動。

1. `Daily/` の直近3日分を読む
2. 案件が特定できるなら、その `project:` / タグで `obsidian_complex_search` を掛け、
   `Decision/` `Knowledge/` の関連ノートを読む
3. これからやる作業に関係する `Mistakes/` を検索する
4. 「前回の進捗 / 決定済みの前提 / 注意すべき過去のミス」の3点に整理して報告する

該当記録がなければ「過去記録なし」と明示する。憶測で埋めない。

---

## エラー時

MCPが繋がっていない場合は**黙って進めない**。以下を伝える。

```
Obsidianに接続できませんでした(Obsidianアプリが起動しているか確認してください)。
記録内容を以下に出力します。手で貼り付けてください:
（ここにMarkdown全文）
```

記録内容そのものは必ず出力する。接続不可を理由に記憶を捨てない。
