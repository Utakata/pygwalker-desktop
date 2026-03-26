# PyGWalker Desktop

![PyGWalker Desktop Banner](https://img.shields.io/badge/PyGWalker-Desktop-blue) ![License](https://img.shields.io/badge/license-Apache%202.0-green) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Qt](https://img.shields.io/badge/Qt-6.8%2B-green)

**PyGWalker と PySide6 (Qt 6) で構築した、オープンソースの Tableau 風データ可視化デスクトップアプリケーション。**

CSV、Excel、Parquet ファイルを読み込み、ドラッグ&ドロップで直感的にグラフを作成・分析できます。

## 特徴

### 🎨 ノーコード可視化
- **Graphic Walker** - ドラッグ&ドロップで簡単にグラフ作成
- Tableau のような直感的なインターフェース
- 複数の選択肢から最適なグラフを自動提案

### 📊 高性能なデータ処理
- **kernel_computation モード** - DuckDB による超高速集計
- 大規模データセット（GB 単位）にも対応
- クライアント側とサーバー側の計算を自動切り替え

### 🌍 ローカルファースト
- データはコンピュータ内で処理（クラウド不要）
- オフライン完全対応
- プライバシーを最優先

### 🎯 直感的な UI
- ライト / ダーク / システム自動 のテーマ切替
- ズーム機能
- 最近開いたファイル履歴
- 完全日本語化

### 💾 複数フォーマット対応
- **CSV / TSV** - カンマ区切り・タブ区切りテキスト
- **Excel** - .xlsx / .xls ファイル
- **Parquet** - 高効率カラムナーフォーマット

## インストール

### 必要な環境

- **Python 3.10 以上**
- **Windows / macOS / Linux**

### 📋 OS 別ガイド

- **🪟 [Windows 環境ガイド](WINDOWS_GUIDE.md)** - Windows 10/11 での詳細手順
- **🍎 macOS** - Coming soon
- **🐧 Linux** - Coming soon

### インストール手順

```bash
# リポジトリをクローン
git clone https://github.com/Utakata/pygwalker-desktop.git
cd pygwalker-desktop

# 開発モードでインストール
pip install -e .
```

### 依存パッケージ

```
pygwalker>=0.5.0.0      # グラフィック・ウォーカー エンジン
PySide6>=6.8.0          # Qt 6 Python バインディング
pandas>=2.0.0           # DataFrameライブラリ
openpyxl>=3.1.0         # Excel 読み込み
pyarrow>=14.0.0         # Parquet 読み込み
```

すべての依存パッケージは `pip install -e .` で自動的にインストールされます。

## 使い方

### 起動方法

```bash
# コマンドラインから
python -m pygwalker_desktop

# または
pygwalker-desktop
```

### 基本的な操作フロー

1. **ファイルを開く** - `ファイル > 開く` から CSV / Excel / Parquet ファイルを選択
2. **フィールドを配置** - 左パネルからフィールドをドラッグして行・列・色などに配置
3. **グラフを作成** - 自動的にグラフが更新されます
4. **さらに詳細に** - フィルタ、並べ替え、集計関数を追加
5. **エクスポート** - グラフを PNG / SVG で保存

### メニュー機能

#### ファイル (F)
- **開く (Ctrl+O)** - CSV / Excel / Parquet ファイルを開く
- **最近開いたファイル** - 過去 10 個のファイルからワンクリックで開く
- **設定をエクスポート** - グラフ設定を JSON で保存（今後のアップデートで対応）
- **設定をインポート** - 以前保存した設定を読み込む（今後のアップデートで対応）
- **終了 (Ctrl+Q)** - アプリケーションを閉じる

#### 表示 (V)
- **ライト / ダーク / システム** - テーマ切替
- **拡大 (Ctrl++)** - ズインイン
- **縮小 (Ctrl+-)** - ズームアウト
- **ズームリセット (Ctrl+0)** - 100% に戻す

#### ヘルプ (H)
- **このアプリについて** - バージョン情報とクレジット

### ツールバー

- **ファイルを開く** - ファイルダイアログを表示
- **ライト / ダーク / 自動** - テーマの素早い切替

### ステータスバー

ファイル名、行数 × 列数、データ処理モード（kernel_computation の有無）を表示

## アーキテクチャ

### システム設計

```
┌─────────────────────────────────────────┐
│  MainWindow (PySide6)                   │
│  ┌─────────────────────────────────┐    │
│  │  メニューバー / ツールバー       │    │
│  ├─────────────────────────────────┤    │
│  │                                 │    │
│  │     QWebEngineView              │    │
│  │   (Graphic Walker UI)           │    │
│  │   ← http://127.0.0.1:{port} →  │    │
│  │                                 │    │
│  ├─────────────────────────────────┤    │
│  │  ステータスバー                  │    │
│  └─────────────────────────────────┘    │
└──────────────┬──────────────────────────┘
               │ HTTP GET/POST
               ▼
┌─────────────────────────────────────────┐
│  ServerBridge (QThread)                 │
│  - PygWalker インスタンス               │
│  - HTTPServer (127.0.0.1:{free_port})   │
│  - GET /     → PyGWalker HTML          │
│  - POST /comm → DuckDB クエリ → JSON   │
└─────────────────────────────────────────┘
```

### なぜこのアーキテクチャ？

#### 1. ローカル HTTP サーバー方式を採用

**問題点：setHtml() による直接埋め込み**
- Chromium は HTML に 2MB の制限がある
- PyGWalker の生成 HTML は 2.8MB に達する
- ✗ 実装不可能

**解決策：ローカル HTTP サーバー**
- サーバーから HTML をストリーミング配信
- 大容量データにも対応
- ✓ kernel_computation (DuckDB) も完全サポート

#### 2. QThread で非同期処理

**メイン UI スレッド**
- Qt イベントループ実行
- QWebEngineView レンダリング
- ユーザーインタラクション

**サーバー スレッド (ServerBridge)**
- HTTP リクエスト処理
- PyGWalker インスタンス管理
- DuckDB クエリ実行
- **UI ブロッキングなし**

#### 3. PyGWalker の内部 API を活用

PyGWalker webserver.py パターンを正しく再現：
```python
walker._get_props("web_server")      # 設定プロパティ取得
walker._get_render_iframe(props)     # HTML 生成
walker._init_callback(comm)          # /comm エンドポイント登録
walker.comm._receive_msg(...)        # DuckDB クエリ処理
```

## ファイル構成

```
pygwalker-desktop/
├── README.md                          # このファイル
├── pyproject.toml                     # プロジェクト設定 (依存パッケージ他)
├── .gitignore                         # Git 除外ファイル
├── sample_data.csv                    # テスト用サンプルデータ
│
├── src/pygwalker_desktop/
│   ├── __init__.py                    # パッケージ初期化
│   ├── __main__.py                    # python -m pygwalker_desktop エントリポイント
│   │
│   ├── app.py                         # QApplication ブートストラップ
│   │   └── main() エントリポイント
│   │
│   ├── main_window.py                 # QMainWindow メイン画面
│   │   ├── メニューバー (ファイル / 表示 / ヘルプ)
│   │   ├── ツールバー
│   │   ├── ステータスバー
│   │   ├── ファイルダイアログ
│   │   ├── 最近開いたファイル管理
│   │   └── テーマ切替
│   │
│   ├── web_view.py                    # QWebEngineView ラッパー
│   │   └── JS / LocalStorage 設定
│   │
│   ├── server/
│   │   ├── __init__.py
│   │   ├── handler.py                 # HTTP リクエストハンドラ
│   │   │   ├── do_GET() → PyGWalker HTML 提供
│   │   │   ├── do_POST(/comm) → DuckDB クエリ処理
│   │   │   └── do_GET(/health) → ヘルスチェック
│   │   │
│   │   └── bridge.py                  # ServerBridge (QThread)
│   │       ├── PygWalker インスタンス生成
│   │       ├── HTTPServer 起動・停止
│   │       └── スレッドセーフなシャットダウン
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── loader.py                  # ファイル読み込み
│   │       ├── CSV / TSV 対応
│   │       ├── Excel 対応
│   │       └── Parquet 対応
│   │
│   └── widgets/
│       ├── __init__.py
│       └── settings_dialog.py         # 設定ダイアログ
│           ├── 外観 (ライト / ダーク / システム)
│           ├── チャートテーマ (g2 / vega)
│           └── デフォルトタブ (可視化 / データ)
│
└── tests/
    └── __init__.py                    # テスト (今後拡充予定)
```

## 技術仕様

### 使用技術

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.10+ | 実装言語 |
| PyGWalker | 0.5.0+ | グラフ・ウォーカー エンジン |
| PySide6 | 6.8.0+ | Qt 6 バインディング |
| pandas | 2.0.0+ | DataFrame 処理 |
| DuckDB | 1.5.1+ | サーバーサイド集計 |
| Chromium (埋め込み) | 最新 | レンダリング エンジン |

### パフォーマンス

| 項目 | 推奨値 |
|------|--------|
| 最大行数 (kernel_computation OFF) | 100,000 |
| 最大行数 (kernel_computation ON) | 100,000,000 (100M) |
| 最大列数 | 1,000 |
| HTML バンドルサイズ | 2.8 MB |

**注:** kernel_computation は 1GB 以上のデータセットで自動的に有効になります。

### スレッドモデル

| スレッド | 役割 | 通信 |
|---------|------|------|
| **メイン (Qt イベントループ)** | UI レンダリング、ユーザー入力 | Qt Signals/Slots |
| **サーバー (QThread)** | HTTP サーバー、PyGWalker、DuckDB | Signal/Slot, HTTP |
| **ファイル読み込み (QThread)** | 大容量ファイル読み込み | Signal/Slot |

## 設定

### QSettings によるローカル保存

以下の設定は自動的に保存・復元されます：

| 設定項目 | デフォルト | 用途 |
|---------|-----------|------|
| `appearance` | media | テーマ (media/light/dark) |
| `theme_key` | g2 | チャートテーマ (g2/vega) |
| `default_tab` | vis | デフォルトタブ (vis/data) |
| `last_open_dir` | (ホームディレクトリ) | 前回開いたディレクトリ |
| `recent_files` | (空) | 最近開いたファイル (最大 10 件) |
| `window_geometry` | (デフォルト) | ウィンドウサイズ・位置 |

### 設定ダイアログ

`ファイル > 設定` (今後のメニューに追加予定) で以下を変更可能：

- **外観** - ライト / ダーク / システム自動
- **チャートテーマ** - g2 / vega
- **デフォルトタブ** - 可視化 / データ

## 今後の拡張予定

### Phase 2: ファイル管理
- [x] CSV / TSV 対応
- [x] Excel 対応
- [x] Parquet 対応
- [ ] 大容量ファイル読み込み時のプログレスダイアログ

### Phase 3: UX 改善
- [x] ライト / ダーク / システムテーマ
- [x] ズーム機能
- [x] ステータスバー情報
- [x] 設定ダイアログ
- [ ] キーボードショートカット追加

### Phase 4: 設定管理
- [ ] グラフ設定の JSON エクスポート
- [ ] グラフ設定の JSON インポート
- [ ] データセットごとの設定自動保存

### Phase 5: 高度な機能
- [ ] SQLクエリエディタ (kernel_computation 用)
- [ ] 複数データセットの結合
- [ ] カスタム計算フィールド
- [ ] 地図ビジュアライゼーション

### Phase 6: パッケージング
- [ ] PyInstaller でスタンドアロン EXE 化
- [ ] macOS アプリバンドル (.app)
- [ ] Linux AppImage 作成

## 参考資料

| 資料 | 内容 |
|------|------|
| [WINDOWS_GUIDE.md](WINDOWS_GUIDE.md) | **Windows 10/11 での詳細なインストール・利用ガイド** |
| [QUICKSTART.md](QUICKSTART.md) | 5 分で始められるクイックスタート |
| [ARCHITECTURE.md](ARCHITECTURE.md) | システム設計・技術仕様書 |

## 開発

### ローカル開発環境セットアップ

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境有効化
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 開発モードでインストール
pip install -e .

# アプリ起動
python -m pygwalker_desktop
```

### コード スタイル

- **フォーマッター**: 未設定 (今後: black / autopep8)
- **Linter**: 未設定 (今後: flake8 / pylint)
- **型チェック**: 未設定 (今後: mypy)

### テスト (今後拡充)

```bash
pytest tests/
```

## トラブルシューティング

### よくある問題と解決方法

#### 起動時に "ModuleNotFoundError: No module named 'pygwalker'" エラー

```bash
# パッケージが正しくインストールされていません
pip install -e .
```

#### ファイルを開いても UI が表示されない

- **原因**: PyGWalker HTML 生成に失敗している
- **解決**: コンソール出力を確認し、エラーメッセージを確認してください

#### メモリ使用量が多い

- **原因**: kernel_computation (DuckDB) でメモリに全データをロード
- **解決**:
  - ファイルサイズを小さくする
  - Parquet 形式を使用（より効率的）
  - フィルタを事前に適用

#### グラフが表示されない

- **原因**: フィールド配置が正しくない、またはデータ型エラー
- **解決**:
  - 左パネルのフィールドリストを確認
  - 行・列・色などが正しく配置されているか確認
  - データが NULL / 空でないか確認

## ライセンス

本プロジェクトは **Apache License 2.0** の下で公開されています。

詳細は [LICENSE](LICENSE) ファイルを参照してください。

### 使用ライセンス

- **PyGWalker**: Apache License 2.0
- **PySide6**: LGPL
- **pandas**: BSD 3-Clause
- **DuckDB**: MIT (PyGWalker の依存）

## 貢献

プルリクエストを歓迎します！

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. コミット (`git commit -m 'feat: amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## クレジット

- **PyGWalker**: [Kanaries](https://github.com/Kanaries/pygwalker) - Graphic Walker エンジン
- **PySide6**: [Qt for Python](https://wiki.qt.io/Qt_for_Python) - Qt 6 Python バインディング
- **pandas**: [pandas development team](https://pandas.pydata.org/)

## サポート

問題が発生した場合は、[GitHub Issues](https://github.com/Utakata/pygwalker-desktop/issues) で報告してください。

---

**Made with ❤️ using PyGWalker and PySide6**
