# app/check_models.py
import google.generativeai as genai
import os

def check_available_models():
    """
    Connects to the Google AI API and lists all models available to the current
    API key that support the 'generateContent' method.
    """
    try:
        # Configure the API key from the environment variable
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("="*60)
            print("錯誤：找不到 GEMINI_API_KEY 環境變數。")
            print("請確認您已在啟動此腳本的終端機中正確設定它。")
            print("="*60)
            return

        genai.configure(api_key=api_key)
        
        print("\n正在查詢您的 API 金鑰可用的模型...")
        print("="*60)
        
        found_models = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
                found_models = True
        
        if not found_models:
            print("未找到任何支援 'generateContent' 的模型。")

        print("="*60)
        print("請將上面列表中的一個模型名稱複製給我。")

    except Exception as e:
        print(f"\n在查詢模型時發生錯誤: {e}")

if __name__ == "__main__":
    check_available_models()
