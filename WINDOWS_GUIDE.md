# Windows 環境ガイド

このガイドは、Windows 10/11 ユーザー向けの詳細なインストール・利用方法です。

## 必要な環境

### システム要件

- **OS**: Windows 10 (バージョン 1909 以降) / Windows 11
- **メモリ**: 最低 2GB、推奨 4GB 以上
- **ディスク容量**: 1GB 以上

### Python インストール

#### 1. Python をダウンロード

1. https://www.python.org/downloads/windows/ にアクセス
2. **「Python 3.12.x」** (最新版) の「Windows installer (64-bit)」をクリック

   ![Python Download](https://python.org/downloads/)

#### 2. Python インストーラを実行

1. ダウンロードした `python-3.x.x-amd64.exe` をダブルクリック
2. **重要**: 「Add Python 3.x to PATH」にチェックを入れる ✅

   ```
   ☑ Install launcher for all users
   ☑ Add Python 3.x to PATH  ← これを必ずチェック！
   ```

3. 「Customize installation」をクリック
4. 以下を確認して「Next」:
   - ☑ pip (パッケージマネージャー)
   - ☑ tcl/tk and IDLE
   - ☑ Python test suite

5. 「Install」をクリック

#### 3. Python インストール確認

Windows の **コマンドプロンプト** (cmd) を開きます：

1. **Win キー + R** を押す
2. `cmd` と入力して **Enter**

コマンドプロンプトで以下を実行：

```cmd
python --version
```

以下のように表示されれば成功：

```
Python 3.12.x
```

#### トラブル：「python は認識されていません」

**原因**: Python が PATH に登録されていない

**解決法**:

1. Python を再度インストール
2. インストール画面で「Add Python 3.x to PATH」にチェック
3. コンピュータを再起動
4. コマンドプロンプトを再度開く

## Git をインストール (オプションだが推奨)

### 1. Git for Windows をダウンロード

1. https://git-scm.com/download/win にアクセス
2. インストーラを自動ダウンロード（約 50MB）

### 2. インストール

1. ダウンロードした `Git-x.x.x-64-bit.exe` をダブルクリック
2. 「Next」を繰り返して進める
3. デフォルト設定でも OK

### 3. インストール確認

コマンドプロンプトで：

```cmd
git --version
```

## PyGWalker Desktop をインストール

### 方法 A: Git を使う (推奨)

#### ステップ 1: リポジトリをクローン

コマンドプロンプトで：

```cmd
cd C:\Users\YourUsername\Desktop
git clone https://github.com/Utakata/pygwalker-desktop.git
cd pygwalker-desktop
```

#### ステップ 2: インストール

```cmd
pip install -e .
```

進捗が表示され、最後に以下のように表示されれば成功：

```
Successfully installed pygwalker-desktop-0.1.0
```

### 方法 B: ZIP ダウンロード (Git なしの場合)

#### ステップ 1: コードをダウンロード

1. https://github.com/Utakata/pygwalker-desktop にアクセス
2. 緑の「Code」ボタンをクリック
3. 「Download ZIP」をクリック
4. `pygwalker-desktop-main.zip` がダウンロード

#### ステップ 2: 解凍

1. ダウンロードフォルダで ZIP を右クリック
2. 「すべて展開」をクリック
3. `C:\Users\YourUsername\Desktop\pygwalker-desktop-main\` に展開

#### ステップ 3: インストール

コマンドプロンプトで：

```cmd
cd C:\Users\YourUsername\Desktop\pygwalker-desktop-main
pip install -e .
```

## 起動方法

### 方法 1: コマンドプロンプトから起動 (推奨)

```cmd
python -m pygwalker_desktop
```

### 方法 2: ショートカットから起動

**ショートカットを作成** (Windows 10/11)

1. デスクトップで右クリック
2. 「新規作成」> 「ショートカット」
3. 「項目の場所を入力」に以下をコピー：

   ```
   python -m pygwalker_desktop
   ```

4. 「次へ」をクリック
5. ショートカット名を入力：`PyGWalker Desktop`
6. 「完了」をクリック

以降、このショートカットをダブルクリックで起動可能

### 方法 3: Windows ターミナル (Windows 11 推奨)

1. **Win キー** を押す
2. `terminal` と入力
3. 「Windows ターミナル」をクリック
4. 以下を実行：

   ```powershell
   python -m pygwalker_desktop
   ```

## スタンドアロン EXE 版の作成 (上級)

アプリを単一の `.exe` ファイルにまとめることができます。

### 前提条件

- PyGWalker Desktop がインストール済み

### ステップ 1: PyInstaller をインストール

```cmd
pip install pyinstaller
```

### ステップ 2: EXE を作成

リポジトリルートで：

```cmd
pyinstaller --onefile --windowed --name "PyGWalker Desktop" src/pygwalker_desktop/app.py
```

処理に 1-2 分かかります。

### ステップ 3: EXE を実行

`dist\PyGWalker Desktop.exe` をダブルクリック

#### トラブル: 「このファイルを実行できません」

Windows Defender がブロックしている可能性があります。

**解決法**:

1. ファイルを右クリック
2. 「プロパティ」をクリック
3. 「セキュリティ」セクションで「許可」をクリック
4. 「OK」をクリック

再度ダブルクリック

## ファイルを開く

### 方法 1: メニューから開く (推奨)

1. アプリが起動したら、「ファイル」メニューをクリック
2. 「開く」をクリック
3. CSV / Excel / Parquet ファイルを選択
4. 「開く」をクリック

### 方法 2: ドラッグ&ドロップ (今後のアップデート対応予定)

現在は未対応ですが、将来的には以下が可能になります：

```
エクスプローラーから CSV ファイルを
PyGWalker Desktop ウィンドウにドラッグ&ドロップ
```

### サンプルデータで試す

リポジトリに含まれる `sample_data.csv` を使用：

1. 「ファイル」> 「開く」
2. `sample_data.csv` を選択
3. 「開く」をクリック

### よく使う CSV の準備

自分の CSV を使う場合：

1. **フォーマット確認**:
   - 最初の行はカラム名
   - 日本語も含める場合は UTF-8 エンコーディング

2. **エンコーディング確認** (Windows の場合)

   メモ帳で CSV を開き：
   1. 「ファイル」> 「名前を付けて保存」
   2. 「文字コード」で **UTF-8** を選択
   3. 保存

## グラフの作成方法

### 基本操作

```
1. ファイルを開く
2. 左パネルのフィールド (列) をドラッグ
3. 右パネルの配置エリアにドロップ

配置エリア:
├── 行 (X 軸)
├── 列 (Y 軸)
├── 値 (数値の集計)
├── 色 (色分け)
├── サイズ (泡の大きさ)
└── フィルタ (条件絞り込み)
```

### 例 1: 棒グラフ (Category 別 Price)

```
1. 左パネルから "category" を "行" にドラッグ
2. 左パネルから "price" を "値" にドラッグ
3. グラフが自動生成されます
```

### 例 2: 折れ線グラフ (時系列)

```
1. "date" を "列" にドラッグ
2. "price" を "値" にドラッグ
3. グラフタイプを「折れ線」に切り替え
```

### グラフタイプ選択

グラフ上部のアイコンをクリック：
- 📊 棒グラフ
- 📈 折れ線グラフ
- 🔵 散布図
- 📦 ヒートマップ
- 🌍 地図
- その他...

## キーボードショートカット

| 操作 | ショートカット |
|------|-----------|
| ファイルを開く | Ctrl+O |
| アプリを閉じる | Ctrl+Q |
| ズームイン | Ctrl+++ |
| ズームアウト | Ctrl+- |
| ズームリセット | Ctrl+0 |

## テーマ変更

### 方法 1: メニューから

1. 「表示」メニューをクリック
2. 「ライト」「ダーク」「システム」から選択

### 方法 2: ツールバーから

ツールバーの「ライト」「ダーク」「自動」をクリック

**設定内容**:
- **ライト**: 白背景（日中推奨）
- **ダーク**: 黒背景（夜間推奨、目に優しい）
- **システム**: OS の設定に自動追従

## データのエクスポート

### グラフを PNG で保存 (Graphic Walker 組み込み)

1. グラフの右上のメニューアイコン (⋯) をクリック
2. 「Export as PNG」をクリック
3. ファイル保存ダイアログが表示
4. ファイル名を入力して「保存」

### グラフ設定を保存 (今後のアップデート)

予定中の機能：

```
「ファイル」> 「設定をエクスポート」
→ グラフ設定が JSON で保存
→ 後で「設定をインポート」で復元
```

## 大容量ファイルを開く

### データセットサイズ別の最適な方法

| ファイルサイズ | 形式 | 方法 |
|------------|------|------|
| < 100 MB | CSV | そのまま開く |
| 100 MB - 1 GB | CSV | Parquet に変換推奨 |
| 1 GB 以上 | CSV | **Parquet に変換必須** |
| - | Parquet | kernel_computation 自動有効 |

### CSV → Parquet 変換スクリプト

Python スクリプトで変換：

```python
import pandas as pd

# CSV を読み込み
df = pd.read_csv("large_file.csv")

# Parquet で保存（圧縮率 70-90%）
df.to_parquet("large_file.parquet")

print(f"変換完了: {len(df)} 行")
```

実行方法：

1. 上記コードをメモ帳に貼り付け
2. `convert.py` で保存
3. コマンドプロンプト：

   ```cmd
   python convert.py
   ```

4. `large_file.parquet` が生成
5. PyGWalker Desktop で開く

### メモリ不足エラーが出た場合

```
「MemoryError」「Out of memory」
```

**解決法**:

1. 他のアプリを閉じる
2. CSV を Parquet に変換
3. フィルタで行数を削減
4. メモリを 8GB 以上に増強

## トラブルシューティング

### Python が見つからない

```
'python' は認識されていません
```

**原因**: PATH 設定がない

**解決**:

1. Python を再インストール
2. 「Add Python to PATH」にチェック
3. コンピュータを再起動

### PyGWalker のインストールが失敗

```
ERROR: Could not find a version that satisfies the requirement
```

**原因**: pip が古い

**解決**:

```cmd
python -m pip install --upgrade pip
pip install -e .
```

### アプリが起動しない

```
ModuleNotFoundError: No module named 'pygwalker'
```

**原因**: インストールが不完全

**解決**:

```cmd
pip install -e . --force-reinstall
```

### CSV を開いても何も表示されない

**原因**: ファイルが破損、またはフォーマットが不正

**確認**:

1. メモ帳でファイルを開く
2. データが見えるか確認
3. 最初の行がカラム名か確認
4. エンコーディングが UTF-8 か確認 (日本語の場合)

### グラフが遅い / フリーズしたようにみえる

**原因**: データセットが大きい、kernel_computation で集計中

**確認**:

- ステータスバーに「kernel computation: active」と表示されていたら、処理中です
- 大規模データは数秒～数十秒かかることもあります

**待ってください** (1 分以内に完了するはずです)

## パフォーマンス Tips

### 快適に使うための設定

| 設定 | 推奨値 | 理由 |
|------|--------|------|
| RAM | 4 GB 以上 | メモリ効率向上 |
| SSD | 推奨 | ファイル読み込み高速化 |
| CPU | 4 コア以上 | DuckDB マルチスレッド |

### データセット最適化

1. **不要な列を削除**:
   - ファイルサイズ削減
   - メモリ効率向上

2. **Parquet 形式を利用**:
   - CSV より 70-90% 圧縮
   - 読み込み速度 10 倍高速

3. **事前フィルタ**:
   - 不要な行を削除
   - 処理時間短縮

## アップデート

### バージョン確認

```cmd
pip list | findstr pygwalker
```

### アップデート

```cmd
pip install --upgrade pygwalker-desktop
```

最新版がインストールされます。

## よくある質問 (FAQ)

### Q. インターネット接続は必要？

**A.** いいえ。完全オフラインで動作します。

### Q. データはクラウドに送信される？

**A.** いいえ。すべてローカルコンピュータで処理されます。

### Q. 大人数で同時に使える？

**A.** いいえ。単一ユーザー向けです。複数人で使う場合は、別々の PC で実行してください。

### Q. 日本語の CSV でも大丈夫？

**A.** はい。UTF-8 エンコーディングなら問題ありません。

### Q. Excel ファイルの複数シートに対応？

**A.** 現在は最初のシートのみ。将来のアップデートで対応予定。

### Q. グラフをパワーポイントに貼り付けたい

**A.** グラフを PNG でエクスポート → PowerPoint に挿入

## さらに詳しく

- 📖 [README.md](README.md) - 機能・技術仕様
- 🚀 [QUICKSTART.md](QUICKSTART.md) - 5分スタートガイド
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - 技術仕様書

---

**質問・バグ報告:** https://github.com/Utakata/pygwalker-desktop/issues

Happy data visualization! 📊
