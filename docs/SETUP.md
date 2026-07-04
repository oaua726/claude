# Claude Code × Obsidian「外部記憶」セットアップ手順

Claude Code と Obsidian を連携させ、Obsidian を Claude の「外部脳（外部記憶）」として機能させるための手順書です。
セッションをまたいで記憶が引き継がれるため、Claude が「昨日の続き」から作業を再開でき、同じミスを繰り返さなくなります。

> **注意**: MCP の設定や外部ツールの利用はセキュリティ面を考慮し、自己責任で行ってください。

## 1. 事前準備

| ツール | 内容 |
| --- | --- |
| **Claude Code** | 月額制の **Pro プラン（または Max プラン）** での利用が前提。<https://claude.ai/code> |
| **Obsidian** | 公式サイト <https://obsidian.md> からダウンロードしてインストール |
| **uv（uvx）** | mcp-obsidian の実行に使用。<https://docs.astral.sh/uv/getting-started/installation/> |

このリポジトリをクローンしたら、Obsidian で「保管庫としてフォルダを開く」を選び、**リポジトリ内の `vault/` フォルダ**を保管庫として開いてください。ノート保存用の専用フォルダはこれで準備完了です。

## 2. MCP（Model Context Protocol）の設定 — REST API 方式

MCP は Claude と Obsidian を繋ぐ「パイプ」の役割を果たします。このリポジトリでは [mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian)（Obsidian の Local REST API 経由）を使う設定を `.mcp.json` に同梱しています。

### 2-1. Obsidian 側: Local REST API プラグインの導入

1. Obsidian の **設定 → コミュニティプラグイン** で制限モードをオフにする
2. 「閲覧」から **Local REST API** を検索してインストールし、有効化する
3. プラグイン設定画面に表示される **API Key をコピー**する
   - デフォルトでは HTTPS ポート `27124` で待ち受けます

### 2-2. Claude Code 側: 環境変数の設定

API キーは `.mcp.json` に直接書かず、環境変数で渡します（キーの流出防止）。シェルの設定ファイル（`~/.zshrc` や `~/.bashrc` など）に追記してください。

```bash
export OBSIDIAN_API_KEY="コピーしたAPIキー"
# 必要に応じて（デフォルトのままなら不要）
# export OBSIDIAN_HOST="127.0.0.1"
# export OBSIDIAN_PORT="27124"
```

### 2-3. 接続確認

Obsidian を起動した状態で、このリポジトリのルートで Claude Code を起動し、次を確認します。

```bash
claude mcp list
```

`obsidian` が **connected** と表示されれば成功です。初回はプロジェクトの `.mcp.json` を使用してよいか確認されるので許可してください。

### 2-4. うまくいかない場合 — ファイル直接アクセスへのフォールバック

REST API の接続に失敗しても、**この仕組みは動きます**。Obsidian のノートはただの Markdown ファイルなので、Claude Code は標準の Read / Write ツールで `vault/` を直接読み書きできます。このフォールバックは `CLAUDE.md` のルールとして明文化済みで、Claude が自動的に切り替えます。

よくあるつまずき:

- **connection refused** → Obsidian 本体が起動していない／Local REST API プラグインが無効
- **401 エラー** → `OBSIDIAN_API_KEY` の値が違う（シェルを再起動して反映されているか確認）
- **証明書エラー** → Local REST API は自己署名証明書を使うため、プラグイン設定で HTTP（デフォルトはポート `27123`）を有効にし `OBSIDIAN_PORT` を合わせる方法もあります

## 3. Claude への基本ルール

「Claude に3つのルールをチャットで伝えて覚えさせる」工程は、このリポジトリでは **`CLAUDE.md` にあらかじめ記述済み**です（Claude Code はセッション開始時に `CLAUDE.md` を自動で読み込みます）。

1. **前提条件の共有** — あなたは私のアシスタントであり、Obsidian を外部脳（外部記憶）として使用する
2. **読み取りルール** — 新しいセッションを開始する前に、必ず Obsidian の中身を確認しに行く（記憶喪失の防止）
3. **書き込みルール** — ミス・知見・決定事項・日次記録を、対応するフォルダへ自動で記録する

ルールを変えたくなったら、チャットで指示するか `CLAUDE.md` を直接編集してください。

## 4. フォルダ構成と運用

```
vault/
├── HOME.md          # 入口。運用ルールの索引
├── Mistakes/        # ミスと修正方法。毎回参照させることで同じミスを繰り返さない
├── Knowledge/       # プロジェクトで得た知見・問題の対処法
├── Decisions/       # どんな時にどう判断したか。ルール・判断基準
└── Daily/           # 日次の作業記録。翌日「昨日の続き」から再開
```

各フォルダに `README.md`（記入ルール）と `_template.md`（ノートの書式）が入っています。

## 5. 設定のコツ

- **徐々にカスタマイズする**: 最初から完璧なルールを作る必要はありません。使いながら「これは覚えておいて」「セッション開始時にここを確認して」と Claude に直接伝えて、徐々にルールを肉付けしていくことで、自分好みの「相棒」に育てていけます
- **記録は Claude 任せでよい**: 書き込みルールにより、ミスの修正や決定事項は Claude が自発的に記録します。記録漏れに気づいたら「今のを Mistakes に残して」と一言伝えれば OK
- **自己責任での構築**: MCP はローカルの Obsidian への読み書き権限を Claude に与えるものです。API キーの管理を含め、セキュリティ面は自己責任で運用してください

これらの設定により、AI が単なるチャット相手ではなく、「長年連れ添った秘書」のように最小限の指示で意図を汲み取ってくれる存在になっていきます。
