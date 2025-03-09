import requests
import hashlib
import base64
import json
import time
import os
from dotenv import load_dotenv
from PIL import Image
import io

# .envファイルを読み込む
load_dotenv()

# 設定
NETLIFY_URL = "https://posekit.netlify.app"
API_KEY = os.getenv("POSEKIT_API_KEY", "")

# APIキーをSHA-256でハッシュ化
def hash_api_key(api_key):
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()

# PIL画像をBase64エンコード
def encode_pil_image(pil_image):
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# photo2pose処理開始
def start_photo2pose(pil_image, model_name="sotai01_B_sd_mat=0.2.fbx", output_format="fbx,glb"):
    # エンドポイントURL
    url = f"{NETLIFY_URL}/.netlify/functions/photo2pose-runpod-start"
    
    # APIキーをハッシュ化
    hashed_api_key = hash_api_key(API_KEY)
    
    # 画像をエンコード
    base64_image = encode_pil_image(pil_image)
    
    # ヘッダー
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": hashed_api_key,
        "X-Source": "external"
    }
    
    # リクエストボディ
    payload = {
        "image": base64_image,
        "modelName": model_name,
        "format": output_format
    }
    
    # リクエスト送信
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"エラー: {response.status_code}")
        print(response.text)
        return None

# ジョブステータス取得（分割データ対応版）
def get_job_status(job_id):
    """
    RunPodのジョブステータスを取得し、大きなデータを分割して受け取る
    """
    url = f"{NETLIFY_URL}/.netlify/functions/photo2pose-runpod-status"
    
    # APIキーをハッシュ化
    hashed_api_key = hash_api_key(API_KEY)
    
    # ヘッダー
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": hashed_api_key,
        "X-Source": "external"
    }
    
    all_data = ''
    current_part = 0
    total_chunks = 1
    
    while current_part < total_chunks:
        # リクエストボディ
        payload = {
            "jobId": job_id,
            "part": current_part
        }
        
        # リクエスト送信
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"ステータス取得エラー: {response.status_code}")
            print(response.text)
            return None
            
        result = response.json()
        
        # 分割データを結合
        chunk = result.get('chunk', '')
        total_chunks = result.get('totalChunks', 1)
        is_last_chunk = result.get('isLastChunk', False)
        
        all_data += chunk
        
        if is_last_chunk:
            break
            
        current_part += 1
    
    # 完全なJSONデータをパース
    try:
        return json.loads(all_data)
    except json.JSONDecodeError as e:
        print(f"JSONデコードエラー: {e}")
        return None

# 処理結果のポーリング（ウェイトタイム最適化版）
def poll_for_result(job_id, max_attempts=30):
    print(f"ジョブID {job_id} の処理状況を確認しています...")
    
    # 初期待機時間を設定
    wait_times = [10, 5, 5, 3]  # 秒単位
    current_wait_index = 0
    
    for attempt in range(max_attempts):
        # 現在の待機時間を使用
        interval = wait_times[min(current_wait_index, len(wait_times) - 1)]
        time.sleep(interval)
        
        # ステータス確認（大きなデータ対応版）
        result = get_job_status(job_id)
        
        if not result:
            print("ステータス確認に失敗しました。再試行します...")
            continue
        
        status = result.get("status")
        
        if status == "COMPLETED":
            print("処理が完了しました！")
            return result
        elif status == "FAILED":
            print("処理が失敗しました。")
            print(result.get("error", "不明なエラー"))
            return None
        else:
            print(f"処理中... 待機時間: {interval}秒")
            # 次の待機インデックスへ進む（上限あり）
            current_wait_index = min(current_wait_index + 1, len(wait_times) - 1)
    
    print("タイムアウトしました。後でもう一度確認してください。")
    return None

# 結果からFBXとGLBデータを抽出
def extract_model_data(result):
    if result and result.get("status") == "COMPLETED" and result.get("output"):
        output = result.get("output", {})
        return [output.get("pose_model_data_fbx"), output.get("pose_model_data_glb")]
    return [None, None]

# メイン関数
def process_image(pil_image, model_name="sotai01_B_sd_mat=0.2.fbx"):
    """
    PIL画像を受け取り、3Dモデルを生成する
    
    Returns:
        tuple: (fbx_data, glb_data) - Base64エンコードされたモデルデータ
    """
    print("Photo2Pose処理を開始します...")
    result = start_photo2pose(pil_image, model_name=model_name)
    
    if not result:
        print("処理の開始に失敗しました。")
        return None, None
    
    job_id = result.get("jobId")
    print(f"ジョブIDが発行されました: {job_id}")
    
    # 結果を確認（最適化されたポーリングで）
    final_result = poll_for_result(job_id)
    
    if final_result and final_result.get("status") == "COMPLETED":
        # モデルデータを抽出
        fbx_data, glb_data = extract_model_data(final_result)
        return fbx_data, glb_data
    else:
        print("結果を取得できませんでした。")
        return None, None 