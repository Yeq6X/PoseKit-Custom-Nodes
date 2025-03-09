import os
import base64
import torch
import folder_paths
from PIL import Image
import torchvision.transforms.functional as TF

from .photo2pose import process_image

# 出力モデルを保存するディレクトリを設定
model_output_dir = os.path.join(folder_paths.output_directory, "photo2pose_models")
os.makedirs(model_output_dir, exist_ok=True)

# ComfyUIのカスタムノード: Photo2Pose
class Photo2Pose:
    def __init__(self):
        pass

    RETURN_TYPES = ("STRING", "STRING")  # FBXとGLBのファイルパスを返す
    RETURN_NAMES = ("fbx_path", "glb_path")
    FUNCTION = "process"
    OUTPUT_NODE = True
    CATEGORY = "3D_Models"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "model_name": (
                    [
                        "sotai01_B_sd_mat=0.2.fbx",
                        "sotai01_A_sd_mat=0.1.fbx",
                        "sotai02_sd_mat=0.2.fbx"
                    ],
                    {"default": "sotai01_B_sd_mat=0.2.fbx"}
                )
            },
        }

    def process(self, image, model_name):
        # torch.Tensorからpil imageに変換
        if len(image.shape) == 4:
            # バッチの最初の画像のみを使用
            image = image[0]
        
        # [H, W, C] -> [C, H, W]
        image = image.permute(2, 0, 1)
        
        # torch tensor -> PIL image
        pil_image = TF.to_pil_image(image)
        
        # 画像をAPIに送信し、3Dモデルを生成
        fbx_data, glb_data = process_image(pil_image, model_name)
        
        if fbx_data is None or glb_data is None:
            print("モデル生成に失敗しました")
            return "", ""
        
        # タイムスタンプベースのファイル名を生成
        import time
        timestamp = int(time.time())
        fbx_filename = f"pose_model_{timestamp}.fbx"
        glb_filename = f"pose_model_{timestamp}.glb"
        
        # ファイルパスを設定
        fbx_path = os.path.join(model_output_dir, fbx_filename)
        glb_path = os.path.join(model_output_dir, glb_filename)
        
        # Base64デコードしてファイルに保存
        with open(fbx_path, "wb") as f:
            f.write(base64.b64decode(fbx_data))
            print(f"FBXモデルを {fbx_path} として保存しました。")
            
        with open(glb_path, "wb") as f:
            f.write(base64.b64decode(glb_data))
            print(f"GLBモデルを {glb_path} として保存しました。")
        
        return fbx_path, glb_path

# ノードクラスのマッピング
NODE_CLASS_MAPPINGS = {
    "Photo2Pose": Photo2Pose
}

# ノード表示名のマッピング
NODE_DISPLAY_NAME_MAPPINGS = {
    "Photo2Pose": "Photo2Pose (3D Model Generator)"
} 