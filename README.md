# PoseKit Photo2Pose Custom Node for ComfyUI

このComfyUIカスタムノードは、画像から3Dポーズモデル（FBXおよびGLB形式）を生成します。

## 機能

- 画像を入力として、3Dポーズモデルを生成
- FBXとGLB形式のモデルを出力
- 複数のポーズモデルタイプをサポート

## インストール

1. このリポジトリをComfyUIの`custom_nodes`ディレクトリにクローンまたはダウンロードします。
2. 必要なPythonパッケージをインストールします：
   ```
   pip install python-dotenv requests Pillow
   ```
3. `.env`を編集して、APIキーを設定します。

## APIキーの設定

1. `.env`ファイル内の`POSEKIT_API_KEY`にあなたのAPIキーを設定します。

## 使用方法

1. ComfyUIワークフロー内で「Photo2Pose (3D Model Generator)」ノードを追加します。
2. 入力として画像を接続します。
3. 必要に応じてモデルタイプを選択します。
4. ワークフローを実行すると、出力ディレクトリに3Dモデルファイルが生成されます。

## 出力

- **fbx_path**: 生成されたFBXモデルのファイルパス
- **glb_path**: 生成されたGLBモデルのファイルパス

生成されたモデルファイルは、ComfyUIの出力ディレクトリ内の`photo2pose_models`フォルダに保存されます。

## サポートされているモデルタイプ

- sotai01_B_sd_mat=0.2.fbx
- sotai01_A_sd_mat=0.1.fbx
- sotai02_sd_mat=0.2.fbx 