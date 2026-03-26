# アーキテクチャドキュメント

## 概要

PyGWalker Desktop は、**Qt 6 ベースのデスクトップ GUI** と **ローカル HTTP サーバー** を組み合わせることで、PyGWalker (Graphic Walker) の Tableau 風 UI をスタンドアロンアプリケーションとして提供します。

## システムアーキテクチャ図

```
┌─────────────────────────────────────────────────┐
│           アプリケーションプロセス               │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │  メインスレッド (Qt イベントループ)      │   │
│  ├──────────────────────────────────────────┤   │
│  │                                          │   │
│  │  ┌─────────────────────────────────┐   │   │
│  │  │  MainWindow (QMainWindow)       │   │   │
│  │  │  - メニューバー                  │   │   │
│  │  │  - ツールバー                    │   │   │
│  │  │  - ステータスバー                │   │   │
│  │  │  - Web View (QWebEngineView)    │   │   │
│  │  └──────────────────┬──────────────┘   │   │
│  │                     │                   │   │
│  │            HTTP GET/POST               │   │
│  │                     │                   │   │
│  │                     ▼                   │   │
│  │          http://127.0.0.1:{port}      │   │
│  │                                        │   │
│  └────────────────────────────────────────┘   │
│                     │                         │
│  ┌──────────────────▼────────────────────┐   │
│  │  サーバースレッド (ServerBridge)      │   │
│  ├──────────────────────────────────────┤   │
│  │                                      │   │
│  │  ┌─────────────────────────────┐    │   │
│  │  │  HTTPServer                 │    │   │
│  │  │  - GET / → HTML             │    │   │
│  │  │  - POST /comm → JSON        │    │   │
│  │  │  - GET /health              │    │   │
│  │  └──────────────┬──────────────┘    │   │
│  │                 │                   │   │
│  │  ┌──────────────▼──────────────┐    │   │
│  │  │  PygWalker インスタンス      │    │   │
│  │  │  - データ管理                │    │   │
│  │  │  - フィールド定義            │    │   │
│  │  │  - ビジュアルスペック        │    │   │
│  │  │  - コミュニケーション層      │    │   │
│  │  └──────────────┬──────────────┘    │   │
│  │                 │                   │   │
│  │  ┌──────────────▼──────────────┐    │   │
│  │  │  データパーサー              │    │   │
│  │  │  - pandas DataFrame          │    │   │
│  │  │  - DuckDB (kernel_comp)     │    │   │
│  │  │  - SQL クエリ実行            │    │   │
│  │  └─────────────────────────────┘    │   │
│  │                                      │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │  ファイル読み込みスレッド (オプション) │   │
│  │  - 大容量 CSV 読み込み                │   │
│  │  - Excel シート読み込み              │   │
│  │  - Parquet ファイル読み込み          │   │
│  └──────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

## コアコンポーネント

### 1. MainWindow (main_window.py)

**責務**: UI オーケストレーション

```python
class MainWindow(QMainWindow):
    - メニューバー (ファイル / 表示 / ヘルプ)
    - ツールバー (クイックアクション)
    - ステータスバー (データセット情報)
    - QWebEngineView (グラフ表示)
    - ServerBridge ライフサイクル管理
```

**主な処理**:
1. ユーザー操作（ファイル選択、テーマ変更）
2. DataLoader を使用した CSV/Excel/Parquet 読み込み
3. ServerBridge の起動・停止
4. シグナル/スロット による通信

### 2. ServerBridge (server/bridge.py)

**責務**: HTTP サーバーのライフサイクル管理

```python
class ServerBridge(QThread):
    - PygWalker インスタンス生成
    - HTTPServer (127.0.0.1:{port}) 起動
    - リクエスト処理
    - スレッドセーフなシャットダウン
```

**データフロー**:
```
MainWindow.open_file()
    ↓
DataLoader.load_file(path)
    ↓
ServerBridge(df, spec, appearance, ...)
    ↓ start()
ServerBridge.run() → HTTPServer.serve_forever()
    ↓ server_ready.emit(url)
MainWindow._on_server_ready(url)
    ↓
PygWalkerWebView.load_url(url)
    ↓ HTTP GET http://127.0.0.1:{port}
Handler.do_GET()
    ↓ walker._get_render_iframe()
PyGWalker HTML (2.8 MB)
    ↓
QWebEngineView レンダリング
    ↓
Graphic Walker UI 表示完了
```

### 3. HTTP Handler (server/handler.py)

**責務**: HTTP リクエスト処理

```python
class Handler(SimpleHTTPRequestHandler):
    do_GET():    # GET / → PyGWalker HTML 提供
    do_POST():   # POST /comm → DuckDB クエリ実行
```

#### GET / (メイン HTML)

```
リクエスト: GET http://127.0.0.1:8000/
    ↓
walker._get_props("web_server")
    ↓ props = {
        id, dataSource, version, visSpec, rawFields,
        themeKey, dark, useKernelCalc, ...
      }
props["communicationUrl"] = "comm"
    ↓
walker._get_render_iframe(props)
    ↓ HTML = <iframe> + Graphic Walker JS Bundle (2.8 MB)
    ↓
レスポンス: 200 OK
Content-type: text/html
Body: HTML (2.8 MB)
```

#### POST /comm (動的クエリ)

```
リクエスト: POST http://127.0.0.1:8000/comm
Content-type: application/json
Body: {
    "action": "get_datas_by_sql",
    "data": { "sql": "SELECT ... FROM ...", ... }
}
    ↓
walker.comm._receive_msg("get_datas_by_sql", {...})
    ↓
kernel_computation = True の場合:
    data_parser.get_datas_by_sql(sql)
        ↓
    DuckDB.execute(sql)  ← ここで高速集計！
        ↓
    結果セット返却
    ↓
レスポンス: 200 OK
Content-type: application/json
Body: { "status": "success", "data": [...] }
```

**kernel_computation の流れ**:

```
user が「Category ごとの Price 合計」を指定
    ↓
JavaScript: POST /comm
    {
        "action": "get_datas_by_payload",
        "data": {
            "drillBy": ["category"],
            "measures": ["price"],
            "aggregation": "sum"
        }
    }
    ↓
Handler.do_POST() → walker.comm._receive_msg()
    ↓
PygWalker が SQL を生成:
    SELECT category, SUM(price) FROM df GROUP BY category
    ↓
data_parser.get_datas_by_sql(sql)
    ↓
DuckDB.execute(sql)  ← 💨 高速！
    ↓
レスポンス JSON に結果を詰めて返却
    ↓
JavaScript: グラフ更新
```

### 4. Data Loader (data/loader.py)

**責務**: ファイル読み込みと正規化

```python
def load_file(filepath) -> pd.DataFrame:
    if .csv or .tsv:
        return pd.read_csv()
    elif .xlsx or .xls:
        return pd.read_excel()
    elif .parquet or .pq:
        return pd.read_parquet()
```

### 5. Web View (web_view.py)

**責務**: QWebEngineView の設定と初期化

```python
class PygWalkerWebView(QWebEngineView):
    _configure_settings():
        - JavaScript 有効化
        - LocalStorage 有効化
        - クリップボードアクセス許可
        - リモート URL アクセス許可
```

### 6. Settings Dialog (widgets/settings_dialog.py)

**責務**: ユーザー設定管理

```
外観 (Appearance):  media | light | dark
    → walker.appearance パラメータ
    → サーバー再起動時に反映

テーマ (Theme Key): g2 | vega
    → 視覚的スタイル選択

デフォルトタブ: vis | data
    → 起動時の初期表示タブ
```

すべての設定は `QSettings` で永続化されます。

## スレッドセーフティ

### メインスレッド (Qt イベントループ)

**処理**:
- UI レンダリング
- ユーザーインタラクション処理
- QWebEngineView 制御

**禁止事項**:
- ❌ PyGWalker インスタンスへのアクセス
- ❌ HTTP サーバー直接操作
- ❌ 重い計算処理（ブロッキング）

### サーバースレッド (ServerBridge)

**処理**:
- HTTP リクエスト処理
- PyGWalker インスタンス管理
- DuckDB クエリ実行

**通信方法**:
- シグナル: `server_ready(url)`, `server_error(error)`
- スロット: `MainWindow._on_server_ready()`, `_on_server_error()`

### スレッド間通信

```
MainWindow (メイン) → ServerBridge (サーバー)
- user clicks "Open File"
- _open_file() → _load_and_display(filepath)
- _start_server(df)
    ↓
- ServerBridge(df, ...).start()
    ↓ runs in background thread
    ↓ runs PygWalker + HTTPServer
    ↓
server_ready.emit(url)  ← signal (スレッドセーフ)
    ↓ (main thread へ自動切り替え)
MainWindow._on_server_ready(url)
    ↓
web_view.load_url(url)
    ↓
browser requests http://127.0.0.1:{port}
    ↓ (server thread)
Handler.do_GET() → PyGWalker HTML
    ↓
browser renders Graphic Walker
```

## データフロー

### ファイル読み込みから表示まで

```
1. ユーザーが「ファイルを開く」をクリック
   ↓
2. MainWindow._open_file()
   → QFileDialog.getOpenFileName()
   ↓
3. MainWindow._load_and_display(filepath)
   ↓
4. DataLoader.load_file(filepath)
   → pd.read_csv() / read_excel() / read_parquet()
   → pd.DataFrame
   ↓
5. MainWindow._start_server(df)
   ↓
6. ServerBridge(df, appearance="media", ...)
   ↓
7. ServerBridge.run() [サーバースレッド]
   ↓
8. PygWalker(dataset=df, ...)
   → DataFrame をメモリにロード
   ↓
9. walker._init_callback(BaseCommunication(...))
   → /comm エンドポイント登録
   ↓
10. HTTPServer(("127.0.0.1", port), handler_class).serve_forever()
    ↓
11. server_ready.emit(f"http://127.0.0.1:{port}")
    → シグナル (メインスレッドへ)
    ↓
12. MainWindow._on_server_ready(url) [メインスレッド]
    ↓
13. web_view.load_url(url)
    → QWebEngineView.setUrl(QUrl(url))
    ↓
14. QWebEngineView
    → HTTP GET http://127.0.0.1:{port}/
    ↓
15. Handler.do_GET() [サーバースレッド]
    ↓
16. walker._get_props("web_server")
    ↓
17. walker._get_render_iframe(props)
    ↓
18. HTML (2.8 MB) レスポンス
    ↓
19. QWebEngineView (Chromium)
    → HTML/JS/CSS パース
    → Graphic Walker UI レンダリング
    ↓
20. ✅ 表示完了！
```

### ユーザーがグラフを作成

```
21. ユーザーが
    - category を「行」にドラッグ
    - price を「Y 軸」にドラッグ
    ↓
22. JavaScript (Graphic Walker)
    → アクション発火
    → POST http://127.0.0.1:{port}/comm
    {
        "action": "get_datas_by_payload",
        "data": {
            "drillBy": ["category"],
            "measures": ["price"]
        }
    }
    ↓
23. Handler.do_POST("/comm") [サーバースレッド]
    ↓
24. walker.comm._receive_msg("get_datas_by_payload", data)
    ↓
25. kernel_computation = True の場合:
    data_parser.get_datas_by_sql(
        "SELECT category, SUM(price) FROM ... GROUP BY category"
    )
    ↓
26. DuckDB.execute(sql)
    → メモリ内データベース (超高速)
    ↓
27. 集計結果 JSON
    {
        "status": "success",
        "data": [
            {"category": "Electronics", "price": 50000},
            {"category": "Clothing", "price": 25000},
            ...
        ]
    }
    ↓
28. レスポンス返却
    ↓
29. JavaScript
    → グラフ レンダリング (D3/Vega)
    → 💥 グラフ表示！
```

## パフォーマンス最適化

### 1. ローカルサーバーの利点

| 方法 | HTML制限 | kernel_comp | 説明 |
|------|---------|-----------|------|
| setHtml() | **2 MB** | ❌ | Chromium の制限により実装不可 |
| ローカルサーバー | **無制限** | ✅ | 高性能、動的生成対応 |

### 2. kernel_computation による高速化

```
データセットサイズ: 1 GB
行数: 10,000,000 rows

JavaScript 計算:
  SUM(price) GROUP BY category
  → ブラウザ内で処理
  → 10M行全体をメモリに展開 (遅い)
  ↓
  ~5-10 秒

DuckDB (kernel_computation):
  SELECT SUM(price) FROM table GROUP BY category
  → C++ で最適化された計算
  → インデックス活用
  ↓
  ~100-500 ms (50倍高速！)
```

### 3. メモリ効率

```
1GB ファイル読み込み時:

kernel_computation = False:
  - pandas DataFrame: 1 GB (メモリにロード)
  - JavaScript: 1 GB (ブラウザプロセス)
  → 合計 2 GB

kernel_computation = True:
  - pandas DataFrame: 1 GB (初期ロード)
  - DuckDB テーブル: 実データへのポインタ（コピーなし）
  - ブラウザ: クエリ結果のみ（数 MB）
  → 合計 ~1.1 GB
```

## セキュリティ考慮

### ローカルのみ バインド

```python
HTTPServer(("127.0.0.1", port), handler)
                  ↑
                127.0.0.1 = localhost のみ
                (外部からアクセス不可)
```

### データフロー

```
ユーザーコンピュータ:
  ファイル → DataFrame → DuckDB → JSON → QWebEngineView
                                              ↑
                                    localhost のみ
```

### プライバシー

- ✅ データはディスク保存されない
- ✅ ネットワーク送信なし
- ✅ クラウドサーバー利用なし
- ✅ 完全オフライン対応

## 拡張性

### 新しいファイルフォーマット追加

```python
# data/loader.py に追加
def load_file(filepath):
    ...
    elif suffix == ".json":
        return pd.read_json(filepath)
    elif suffix == ".sqlite":
        return pd.read_sql("SELECT * FROM ...", sqlite_conn)
```

### 新しいシグナル追加

```python
# server/bridge.py に追加
class ServerBridge(QThread):
    server_ready = Signal(str)
    server_error = Signal(str)
    query_executed = Signal(str, float)  ← 新規: クエリと実行時間
```

### 新しいハンドラエンドポイント追加

```python
# server/handler.py に追加
def do_POST(self):
    if path == "/export":
        # グラフ PNG エクスポート処理
```

## トラブルシューティング

### デバッグモード

```python
# server/bridge.py
def run(self):
    print(f"Starting server at http://127.0.0.1:{port}")
    print(f"PyGWalker GID: {walker.gid}")
    print(f"kernel_computation: {walker.kernel_computation}")
    self._httpd.serve_forever()
```

### ポート衝突

```python
# server/bridge.py
port = find_free_port()  # 自動的に空きポート検索
```

### スレッド デッドロック

```python
# ❌ 危険:
MainWindow → server_bridge.stop()
server_bridge.stop() → _httpd.shutdown()  # 待機...
                      → serve_forever() exit  # ここで待つ

# ✅ 安全:
server_bridge.stop()
    ↓
_httpd.shutdown()  (スレッドセーフ)
    ↓
wait(5000)  # 最大5秒待機
```

---

詳細な実装は、各ソースコードのコメントを参照してください。
