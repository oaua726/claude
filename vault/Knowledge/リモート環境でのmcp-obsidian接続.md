# リモート環境での mcp-obsidian 接続

- **日付**: 2026-07-12
- **タグ**: #knowledge

## 背景

`.mcp.json` に設定した mcp-obsidian の接続確認をリモート実行環境（Claude Code on the web のコンテナ）で試みた。

## 内容

- リモート環境でも mcp-obsidian サーバー自体は起動し、`mcp__obsidian__*` ツールは**一覧に現れる**
- しかし実際に呼び出すと `Connection refused (127.0.0.1:27124)` で失敗する。Obsidian 本体（Local REST API プラグイン）はユーザーのローカルPCでしか動いていないため
- つまり「MCP ツールが存在すること」と「接続できること」は別。**ツール呼び出しが接続エラーになったら、即座にファイル直接アクセス（Read/Write で `vault/` を読み書き）へフォールバックする**（CLAUDE.md のルール通り）
- REST API の実接続確認は、ローカルPCで Obsidian を起動した状態で `claude mcp list` → `obsidian: connected` を見るのが確実（`docs/SETUP.md` §2-3）

## 参照

- `CLAUDE.md` — 接続方式（MCP 優先・フォールバック）のルール
- `docs/SETUP.md` §2-4 — フォールバックとトラブルシューティング
