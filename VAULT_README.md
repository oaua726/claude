---
date: 2026-06-21
tags: [meta, vault]
project: obsidian-vault
---

# Obsidian Vault (Git-backed)

このリポジトリを「外部脳」Vaultとして使う。Obsidianアプリでこのフォルダを
Vaultとして開けば、AIが書いたノートをそのまま閲覧・編集できる。

## フォルダの役割

- `Knowledge/` — 技術的な知見・解決したバグ・新しい発見。`Knowledge/mistakes.md` はAIのミス記録。
- `Decisions/` — 判断・選択・方針決定の記録。
- `Projects/` — 進行中プロジェクトの状態・バージョン・概要。
- `Preferences/` — ユーザーの好み・作業スタイル。

## 命名規則

- Knowledge: `topic-subtopic.md`（例: `nextjs-auth-cookie.md`）
- Decisions: `YYYY-MM-DD-topic.md`（例: `2026-05-16-database-choice.md`）
- Preferences: `category.md`（例: `coding-style.md`）
- Projects: `project-name.md`

## ノート形式

各ノートには YAML フロントマター（date / tags / project / related）を付け、
関連ノートには `[[wiki link]]` でリンクする。
