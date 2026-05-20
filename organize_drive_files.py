#!/usr/bin/env python3
"""
Google Drive マイドライブ ファイル名整理スクリプト

機能:
  1. URLエンコードされたファイル名を日本語に修正
  2. ランダムな英数字ファイル名を特定（手動確認用）
  3. 重複ファイルを検出して整理
  4. 命名規則を統一（末尾スペース除去、様ー → 様-）

使い方:
  python organize_drive_files.py              # ドライラン（デフォルト）
  python organize_drive_files.py --apply      # AUTO修正を実行
  python organize_drive_files.py --fix-encoding --dry-run
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from urllib.parse import unquote

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive"]

_RANDOM_NAME_RE = re.compile(r"^[0-9a-z]{20,}$")
_SEPARATOR_RE = re.compile(r"(様)ー")
_PCT_ENCODED_RE = re.compile(r"%[0-9A-Fa-f]{2}")


# ---------------------------------------------------------------------------
# データモデル
# ---------------------------------------------------------------------------

class FixCategory(Enum):
    URL_DECODE = "url_encoding"
    RANDOM_NAME = "random_name"
    DUPLICATE = "duplicate"
    NAME_CONVENTION = "name_convention"


class FixAction(Enum):
    RENAME = "rename"
    TRASH = "trash"
    REVIEW = "review"


@dataclass
class DriveFile:
    id: str
    name: str
    mime_type: str
    size: int | None
    created_time: datetime
    modified_time: datetime
    md5: str | None


@dataclass
class Fix:
    category: FixCategory
    action: FixAction
    file: DriveFile
    new_name: str | None = None
    reason: str = ""
    confidence: str = "AUTO"
    related_file: DriveFile | None = None


# ---------------------------------------------------------------------------
# 認証
# ---------------------------------------------------------------------------

def get_drive_service(credentials_path: str = "credentials.json",
                      token_path: str = "token.json"):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as fh:
            fh.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# ファイル取得
# ---------------------------------------------------------------------------

def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def fetch_all_my_drive_files(service) -> list[DriveFile]:
    files: list[DriveFile] = []
    page_token = None
    while True:
        resp = service.files().list(
            q="'root' in parents and trashed = false",
            pageSize=1000,
            fields=(
                "nextPageToken,"
                "files(id,name,mimeType,size,createdTime,modifiedTime,md5Checksum)"
            ),
            pageToken=page_token,
        ).execute()
        for f in resp.get("files", []):
            files.append(DriveFile(
                id=f["id"],
                name=f["name"],
                mime_type=f.get("mimeType", ""),
                size=int(f["size"]) if f.get("size") else None,
                created_time=_parse_dt(f["createdTime"]),
                modified_time=_parse_dt(f["modifiedTime"]),
                md5=f.get("md5Checksum"),
            ))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files


# ---------------------------------------------------------------------------
# 分析: URLエンコード修正
# ---------------------------------------------------------------------------

def analyze_url_encoding(files: list[DriveFile]) -> list[Fix]:
    existing_names = {f.name for f in files}
    fixes: list[Fix] = []
    for f in files:
        if not _PCT_ENCODED_RE.search(f.name):
            continue
        decoded = unquote(f.name)
        if decoded == f.name:
            continue
        if decoded in existing_names:
            base, _, ext = decoded.rpartition(".")
            decoded = f"{base}_decoded.{ext}" if ext else f"{decoded}_decoded"
        fixes.append(Fix(
            category=FixCategory.URL_DECODE,
            action=FixAction.RENAME,
            file=f,
            new_name=decoded,
            reason="URLエンコードされたファイル名をデコード",
            confidence="AUTO",
        ))
    return fixes


# ---------------------------------------------------------------------------
# 分析: ランダム名フラグ
# ---------------------------------------------------------------------------

def analyze_random_names(files: list[DriveFile],
                         time_window_seconds: int = 120) -> list[Fix]:
    fixes: list[Fix] = []
    for f in files:
        stem = Path(f.name).stem
        if not _RANDOM_NAME_RE.match(stem):
            continue
        nearby = _find_nearby_file(f, files, time_window_seconds)
        if nearby:
            reason = (
                f"作成時刻が {nearby.name!r} と {_seconds_diff(f, nearby)}秒以内 "
                "- 重複アップロードの可能性あり"
            )
        else:
            reason = "近傍ファイルなし - 手動確認が必要"
        fixes.append(Fix(
            category=FixCategory.RANDOM_NAME,
            action=FixAction.REVIEW,
            file=f,
            reason=reason,
            confidence="REVIEW",
            related_file=nearby,
        ))
    return fixes


def _seconds_diff(a: DriveFile, b: DriveFile) -> int:
    return int(abs((a.created_time - b.created_time).total_seconds()))


def _find_nearby_file(target: DriveFile, files: list[DriveFile],
                      window: int) -> DriveFile | None:
    best: DriveFile | None = None
    best_diff = window + 1
    for f in files:
        if f.id == target.id:
            continue
        diff = _seconds_diff(target, f)
        if diff <= window and diff < best_diff:
            best_diff = diff
            best = f
    return best


# ---------------------------------------------------------------------------
# 分析: 重複検出
# ---------------------------------------------------------------------------

def _normalize_for_dedup(name: str) -> str:
    stem = Path(name).stem.strip()
    stem = re.sub(r"[\s　]+", " ", stem)
    stem = stem.replace("ー", "-")
    return stem.lower()


def analyze_duplicates(files: list[DriveFile]) -> list[Fix]:
    fixes: list[Fix] = []

    # 完全一致
    exact_groups: dict[str, list[DriveFile]] = defaultdict(list)
    for f in files:
        exact_groups[f.name].append(f)

    for name, group in exact_groups.items():
        if len(group) < 2:
            continue
        group_sorted = sorted(group, key=lambda x: x.modified_time, reverse=True)
        keep = group_sorted[0]
        for old in group_sorted[1:]:
            if keep.md5 and old.md5 and keep.md5 == old.md5:
                fixes.append(Fix(
                    category=FixCategory.DUPLICATE,
                    action=FixAction.TRASH,
                    file=old,
                    reason=f"完全一致の重複 (md5同一) - {keep.name!r} を保持",
                    confidence="AUTO",
                    related_file=keep,
                ))
            else:
                fixes.append(Fix(
                    category=FixCategory.DUPLICATE,
                    action=FixAction.REVIEW,
                    file=old,
                    reason=f"同名ファイルあり - 内容を確認して手動で整理してください",
                    confidence="REVIEW",
                    related_file=keep,
                ))

    # 近似一致（名前正規化後に衝突するもの）
    seen_exact = {f.id for group in exact_groups.values()
                  if len(group) > 1 for f in group}
    norm_groups: dict[str, list[DriveFile]] = defaultdict(list)
    for f in files:
        norm_groups[_normalize_for_dedup(f.name)].append(f)

    for norm, group in norm_groups.items():
        if len(group) < 2:
            continue
        if all(f.id in seen_exact for f in group):
            continue
        for f in group:
            if f.id not in seen_exact:
                fixes.append(Fix(
                    category=FixCategory.DUPLICATE,
                    action=FixAction.REVIEW,
                    file=f,
                    reason=(
                        f"近似名の重複グループ: "
                        + ", ".join(repr(x.name) for x in group)
                    ),
                    confidence="REVIEW",
                ))

    return fixes


# ---------------------------------------------------------------------------
# 分析: 命名規則統一
# ---------------------------------------------------------------------------

def analyze_name_conventions(files: list[DriveFile]) -> list[Fix]:
    fixes: list[Fix] = []
    for f in files:
        new_name = f.name
        # 末尾スペース除去（ASCII + 全角スペース）
        new_name = new_name.rstrip(" 　")
        # 様ー → 様- （語中のー伸音符は変更しない）
        new_name = _SEPARATOR_RE.sub(r"\1-", new_name)

        if new_name != f.name:
            reasons = []
            if f.name.rstrip(" 　") != f.name:
                reasons.append("末尾スペース除去")
            if _SEPARATOR_RE.search(f.name):
                reasons.append("セパレータ統一 (様ー → 様-)")
            fixes.append(Fix(
                category=FixCategory.NAME_CONVENTION,
                action=FixAction.RENAME,
                file=f,
                new_name=new_name,
                reason="、".join(reasons),
                confidence="AUTO",
            ))
    return fixes


# ---------------------------------------------------------------------------
# レポート出力
# ---------------------------------------------------------------------------

CATEGORY_LABELS = {
    FixCategory.URL_DECODE: "URLエンコード修正",
    FixCategory.RANDOM_NAME: "ランダム名 (要確認)",
    FixCategory.DUPLICATE: "重複ファイル",
    FixCategory.NAME_CONVENTION: "命名規則統一",
}


def print_report(fixes: list[Fix], dry_run: bool = True) -> None:
    mode = "ドライラン" if dry_run else "適用モード"
    print(f"\n{'='*60}")
    print(f"  Google Drive ファイル名整理レポート [{mode}]")
    print(f"{'='*60}")

    by_cat: dict[FixCategory, list[Fix]] = defaultdict(list)
    for fix in fixes:
        by_cat[fix.category].append(fix)

    auto_count = sum(1 for f in fixes if f.confidence == "AUTO")
    review_count = sum(1 for f in fixes if f.confidence == "REVIEW")

    for cat in FixCategory:
        cat_fixes = by_cat.get(cat, [])
        if not cat_fixes:
            continue
        label = CATEGORY_LABELS[cat]
        print(f"\n[{label}] {len(cat_fixes)}件")
        for i, fix in enumerate(cat_fixes, 1):
            tag = "AUTO" if fix.confidence == "AUTO" else "要確認"
            print(f"  {i}. [{tag}] {fix.file.name!r}")
            if fix.new_name:
                print(f"       → {fix.new_name!r}")
            print(f"       理由: {fix.reason}")
            if fix.related_file:
                print(f"       関連: {fix.related_file.name!r} (ID: {fix.related_file.id})")
            print(f"       ID: {fix.file.id}")

    print(f"\n{'─'*60}")
    print(f"  AUTO修正: {auto_count}件  |  手動確認: {review_count}件")
    if dry_run and auto_count > 0:
        print("  --apply を付けて実行すると AUTO修正が適用されます")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# 修正の適用
# ---------------------------------------------------------------------------

def apply_fixes(service, fixes: list[Fix]) -> None:
    auto_fixes = [f for f in fixes if f.confidence == "AUTO"]
    if not auto_fixes:
        print("適用可能な AUTO修正がありません。")
        return

    print(f"\n{len(auto_fixes)}件の AUTO修正を適用します...\n")
    ok = 0
    ng = 0
    for fix in auto_fixes:
        try:
            if fix.action == FixAction.RENAME and fix.new_name:
                service.files().update(
                    fileId=fix.file.id,
                    body={"name": fix.new_name},
                ).execute()
                print(f"  OK  {fix.file.name!r} → {fix.new_name!r}")
                ok += 1
            elif fix.action == FixAction.TRASH:
                service.files().update(
                    fileId=fix.file.id,
                    body={"trashed": True},
                ).execute()
                print(f"  OK  ゴミ箱: {fix.file.name!r}")
                ok += 1
        except HttpError as e:
            print(f"  NG  {fix.file.name!r} : {e}")
            ng += 1

    print(f"\n完了: 成功 {ok}件 / 失敗 {ng}件")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Google Drive マイドライブのファイル名を整理します",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", default=False,
                      help="変更内容を表示するだけ（デフォルト動作）")
    mode.add_argument("--apply", action="store_true", default=False,
                      help="AUTO修正を実際に適用する")

    parser.add_argument("--fix-encoding", action="store_true",
                        help="URLエンコード修正のみ実行")
    parser.add_argument("--fix-duplicates", action="store_true",
                        help="重複検出のみ実行")
    parser.add_argument("--fix-names", action="store_true",
                        help="命名規則統一のみ実行")
    parser.add_argument("--fix-random", action="store_true",
                        help="ランダム名フラグのみ実行")

    parser.add_argument("--credentials", default="credentials.json",
                        help="OAuth認証ファイルのパス (デフォルト: credentials.json)")
    parser.add_argument("--token", default="token.json",
                        help="トークンキャッシュのパス (デフォルト: token.json)")
    parser.add_argument("--time-window", type=int, default=120,
                        help="ランダム名の近傍判定秒数 (デフォルト: 120)")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dry_run = not args.apply

    if not os.path.exists(args.credentials):
        print(f"エラー: {args.credentials} が見つかりません。")
        print("Google Cloud Console で OAuth クライアントIDを作成し、")
        print(f"{args.credentials} として保存してください。")
        sys.exit(1)

    print("Google Drive に接続中...")
    service = get_drive_service(args.credentials, args.token)

    print("マイドライブのファイルを取得中...")
    files = fetch_all_my_drive_files(service)
    print(f"{len(files)}件のファイルを取得しました。")

    run_all = not any([args.fix_encoding, args.fix_duplicates,
                       args.fix_names, args.fix_random])

    fixes: list[Fix] = []
    if run_all or args.fix_encoding:
        fixes.extend(analyze_url_encoding(files))
    if run_all or args.fix_random:
        fixes.extend(analyze_random_names(files, args.time_window))
    if run_all or args.fix_duplicates:
        fixes.extend(analyze_duplicates(files))
    if run_all or args.fix_names:
        fixes.extend(analyze_name_conventions(files))

    print_report(fixes, dry_run=dry_run)

    if not dry_run:
        confirm = input("AUTO修正を適用しますか？ [y/N]: ")
        if confirm.strip().lower() == "y":
            apply_fixes(service, fixes)
        else:
            print("キャンセルしました。")


if __name__ == "__main__":
    main()
