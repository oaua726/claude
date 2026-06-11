# Neon Sticker Studio 🌟

ブラウザだけで動く、レトロフューチャー系ステッカー・アイコンメーカー。
ビルド不要・サーバー不要の静的Webアプリです（HTML / CSS / JavaScript のみ）。

`index.html` をブラウザで開くだけで動きます。

## 機能

- 6種類のテンプレート（惑星 / ロケット / 宇宙ネコ / 三日月 / バースト / アーケード）
- ベース・アクセント・グローの3色カスタマイズ
- 上下テキストの入れ替え（SNSアイコン・配信サムネ・LINEスタンプ素材に）
- 「おまかせ生成」ボタンでランダムデザイン
- PNG書き出し（透過背景）
- フリーミアム設計：無料＝512px透かし入り / PRO＝1024px透かしなし

## 公開方法（無料・5分）

GitHub Pages にデプロイするだけで公開できます：

1. リポジトリの **Settings → Pages** を開く
2. Source を「Deploy from a branch」、対象ブランチと `/app` フォルダ（またはルート）を選択
3. 数分で `https://<ユーザー名>.github.io/<リポジトリ名>/app/` で公開されます

Netlify / Cloudflare Pages へのドラッグ＆ドロップでもOKです。

## 収益化の設定

### 1. 決済リンクを用意する

以下のいずれかで「買い切り ¥980」の商品を作成します：

| サービス | 特徴 |
|---|---|
| **Stripe Payment Links** | 手数料3.6%。コード不要で決済URLを発行できる |
| **Gumroad** | ライセンスキー自動発行機能あり（PRO認証と相性◎） |
| **BOOTH** | 日本のクリエイター向け。pixivユーザーにリーチしやすい |

### 2. 決済URLをアプリに設定する

`index.html` の購入ボタンに決済URLを設定します：

```html
<a class="btn btn-primary btn-large" id="buyBtn"
   href="https://buy.stripe.com/xxxx" data-payment-link="https://buy.stripe.com/xxxx">
```

### 3. ライセンス認証を本物にする

現在 `app.js` の `activateLicense()` はキーの形式チェックのみの**プレースホルダ**です。
Gumroad を使う場合は [License API](https://gumroad.com/help/article/76-license-keys) を呼び出して
検証する実装に置き換えてください（serverless function 1本で実装可能）。

### 4. その他の収益チャネル

- **作ったステッカー自体を売る**：このツールで量産したデザインを LINE Creators Market / Redbubble / SUZURI でグッズ化
- **カスタムオーダー**：ココナラ等で「あなた専用ネオンアイコン作ります」を出品し、このツールで高速納品
- **テンプレート追加パック**：季節もの（ハロウィン・年賀）テンプレートを追加課金で販売

## 既存の Python 版との関係

リポジトリ直下の `generate_stickers.py` は同じデザインシステムのバッチ生成版です。
大量生成（ストアへの一括出品用）はPython版、対話的なカスタマイズ・販売はこのWebアプリ、と使い分けられます。

## ライセンス

作成したステッカーの著作権は作成者（ツール利用者）に帰属します。
