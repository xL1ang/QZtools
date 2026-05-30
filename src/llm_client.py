"""统一 LLM 调用封装，基于 OpenAI SDK 格式。"""

import time
from pathlib import Path

import yaml
from openai import OpenAI

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
MAX_RETRIES = 2


def load_config() -> dict:
    """读取 config.yaml 并返回当前 provider 的配置。"""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"配置文件不存在: {CONFIG_PATH}\n"
            "请复制 config.yaml.example 为 config.yaml 并填写 API 密钥。"
        )
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    provider_name = config.get("use_provider", "")
    providers = config.get("providers", {})

    if provider_name not in providers:
        raise ValueError(
            f"config.yaml 中 use_provider 填的是 '{provider_name}'，"
            f"但 providers 里没有这个配置。"
        )

    provider = providers[provider_name]
    if not provider.get("api_key"):
        raise ValueError(
            f"config.yaml 中 {provider_name} 的 api_key 为空，请填写你的密钥。"
        )

    return provider


def create_client() -> tuple[OpenAI, str]:
    """创建 OpenAI 客户端，返回 (client, model)。"""
    config = load_config()
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )
    return client, config["model"]


def chat(prompt: str) -> str:
    """发送 prompt 给 LLM，返回回复文本。自动重试。"""
    client, model = create_client()

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"  [重试] 第 {attempt + 1} 次调用失败: {e}")
                time.sleep(3)
            else:
                raise RuntimeError(
                    f"LLM 调用失败（已重试 {MAX_RETRIES} 次）: {e}\n"
                    "请检查：1. API 密钥是否正确  2. 网络是否通畅"
                ) from e
    # 不应到达此处，但满足类型检查
    raise RuntimeError("LLM 调用异常")
