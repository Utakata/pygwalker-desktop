# クイックスタートガイド

このガイドに従えば、5 分でアプリを起動できます。

## インストール

### ステップ 1: Python 確認

Python 3.10 以上がインストールされていることを確認してください。

```bash
python --version
# Python 3.12.x 以上が表示されれば OK
```

### ステップ 2: リポジトリクローン

```bash
git clone https://github.com/Utakata/pygwalker-desktop.git
cd pygwalker-desktop
```

### ステップ 3: インストール

```bash
pip install -e .
```

依存パッケージが自動的にインストールされます。

## 起動

```bash
python -m pygwalker_desktop
```

アプリが起動します！

## 最初のグラフを作成

### 1. ファイルを開く

1. `ファイル > 開く` をクリック
2. `sample_data.csv` を選択（プロジェクトフォルダに含まれています）

### 2. グラフを作成

1. 左パネルの **category** を **行** にドラッグ
2. **price** を **Y 軸** にドラッグ
3. **quantity** を **色** にドラッグ

グラフが自動的に生成されます！

### 3. グラフタイプを変更

グラフ上部のチャートタイプボタン（棒グラフ、折れ線グラフ、散布図など）をクリック

## よく使う操作

| 操作 | ショートカット |
|-----|-----------|
| ファイルを開く | Ctrl+O |
| アプリを閉じる | Ctrl+Q |
| ズームイン | Ctrl++ |
| ズームアウト | Ctrl+- |
| ズームリセット | Ctrl+0 |

## テーマを変更

表示メニュー > ライト / ダーク / システム

## サポートファイル形式

- **CSV / TSV** - comma/tab-separated values
- **Excel** - .xlsx, .xls
- **Parquet** - .parquet, .pq

## 次のステップ

詳細な使い方は [README.md](README.md) を参照してください。

## トラブル

### 起動しない場合

```bash
# パッケージを再度インストール
pip install -e . --force-reinstall
```

### モジュールが見つからない

```bash
# 依存パッケージを確認
pip list | grep -E "pygwalker|PySide6|pandas"
```

表示されない場合は、インストール手順を再度実行してください。

---

何か問題があれば、[Issues](https://github.com/Utakata/pygwalker-desktop/issues) で報告してください。
