# Obsidian外部記憶 セットアップ手順

Claude CodeからローカルのObsidian Vaultを読み書きできるようにする手順。
接続方式は **Obsidian Local REST API プラグイン + mcp-obsidian(MCPサーバ)**。

運用ルール本体はリポジトリ直下の [CLAUDE.md](../CLAUDE.md)。

---

## 全体像

```
Claude Code  ──MCP──▶  mcp-obsidian  ──HTTPS──▶  Obsidian Local REST API  ──▶  Vault(.md)
                                                  (Obsidianが起動している必要あり)
```

この方式のメリット/デメリット:

- ✅ Obsidianのタグ検索・デイリーノート等の機能をそのまま使える
- ✅ Obsidian上の表示と即座に同期する
- ⚠️ **Obsidianアプリを起動していないと接続できない**(作業前に起動する)
- ⚠️ APIキーの管理が必要

---

## 1. Obsidian側の準備

### 1-1. Vaultを作る

Obsidianを起動 →「新規Vaultを作成」。名前は任意(例: `業務メモ`)。
保存先は**クラウド同期フォルダ配下を推奨**(iCloud/Dropbox等。PC買い替え・故障時に記憶を失わないため)。

### 1-2. フォルダとテンプレートを配置

このリポジトリの `obsidian-vault-template/` の中身を、作ったVaultのルートにコピーする。

```
Vault/
  Daily/
  Decision/
  Knowledge/
  Mistakes/
  _templates/
  README.md
```

### 1-3. Local REST API プラグインを入れる

1. Obsidian → 設定 → **コミュニティプラグイン** → 「制限モード」をオフ
2. 「閲覧」→ `Local REST API` を検索 → インストール → **有効化**
3. 設定 → Local REST API を開き、表示されている **API Key をコピー**しておく
4. 同画面で待ち受けポートを確認する(既定: HTTPS `27124` / HTTP `27123`)

---

## 2. MCPサーバの登録

`mcp-obsidian` を Claude Code に登録する。`uv` が必要(未導入なら先に `brew install uv` 等)。

### コマンドで登録する場合

```bash
claude mcp add obsidian \
  --env OBSIDIAN_API_KEY=ここにAPIキー \
  --env OBSIDIAN_HOST=127.0.0.1 \
  --env OBSIDIAN_PORT=27124 \
  -- uvx mcp-obsidian
```

### 設定ファイルに直接書く場合

`~/.claude.json`(ユーザー設定)の `mcpServers` に追記:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uvx",
      "args": ["mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "ここにAPIキー",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27124"
      }
    }
  }
}
```

> **APIキーはこのGitリポジトリにコミットしない。** ユーザー設定側に書くこと。
> リポジトリに `.mcp.json` を置く場合は、値を直書きせず `${OBSIDIAN_API_KEY}` の形で環境変数を参照する。

---

## 3. 動作確認

1. **Obsidianを起動しておく**(必須)
2. Claude Codeを再起動し、`/mcp` で `obsidian` が `connected` になっているか確認
3. 「Vaultのファイル一覧を出して」と依頼 → `Daily/` `Decision/` 等が返れば成功

使えるツール名は `/mcp` の一覧で確認できる。おおよそ以下が揃う:

| 用途 | ツール(例) |
|---|---|
| ファイル一覧 | `obsidian_list_files_in_vault` / `obsidian_list_files_in_dir` |
| 読み取り | `obsidian_get_file_contents` / `obsidian_batch_get_file_contents` |
| 検索 | `obsidian_simple_search` / `obsidian_complex_search` |
| 追記 | `obsidian_append_content` |
| 部分更新 | `obsidian_patch_content` |
| 新規作成・全文置換 | `obsidian_put_content` |

書き込みは原則 `obsidian_append_content`(追記)を使う。
`obsidian_put_content` は**新規作成のときだけ**。既存ノートへの全文置換は記憶の破壊にあたるので使わない。

---

## 4. つながらないとき

| 症状 | 原因と対処 |
|---|---|
| `/mcp` に出ない | Claude Codeを再起動。設定ファイルのJSONが壊れていないか確認 |
| connection refused | **Obsidianが起動していない**。起動してから再試行 |
| 401 / Unauthorized | APIキーの貼り間違い。プラグイン設定から再コピー |
| 証明書エラー | HTTPSの自己署名証明書が原因。`OBSIDIAN_PORT=27123`(HTTP)を試す。ローカル接続のみなので実用上は許容 |
| ファイルが見つからない | パスはVaultルートからの相対(例: `Daily/2026-09-19.md`)。先頭に `/` を付けない |

---

## 5. 運用メモ

- 作業開始前にObsidianを起動する習慣をつける(接続の前提条件)
- Vaultはクラウド同期フォルダに置き、**記憶を1台のPCに依存させない**
- Vaultの中身はただのMarkdown。将来ほかのAIツールに乗り換えるときもそのまま持ち出せる
- 記憶が増えてきて探しにくくなったら、`Knowledge/` のノートをテーマ単位で統合する(分割より統合)
