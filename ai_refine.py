"""
AI 提示词润色模块
提供调用大模型 API 进行提示词优化的功能
"""

import os
import json
import requests

# 默认的大模型 API 配置（可以根据实际情况修改）
DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-3.5-turbo"
API_KEY_ENV_VAR = "LLM_API_KEY"

# 使用项目根目录已有的 config.json 文件
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


def load_config():
    """加载项目配置（从 config.json）
    
    Returns:
        dict: 包含 drawthings_url, llm_api_url, llm_model, llm_api_key 的配置字典
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # 返回默认配置
    return {
        "drawthings_url": "http://127.0.0.1:7888",
        "llm_api_url": DEFAULT_API_URL,
        "llm_model": DEFAULT_MODEL,
        "llm_api_key": os.getenv(API_KEY_ENV_VAR, "")
    }


def save_config(config):
    """保存项目配置到 config.json
    
    Args:
        config (dict): 完整的配置字典
        
    Returns:
        bool: 保存成功返回 True
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"保存配置出错: {e}")
        return False


def refine_prompt_with_llm(prompt, language="zh"):
    """使用大模型润色提示词
    
    Args:
        prompt (str): 用户输入的原始提示词
        language (str): 目标语言，'zh' 为中文，'en' 为英文
        
    Returns:
        str: 润色后的提示词，如果失败则返回原始提示词
    """
    if not prompt or not prompt.strip():
        return prompt

    config = load_config()
    api_key = config.get("llm_api_key") or os.getenv(API_KEY_ENV_VAR)
    
    if not api_key:
        raise ValueError("未配置 LLM API Key。请在 config.json 中设置 llm_api_key 或在环境变量中设置 LLM_API_KEY。")

    # 构建系统提示词
    system_instruction = (
        "You are a professional AI art prompt engineer. "
        "Your task is to refine and enhance the user's prompt for image generation. "
        "Make it more descriptive, vivid, and detailed while keeping the original intent. "
        "Add artistic styles, lighting details, and composition suggestions if appropriate. "
        "IMPORTANT: Output ONLY the refined prompt text. Do NOT include any explanations, summaries, or conversational filler. "
    )
    
    if language == "zh":
        system_instruction += "Respond in Chinese."
    else:
        system_instruction += "Respond in English."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": config.get("llm_model", DEFAULT_MODEL),
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Refine this prompt: {prompt}"}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(
            config.get("llm_api_url", DEFAULT_API_URL),
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            refined_text = result["choices"][0]["message"]["content"].strip()
            return refined_text
        else:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            raise Exception(f"API 请求失败: {response.status_code} - {error_msg}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求错误: {str(e)}")

