# Claude Code 設定 — Obsidian 外部脳

## 役割の定義

あなたは私の長期的なアシスタントです。**Obsidianのnotesフォルダ（このリポジトリの `notes/` ディレクトリ）を外部脳（外部記憶）として使用します。** GitHubリポジトリ `oaua726/claude` の `notes/` 配下に記録を蓄積し、セッションをまたいで記憶を引き継ぎます。

---

## セッション開始時の必須手順

**新しいセッションを開始するたびに、必ず以下の順番で実行すること：**

1. **今日のデイリーノートを確認・作成**
   - `notes/Daily/YYYY-MM-DD.md` を `mcp__github__get_file_contents` で取得する
   - 存在しない場合は `notes/Templates/Daily.md` の形式で新規作成する

2. **ミスノートを確認**
   - `notes/Mistakes/` ディレクトリの内容を確認する
   - 今回の作業に関連するミスがあれば読み込む（同じミスを繰り返さないため）

3. **関連する過去ノートを検索**
   - 今日のタスクに関連するキーワードで `mcp__github__search_code` を使って検索する
   - 関連するKnowledge・Decisionsノートがあれば読み込む

---

## 記録ルール（いつ書くか）

### 即座に記録すること

| 状況 | 保存先 | テンプレート |
|------|--------|------------|
| ミス・バグ・誤解が発生した | `notes/Mistakes/YYYY-MM-DD-タイトル.md` | Mistake.md |
| 重要な技術知識を得た | `notes/Knowledge/タイトル.md` | Knowledge.md |
| 設計上の決定をした | `notes/Decisions/YYYY-MM-DD-タイトル.md` | Decision.md |
| 作業を完了した・区切りがついた | `notes/Daily/YYYY-MM-DD.md` に追記 | — |

### セッション終了時に記録すること

- 今日やったことの要約を `notes/Daily/YYYY-MM-DD.md` に書く
- 次回に引き継ぐべきタスクを「次回のタスク」セクションに記載する

---

## GitHubMCPツールの使い方

### ノートを読む
```
mcp__github__get_file_contents
  owner: oaua726
  repo: claude
  path: notes/Daily/2026-06-26.md
```

### ノートを新規作成・更新する
```
mcp__github__create_or_update_file
  owner: oaua726
  repo: claude
  path: notes/Daily/2026-06-26.md
  message: "Add daily note for 2026-06-26"
  content: <base64エンコードされたマークダウン>
  branch: main
  sha: <既存ファイルを更新する場合は現在のSHAを指定>
```

> **重要**: 既存ファイルを更新する際は、まず `get_file_contents` で現在の `sha` を取得してから `create_or_update_file` を呼ぶこと。SHA なしで更新しようとするとエラーになる。

### ノートを検索する
```
mcp__github__search_code
  q: "検索キーワード repo:oaua726/claude path:notes/"
```

### ディレクトリ一覧を見る
```
mcp__github__get_file_contents
  owner: oaua726
  repo: claude
  path: notes/Mistakes
```
（ディレクトリを指定するとファイル一覧が返る）

---

## フォルダ構成

```
notes/
├── Daily/          # 日次記録（YYYY-MM-DD.md）
├── Mistakes/       # ミス・問題の記録
├── Knowledge/      # 技術知識・ノウハウ
├── Decisions/      # 設計・方針の決定事項
└── Templates/      # 各ノートのテンプレート
    ├── Daily.md
    ├── Mistake.md
    ├── Knowledge.md
    └── Decision.md
```

---

## Obsidian Git（iPhone連携）の設定

このリポジトリの `notes/` フォルダはObsidianのVaultとして使えます。

**iPhoneでの設定手順：**
1. **Working Copy**（iOS Git アプリ）でこのリポジトリをクローン
2. **Obsidian** → 設定 → コミュニティプラグイン → **Obsidian Git** をインストール
3. Obsidian Git の設定で `notes/` フォルダをVaultのルートに設定
4. 自動プル間隔を設定（例：10分ごと）

これにより、Claudeがノートを更新すると自動的にiPhoneのObsidianに反映されます。

---

## 運用のコツ

- **ルールは徐々に育てる**: 使いながら「これも覚えて」と追記していく
- **検索してから答える**: 過去に調べたことは必ず検索してから回答する
- **同じミスをしない**: Mistakesフォルダを毎回確認し、パターンを把握する
- **具体的に書く**: 「バグを直した」ではなく「〇〇の関数でXXするとNullPointerが出る問題を、YYに変更して修正した」と書く
