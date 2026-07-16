/**
 * Googleドライブ ファイル名一括リネームスクリプト
 * 命名ルール: 顧客名_書類名_日付(YYYYMMDD)
 *
 * ■ 使い方
 * 1. https://script.google.com を開き「新しいプロジェクト」を作成
 * 2. このファイルの内容を全部貼り付けて保存
 * 3. 上部の関数選択で「renameFiles」を選び「実行」
 *    (初回は権限の承認画面が出るので、自分のアカウントで許可)
 * 4. まずは DRY_RUN = true のまま実行し、ログ(実行ログ)で変更内容を確認
 * 5. 問題なければ DRY_RUN = false に変えて再実行 → 実際にリネームされます
 *
 * ■ 安全設計
 * - ファイルはIDで特定するため、同名ファイルの取り違えは起きません
 * - 現在の名前が想定(from)と一致しない場合はスキップして報告します
 * - リネームのみ。削除・移動・共有変更は一切しません
 * - 「【重複】」「【旧版】」プレフィックスの付いたものは、内容確認のうえ
 *   不要ならご自身でドライブから削除してください
 */

// true = 変更せずログ表示のみ / false = 実際にリネーム実行
const DRY_RUN = true;

const RENAMES = [
  // ===== 竹本様 =====
  { id: '1q0PgdCcZoFF6kOD4WwjOap7PSfzVFcjK', from: '竹本 史生 様 2026_7_16 ウッドフェンス・デッキ塗装 御見積書.pdf', to: '竹本史生様_ウッドフェンス・デッキ塗装御見積書_20260716.pdf' },

  // ===== 山本様 =====
  { id: '1P6kqUdS-ldivngwnaN3yeK5JYuIT00JVK3PEkma5RLQ', from: '山本様-社内振込依頼書', to: '山本様_社内振込依頼書_20260601' },
  { id: '1n8EdBYjBAfNIOpR6ttjSSD8LXm2FXmby', from: '山本様-請負契約書.pdf', to: '山本様_請負契約書_20260716.pdf' },
  { id: '1iiq2UDEsC6qmbbBPxhjJXDYfzPz_iSHT', from: '251120山本邸(本契約用訂正済).pdf', to: '山本様_本契約用訂正済_20251120.pdf' },
  // ↓同名ファイル(7/12にもアップロードされたもの)。内容がほぼ同じ可能性が高いため重複マーク
  { id: '1Jhdh8ehwiwccGamyYu6EkW96QNz2jbnQ', from: '251120山本邸(本契約用訂正済).pdf', to: '【重複】山本様_本契約用訂正済_20251120.pdf' },

  // ===== 阿部様 =====
  { id: '1TfIccmckKijqQIHdJytFdxJWTjyor53HC0HUbtIQ-18', from: '阿部様_工事費用_利益率・粗利比較表', to: '阿部様_利益率・粗利比較表_20260716' },
  { id: '14-3SSAMHNZ2gnx-87YfSH6jOwX9mCqwJHvKp4b3WP1M', from: '阿部様邸_工事費用利益率シミュレーション', to: '阿部様_工事費用利益率シミュレーション_20260716' },
  { id: '1A6KxqdcbSOKfVj9WP5OqW_yt3JR_S9oJZJXqVpEh2XI', from: '阿部様', to: '阿部様_提案資料_20260712' },
  { id: '1KRYDy_tWcH3uM6Wwtm2sG_cP_F52Ep2k6N29XLFP4jw', from: 'コピー～ 阿部様', to: '【重複】阿部様_提案資料コピー_20260712' },
  { id: '1ASeHySUXzf8CpoxCyPcJL4cuIV57twPN', from: '%E9%98%BF%E9%83%A8%E6%A7%98.pdf.pdf', to: '阿部様_提案資料_20260712.pdf' },
  { id: '1a2kEZa3kLE_YJV5EpOIhTeXShy9Vo8hF', from: '%E3%82%B3%E3%83%92%E3%82%9A%E3%83%BC%EF%BD%9E%20%E9%98%BF%E9%83%A8%E6%A7%98.pdf.pdf', to: '【重複】阿部様_提案資料コピー_20260712.pdf' },
  { id: '1-OK8joilT6WBCkYNqRMvXTBmnBll0AhcueLivri8G1M', from: '阿部様', to: '阿部様_プレゼン資料_20260712' },
  { id: '1wYxva9fHg7C9ftxdeXqcYuk_kvelc3Lez3r-fAIjDcY', from: '阿部 豊様', to: '阿部豊様_見積シート_20260622' },

  // ===== 萩殿町三丁目37(売買) =====
  { id: '1WK40MZNeAvks76NALxkdvxzdFAdznmVx', from: '売買契約書　萩殿町三丁目３７.docx', to: '萩殿町三丁目37_売買契約書_20260716.docx' },
  { id: '1U3yu-Jw_rH3MV1SbvIpGyrblofhXY_8G', from: '売買契約書　萩殿町三丁目３７.docx', to: '【重複】萩殿町三丁目37_売買契約書_20260716.docx' },
  { id: '1wB-cMtubvHypmcDz_W6AgDnlBe6rWAvk', from: '重説　萩殿町三丁目３７.docx', to: '萩殿町三丁目37_重要事項説明書_20260716.docx' },
  { id: '1TpQqCGKRmmfRseWq-IAX9Iq6c1oB9ilP', from: '重説　萩殿町三丁目３７.docx', to: '【重複】萩殿町三丁目37_重要事項説明書_20260716.docx' },

  // ===== 仕様変更 参考資料シリーズ(V1〜V5) =====
  { id: '1iVtC1Hojrk1HImYPiaL7WAIKEvS44LDaHjA0xYTc_WA', from: '仕様変更に伴う金額変化（コスト増減）参考資料', to: '仕様変更に伴う金額変化（コスト増減）_参考資料V1_20260716' },
  { id: '1ZpSyeO231eFNSQdaFsJj7pSlDsa8T5XhRVFBUkjGnO8', from: '仕様変更に伴う金額変化（コスト増減）参考資料 V2', to: '仕様変更に伴う金額変化（コスト増減）_参考資料V2_20260716' },
  { id: '1KS8pW063Vtb3Ybjo1Jkb0XEFaQpUCwl5DPu4FsS2aF8', from: '仕様変更に伴う金額変化（コストダウン・減額差額）参考資料 V3', to: '仕様変更に伴う金額変化（コストダウン・減額差額）_参考資料V3_20260716' },
  { id: '1YmxkSzWLrWrBQgTgDtRyVi0MHBmK9WPmyyKk3LrxW-k', from: '仕様変更に伴う金額変化（中央値）参考資料 V5', to: '仕様変更に伴う金額変化（中央値）_参考資料V5_20260716' },

  // ===== 冨田様 =====
  { id: '1cSqS_1HOeFkqvjnIcGbZ7Qzrle-gq8fMKS_j-p01YXY', from: '冨田様', to: '冨田様_見積シート_20260706' },
  { id: '18o5Khisg-GbLEizuiA1bUm47Pu03NYm3YgCiLIhPG-M', from: '冨田様-見積比較項目', to: '冨田様_見積比較項目_20260704' },
  { id: '15kCDGEaBVtKmv2pCROEreNzKpdnpJir5', from: '冨田様 - 地鎮祭のご案内.pdf', to: '冨田様_地鎮祭のご案内_20260706.pdf' },
  { id: '1EGOGiEmrzvP56-epAh6tj5BS5u8_2e9O', from: '〇冨田寛樹様邸お見積書0704（修正後）.pdf', to: '冨田寛樹様_お見積書（修正後）_20260704.pdf' },
  { id: '1TKb4AHytWjuFXUM0VpAsIK28DPTQ-XFh', from: '冨田寛樹様邸見積り0424.pdf', to: '冨田寛樹様_見積書_20260424.pdf' },
  { id: '1x0mDI5uuPCZhC4rz2LewCB0tIanA7G3H', from: '260614冨田邸概算見積契約用図面.pdf', to: '冨田寛樹様_概算見積契約用図面_20260614.pdf' },

  // ===== 西岡様 =====
  { id: '12w3AbzPZN3CmJI5p08lIqNsEQ92Q9O0QfwrJhOr8mYE', from: '西岡 研二様-照が丘26.49', to: '西岡研二様_照が丘26.49_20260705' },
  { id: '1pTQiT9ozFPLAwgOJzrNyeM90C0sFUCDwwukqpj1UBWQ', from: '西岡 研二様-照が丘', to: '西岡研二様_照が丘_20260705' },
  { id: '1P-UF-B37N2Rm_C_v-B7Nl1Qx0p4tNMFK1Or5_lZLOY8', from: 'コピー～ 西岡 研二様-照が丘', to: '【重複】西岡研二様_照が丘コピー_20260712' },
  { id: '1gGf8wUiU6bAc8yGeFIUYfHUgPeDh4-aoyJSm6z0jGSc', from: '西岡 研二様-上川原', to: '西岡研二様_上川原_20260623' },
  { id: '1pbY-N-bAisbQOAYKWnGzRlzeeyhBskWLvt1ikqVw1jE', from: '西岡 研二様-下山', to: '西岡研二様_下山_20260705' },
  { id: '19W6_jSVOO7mMJZ9FMiTAohSctlX67zGCQazx5t2eos0', from: '西岡 研二様-下山', to: '【重複】西岡研二様_下山_20260705' },

  // ===== 領家様(「猟家」は誤記と判断し統一) =====
  { id: '1yl5enlNWLu0ZqWxWKHEjilM2uQA-q-6JHo7nun42i2Y', from: '領家様', to: '領家様_見積シート_20260703' },
  { id: '119skFF2-Yr-GQ6fzIrWXva047-1CEKFE', from: '図面_領家様邸_M26061330139-002.PDF', to: '領家様_図面_M26061330139-002_20260706.PDF' },
  { id: '1U2XgmRPtULm5FqiMpHWiJYhUy2dnweKO', from: '【定価】見積_領家様邸_M26061330139-002_2.PDF', to: '領家様_見積【定価】M26061330139-002_20260706.PDF' },
  { id: '1WSvYzEBmIXybGgy3GaIYbfI_YmoTF1k3', from: '【NET】見積_領家様邸_M26061330139-002_1.PDF', to: '領家様_見積【NET】M26061330139-002_20260706.PDF' },
  { id: '1mYmQ2z5VkipJsOxR6eXV6r4M1h4qA6L-', from: 'ＰＢ_領家様邸_サティスXタイプ_M26061330139_002_001-000_000001.PDF', to: '領家様_PB_サティスXタイプ_M26061330139-002_20260706.PDF' },
  { id: '1XXhg1iSH9RjwZg9wwCsDb5F9_MCFTDS7', from: '図面_猟家様邸_M26061330139-001.PDF', to: '領家様_図面_M26061330139-001_20260701.PDF' },
  { id: '1n-TW17GeXurAbHHF-RyFn07qdWKFFE1s', from: 'ＰＢ_猟家様邸_サティスXタイプ_M26061330139_001_001-000_000001.PDF', to: '領家様_PB_サティスXタイプ_M26061330139-001_20260701.PDF' },
  { id: '1sDPeRlKMLxU2qrc8SiiV66DDciiQgd-w', from: '【定価】見積_猟家様邸_M26061330139-001_2.PDF', to: '領家様_見積【定価】M26061330139-001_20260701.PDF' },
  { id: '1eR69oJEJfXawIt7utOrZR246svSUZJHH', from: '【NET】見積_猟家様邸_M26061330139-001_1.PDF', to: '領家様_見積【NET】M26061330139-001_20260701.PDF' },

  // ===== 伊藤様 =====
  { id: '1erqHGgfkvxKofV6Omjn-4u7giGjNbqOW0fKyJ85Gvj8', from: '伊藤様', to: '伊藤様_見積シート_20260703' },
  { id: '1GCteGP-jpbdKQP4pu9z5W_wFJ4O4g3zd', from: '伊藤様 - Google スプレッドシート.pdf', to: '伊藤様_見積シート（PDF出力）_20260626.pdf' },
  { id: '1plOtI-SYZUdV0Jp8kw-jhKeRnr5ogIWf', from: 'DM　伊藤様　2026年8月.jpeg', to: '伊藤様_DM_202608.jpeg' },

  // ===== その他の顧客 =====
  { id: '1qMZFQVYT_pP9i7Sipb5rrSSRyfFsDWsa', from: '【NET】加藤様メンテナンス.pdf', to: '加藤様_メンテナンス【NET】_20260713.pdf' },
  { id: '1dH7O4Aum9jBa0rSvZDp0aMYJIT7W7rcZ', from: '前﨑様-変更契約.pdf', to: '前﨑様_変更契約書_20260620.pdf' },
  { id: '1mKfsY0IVFYoA5-8cm6uq2u68CBXs8EYaGNQDnHslvDE', from: '山崎様邸売却プロジェクト 市場分析と改善提案', to: '山崎様_売却市場分析と改善提案_20260706' },

  // ===== 物件・分譲 =====
  { id: '1Q_rcZNuOR4tmSWfu83yd-H3ydh9tMfq9', from: '旭前駅物件-イノベーション案.pdf', to: '旭前駅物件_リノベーション案_20260714.pdf' },
  { id: '1R0fXJm4EhNL-efJXnw85pm44RcMe55KL', from: '宮脇分譲.pdf', to: '宮脇分譲_資料_20260706.pdf' },
  { id: '1-oIW8ZPfDKXowPrAizuG0DFzi7j1kyoZ', from: '物件概要書／長久手市下山220番、221番、222番（ｒ7.2.4）.pdf', to: '長久手市下山220-222番_物件概要書_20250204.pdf' },
  { id: '13xA0S_GwPKbhTWbA_-MgIExp6yBRplkG', from: '折込チラシB4(1物件)／長久手（2区画）ｒ8.2.7 (1).pdf', to: '長久手2区画_折込チラシB4_20260207.pdf' },
  { id: '1DxD6i-664vhgWvaxtsarnaMSkRwRpv5T', from: '換地図.pdf', to: '換地図①_20260703.pdf' },
  { id: '1huD1tlVuqKNP1iWXWe1-rncJeGnXZNl6', from: '換地図.pdf', to: '換地図②_20260704.pdf' },
  { id: '1fHw4_3a-wNha3nK0BT29_2DiTSK9vIiI', from: '換地図.pdf', to: '換地図③_20260705.pdf' },
  { id: '1E9XNZK6nZUwbeqBH7643_xHW03yIbbya', from: '換地図.pdf', to: '換地図④_20260705.pdf' },
  { id: '1l-KSITlVAR0KOgSox0DPufgIgJPTITQu', from: '換地図.pdf', to: '換地図⑤_20260705.pdf' },

  // ===== 議事録(Geminiメモ) =====
  { id: '1qyPQdHCCVrRxKaIlZkHdArolq_6wa8VYNUD1KaeAPHc', from: 'AI委員会 - 2026/07/13 16:04 JST - Gemini によるメモ', to: 'AI委員会_議事録_20260713' },
  { id: '176SmkcG0Vbey99P93wtT1jNQA42mIvYjWBruBfDCW1c', from: 'NEXT打合せ - 2026/07/09 17:38 JST - Gemini によるメモ', to: 'NEXT打合せ_議事録_20260709' },
  { id: '1Pop88uGv0xpF6B1HX_n_bvomP_SoLso5JFwpNBHsXZY', from: 'NEXT打合せ - 2026/07/03 16:56 JST - Gemini によるメモ', to: 'NEXT打合せ_議事録_20260703' },
  { id: '15H_l_amvOs30B05bz2hH_55xxt8H_-oSPJn3uxbEB14', from: 'NEXT打合せ - 2026/06/25 16:56 JST - Gemini によるメモ', to: 'NEXT打合せ_議事録_20260625' },
  { id: '1spwAQVe-yAyhieq0cwj8B74FiqEeWzEbc7crJCYs_m8', from: '集客・成約MT - 2026/07/03 12:56 JST - Gemini によるメモ', to: '集客・成約MT_議事録_20260703' },
  { id: '1ujZjIFIHXu50El5W6uY9m2n_s0z1-ZeJ1na0LDOl9PU', from: ' 2026/07/03 14:26 JST に開始した会議 - Gemini によるメモ', to: '会議_議事録_20260703' },

  // ===== 社内資料 =====
  { id: '1IxOZlx4lHm12L3KVe_gb_rFje9QpBpNz', from: 'ビジョン経営計画　KINOKA new.pdf', to: 'KINOKA_ビジョン経営計画_20260709.pdf' },
  { id: '1JEMqL73hZsW3WRVl_A9mRTuRtDUp6ve9OjOpVpKNYEk', from: 'AI委員会 活動報告（2026年6月）', to: 'AI委員会_活動報告_202606' },
  { id: '1DML8Tv7muWCUj90HcStYmBiCfuik7PRAXganXFzWVzk', from: '請求書振分け明細票', to: '請求書振分け明細票_20260713' },
  { id: '1ka7_3fa7AQDe2qg9QYg07kxokPW-eDCBehJvl4DMXs8', from: '金券-管理台帳', to: '金券管理台帳_20260421' },
  { id: '1aFFCupuibgLDQp9CQgKtMys8oCA3fa6DOl0fn_1_4J0', from: '見積後追加増減工事', to: '見積後追加増減工事_20260503' },
  { id: '1ggQtz3RRZmNNe-iCRpVtD59gUG3ni6ps7obQ-cBuQRE', from: '上棟時時確認事項', to: '上棟時確認事項_20260626' },
  { id: '17fz3mIJwN5jU-uox06JtNfBRL6C5vJL-ojxNaQrHGXI', from: '目標管理2026（1-3） ', to: '目標管理2026（1-3月）_20260126' },
  { id: '1bfKIy8QALWw1lVP2xKkHrWEIBA2Ca4wNXcHftH0PM6A', from: '勝利敗戦レポート', to: '勝利敗戦レポート_20260207' },
  { id: '1nzkERTK0W7ntqSLj9Wert0rVtvU8whjzsw1dWrOzS1Q', from: '☆着工前の大切なご確認事項ver.2', to: '着工前の大切なご確認事項_ver2_20260701' },
  { id: '1n-qhRXMWFoy77TPvbJiLKFh1hsMFxJspIFtDJgMrgv4', from: 'コピー～ ☆着工前の大切なご確認事項ver.2', to: '【重複】着工前の大切なご確認事項_ver2コピー_20260701' },
  { id: '15gHFYAsDvW_9GDef9pxrQ4HvGdQnRgW2BfD3G-Ev-tg', from: '☆着工前の大切なご確認事項（整理版・部位別）', to: '着工前の大切なご確認事項（整理版・部位別）_20260701' },
  { id: '1EhK_eFTFweAprxV4zpgFd3sHp0WLon2X', from: '%E2%98%86%E7%9D%80%E5%B7%A5%E5%89%8D%E3%81%AE%E5%A4%A7%E5%88%87%E3%81%AA%E3%81%9.pdf', to: '着工前の大切なご確認事項_20260701.pdf' },
  { id: '19lCVGq6Xv1keGTu9oVGVs-xmJHFFyu6x', from: '上棟式 式次第.xlsx', to: '上棟式_式次第_20260503.xlsx' },
  { id: '1q2PNwtlhAUEqXaCUe6amnBeHGWukexv-', from: '上棟式 式次第.xlsx', to: '【旧版】上棟式_式次第_20260503.xlsx' },

  // ===== メーカー見積など =====
  { id: '1js2EkmodYv3FySGiHZxNePhkbNjzLikM', from: '人大浴槽　1501A-2606-1078T.pdf', to: '人大浴槽_1501A-2606-1078T_20260629.pdf' },
  { id: '1aYvag1I05dnLLOLJIPJ81KwKanaRf6M4', from: 'FRP浴槽　1501A-2606-1077T.pdf', to: 'FRP浴槽_1501A-2606-1077T_20260629.pdf' },
];

/**
 * 内容が名前から判断できなかったファイル。
 * 中身を確認して to を決めたら、上の RENAMES に移してください。
 * (このままでは実行されません)
 */
const NEEDS_REVIEW = [
  { id: '1MMwVB72sauwmMiXVpk-w9JPakkT2Z5dj', from: 'Print.pdf', note: '22MB。山本様の本契約書類の印刷出力の可能性' },
  { id: '11buB7GnLQONt29Z74GjcM5-v2W0WnWLO', from: 'Print.pdf', note: '7/4作成 1.9MB。換地図と同時期' },
  { id: '1tYwCynMP5L43BSfuVrOIC1oWX1q39cKX', from: 'hennge_secure_download.pdf', note: '7/14受領のセキュア便' },
  { id: '1dt_UdqGvqwE00eV1zimYJrzB2CY6kKhp', from: 'hennge_secure_download.pdf', note: '7/3受領のセキュア便' },
  { id: '1aSClgjCNFcmYMg0XqPBcVN2WPOiUXaoT', from: 'downloadZmnPdfFile.pdf', note: '7/4取得。ゼンリン地図?' },
  { id: '1QRhoELR1m_A1PEKPhF-9nyG3RKNwHtXW', from: 'map - 2024-02-19T194109.316.pdf', note: '地図。どの物件か要確認' },
  { id: '1ucf2fohqT__WAAwKoLGWB4-ggbTx0pHS', from: '20240821163109.pdf', note: 'スキャン文書と思われる' },
  { id: '1m9TrHZMk9-c5HE22iXJpWLWz45B8rhqa', from: 'doc01478520260703131039.pdf', note: '複合機スキャン。7/3' },
  { id: '1qnC4Nnih__DkMWThOT4A4TLyuvhN6kwD', from: '940bb3d5-6269-406d-96af-89f76c7c41d8.pdf', note: '7/2取得。内容不明' },
  { id: '1GwYnLhlP1PMkVuDIIZ4_6B88spCU5e25', from: 'イメージ.pdf', note: '7/6作成。内容不明' },
  { id: '1R0l-oJURSSh9FAA4u92wGggmGBdWS6jVXPOFOZw_0c4', from: '無題のドキュメント', note: '7/6作成のGoogleドキュメント' },
  { id: '1n8-UC7JINJVgYCaGUfm6MH75yEsXg2DhmjUkorTKk3U', from: '2026年1/4半期', note: '「2026年第1四半期_○○_20260413」等に' },
  { id: '1hAQLnarIomSb_EPjm_JSWx91FMmYr-MQ', from: 'Image_20260709_162453_080.jpeg', note: '写真。被写体を確認して命名' },
  { id: '1J53dOmchJuKYeoL4bgTJ5Uve_mj_slaE', from: 'Image_20260709_170531_935.jpeg', note: '写真' },
  { id: '1MEmbO_Tc4eClcZ66VfRvsloLvqbOHx4B', from: 'Image_20260709_170531_740.jpeg', note: '写真' },
  { id: '1ARsDh_IobepWjlhRKatJyiREwR730uMB', from: 'IMG_3067.JPG', note: '写真' },
  { id: '1v6HtMbgNAZ5Cixn6RpQjTl4xp7n-JWIyG-tT41y7RO8', from: 'タスク管理_v3', note: '運用中の管理表。現状維持でも可' },
];

function renameFiles() {
  let renamed = 0, skipped = 0, failed = 0;
  Logger.log(DRY_RUN ? '=== ドライラン(確認のみ・変更なし) ===' : '=== 本実行(実際にリネームします) ===');

  RENAMES.forEach(function (item) {
    try {
      const file = DriveApp.getFileById(item.id);
      const current = file.getName();
      if (current !== item.from) {
        Logger.log('⏭ スキップ(名前が想定と不一致): 現在「' + current + '」/ 想定「' + item.from + '」');
        skipped++;
        return;
      }
      if (!DRY_RUN) {
        file.setName(item.to);
      }
      Logger.log('✅ 「' + item.from + '」 → 「' + item.to + '」');
      renamed++;
    } catch (e) {
      Logger.log('❌ 失敗 (id: ' + item.id + '): ' + e.message);
      failed++;
    }
  });

  Logger.log('--- 結果: ' + (DRY_RUN ? '対象 ' : '変更 ') + renamed + '件 / スキップ ' + skipped + '件 / 失敗 ' + failed + '件 ---');
  if (DRY_RUN) {
    Logger.log('内容が良ければ、先頭の DRY_RUN を false にして再実行してください。');
  }
  if (NEEDS_REVIEW.length > 0) {
    Logger.log('※ 内容確認が必要なファイルが ' + NEEDS_REVIEW.length + ' 件あります(NEEDS_REVIEW参照)。');
  }
}
