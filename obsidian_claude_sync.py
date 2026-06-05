#!/usr/bin/env python3
"""
Claudeとの対話をObsidianノートとして保存するツール。

使い方:
  python obsidian_claude_sync.py --vault /path/to/vault save --title "会話タイトル"
  python obsidian_claude_sync.py --vault /path/to/vault import conversation.json
  python obsidian_claude_sync.py --vault /path/to/vault list
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_FOLDER = "Claude"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"


def build_frontmatter(title: str, tags: list[str], created_at: datetime) -> str:
    tag_str = "\n".join(f"  - {t}" for t in tags)
    return (
        "---\n"
        f"title: \"{title}\"\n"
        f"date: {created_at.strftime(DATE_FORMAT)}\n"
        f"time: {created_at.strftime(TIME_FORMAT)}\n"
        "tags:\n"
        f"{tag_str}\n"
        "source: Claude\n"
        "---\n"
    )


def messages_to_markdown(messages: list[dict]) -> str:
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if role == "user":
            lines.append(f"### You\n\n{content}\n")
        elif role == "assistant":
            lines.append(f"### Claude\n\n{content}\n")
        else:
            lines.append(f"### {role}\n\n{content}\n")
    return "\n---\n\n".join(lines)


def save_note(vault: Path, title: str, messages: list[dict], tags: list[str]) -> Path:
    now = datetime.now()
    folder = vault / DEFAULT_FOLDER / now.strftime(DATE_FORMAT)
    folder.mkdir(parents=True, exist_ok=True)

    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
    filename = f"{now.strftime('%H%M')}_{safe_title}.md"
    note_path = folder / filename

    frontmatter = build_frontmatter(title, tags, now)
    body = messages_to_markdown(messages)
    header = f"# {title}\n\n"

    note_path.write_text(frontmatter + header + body, encoding="utf-8")
    return note_path


def load_conversation_json(path: str) -> tuple[str, list[dict]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Claude API形式: {"messages": [...], "title": "..."}
    if isinstance(data, dict) and "messages" in data:
        title = data.get("title", Path(path).stem)
        messages = data["messages"]
    # メッセージ配列のみ
    elif isinstance(data, list):
        title = Path(path).stem
        messages = data
    else:
        raise ValueError("サポートされていない形式です。messages配列またはAPIレスポンスJSONを指定してください。")

    return title, messages


def list_notes(vault: Path) -> None:
    claude_dir = vault / DEFAULT_FOLDER
    if not claude_dir.exists():
        print("まだObsidianに保存されたClaudeノートはありません。")
        return

    notes = sorted(claude_dir.rglob("*.md"))
    if not notes:
        print("ノートが見つかりません。")
        return

    print(f"{'日付':<12} {'タイトル'}")
    print("-" * 60)
    for note in notes:
        date = note.parent.name
        print(f"{date:<12} {note.stem}")


def cmd_save(args, vault: Path) -> None:
    messages: list[dict] = []

    print("対話を入力してください。'.' だけの行で終了します。")
    print("形式: user: <メッセージ> または assistant: <メッセージ>")
    print()

    current_role = None
    current_lines: list[str] = []

    def flush():
        if current_role and current_lines:
            messages.append({"role": current_role, "content": "\n".join(current_lines).strip()})

    for line in sys.stdin:
        line = line.rstrip("\n")
        if line == ".":
            flush()
            break
        if line.lower().startswith("user:"):
            flush()
            current_role = "user"
            current_lines = [line[5:].strip()]
        elif line.lower().startswith("assistant:") or line.lower().startswith("claude:"):
            flush()
            current_role = "assistant"
            current_lines = [line.split(":", 1)[1].strip()]
        else:
            current_lines.append(line)

    if not messages:
        print("メッセージが入力されませんでした。")
        return

    tags = args.tags or ["claude", "ai", "conversation"]
    note_path = save_note(vault, args.title, messages, tags)
    print(f"\nノートを保存しました: {note_path}")


def cmd_import(args, vault: Path) -> None:
    try:
        title, messages = load_conversation_json(args.file)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"エラー: {e}")
        sys.exit(1)

    if args.title:
        title = args.title

    tags = args.tags or ["claude", "ai", "conversation"]
    note_path = save_note(vault, title, messages, tags)
    print(f"ノートを保存しました: {note_path}")


def cmd_list(args, vault: Path) -> None:
    list_notes(vault)


def cmd_export_template(args, vault: Path) -> None:
    """Claude API形式のJSONテンプレートを出力する。"""
    template = {
        "title": "会話タイトルをここに入力",
        "messages": [
            {"role": "user", "content": "こんにちは"},
            {"role": "assistant", "content": "こんにちは！どのようにお手伝いできますか？"},
        ],
    }
    print(json.dumps(template, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ClaudeとObsidian連携ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--vault",
        default=os.environ.get("OBSIDIAN_VAULT", str(Path.home() / "Documents" / "ObsidianVault")),
        help="ObsidianのVaultパス (環境変数 OBSIDIAN_VAULT でも設定可)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # save コマンド
    p_save = subparsers.add_parser("save", help="対話を入力してノート保存")
    p_save.add_argument("--title", default="Claude対話", help="ノートのタイトル")
    p_save.add_argument("--tags", nargs="+", help="タグリスト")
    p_save.set_defaults(func=cmd_save)

    # import コマンド
    p_import = subparsers.add_parser("import", help="JSON形式の対話ファイルをインポート")
    p_import.add_argument("file", help="インポートするJSONファイルのパス")
    p_import.add_argument("--title", help="ノートのタイトル（省略時はJSONから取得）")
    p_import.add_argument("--tags", nargs="+", help="タグリスト")
    p_import.set_defaults(func=cmd_import)

    # list コマンド
    p_list = subparsers.add_parser("list", help="保存済みノートの一覧表示")
    p_list.set_defaults(func=cmd_list)

    # template コマンド
    p_tmpl = subparsers.add_parser("template", help="JSONテンプレートを出力")
    p_tmpl.set_defaults(func=cmd_export_template)

    args = parser.parse_args()
    vault = Path(args.vault).expanduser()

    args.func(args, vault)


if __name__ == "__main__":
    main()
