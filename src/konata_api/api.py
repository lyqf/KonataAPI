import requests


def query_balance(
    api_key: str,
    base_url: str = "",
    subscription_api: str = "/v1/dashboard/billing/subscription",
    usage_api: str = "/v1/dashboard/billing/usage"
) -> dict:
    """
    查询中转站余额（USD 和 Token 两种统计）

    Args:
        api_key: API Key (sk-xxx 格式)
        base_url: API 基础地址，默认 cifang.xyz，可换成其他中转站
        subscription_api: 订阅信息接口路径
        usage_api: 用量信息接口路径

    Returns:
        dict: 包含余额信息的字典
            - USD 统计: hard_limit_usd, used_usd, remaining_usd
            - Token 统计: total_granted, total_used, total_available
    """
    base = base_url.rstrip("/")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    result = {}
    raw_responses = {}  # 保存原始返回数据

    # 1. 查询 USD 余额 (OpenAI 兼容 API)
    try:
        sub_resp = requests.get(
            f"{base}{subscription_api}", headers=headers, timeout=10
        )
        sub_resp.raise_for_status()
        sub_data = sub_resp.json()
        raw_responses["subscription"] = sub_data
        result["hard_limit_usd"] = sub_data.get("hard_limit_usd", 0)

        # 计算日期范围（最近 100 天）
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=100)

        usage_resp = requests.get(
            f"{base}{usage_api}",
            headers=headers,
            params={
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            },
            timeout=10,
        )
        usage_resp.raise_for_status()
        usage_data = usage_resp.json()
        raw_responses["usage"] = usage_data
        total_usage_cents = usage_data.get("total_usage", 0)
        result["used_usd"] = round(total_usage_cents / 100, 2)
        result["remaining_usd"] = round(
            result["hard_limit_usd"] - result["used_usd"], 2
        )
    except requests.exceptions.RequestException:
        pass  # billing API 可能不可用，继续尝试其他接口

    # 2. 查询 Token 用量 (NewAPI 风格)
    try:
        token_resp = requests.get(
            f"{base}/api/usage/token/", headers=headers, timeout=10
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()
        raw_responses["token"] = token_data
        if token_data.get("code") and "data" in token_data:
            data = token_data["data"]
            result["total_granted"] = data.get("total_granted", 0)
            result["total_used"] = data.get("total_used", 0)
            result["total_available"] = data.get("total_available", 0)
    except requests.exceptions.RequestException:
        pass  # token API 可能不可用

    if not result:
        result["error"] = "无法获取余额信息"

    result["raw_response"] = raw_responses
    return result


def query_logs(
    api_key: str,
    base_url: str,
    page_size: int = 50,
    page: int = 1,
    order: str = "desc",
    custom_api_path: str = "",
    proxy_url: str = "",
) -> dict:
    """
    查询调用日志（使用 API Key）

    Args:
        api_key: API Key (sk-xxx 格式)
        base_url: API 基础地址
        page_size: 每页返回多少条日志（默认 50）
        page: 页码（默认 1）
        order: 排序方式，desc=降序/最新在前，asc=升序（默认 desc）
        custom_api_path: 自定义日志接口路径（如 /api/log/custom），留空使用默认 /api/log/token
        proxy_url: 代理地址（如 https://proxy.cifang.xyz/proxy），留空则直接访问

    Returns:
        dict: 包含日志列表的字典
            - total: 总条数
            - items: 日志列表，每条包含 model_name, token_name, quota,
                     prompt_tokens, completion_tokens, created_at 等
            - raw_response: 原始 API 返回数据
    """
    from urllib.parse import urlencode, quote

    base = base_url.rstrip("/")
    api_path = custom_api_path.strip() if custom_api_path else "/api/log/token"

    # 构建目标 URL
    target_url = f"{base}{api_path}?key={api_key}&p={page}&per_page={page_size}&order={order}"

    # 如果有代理，通过代理访问
    if proxy_url.strip():
        request_url = f"{proxy_url.rstrip('/')}?url={quote(target_url, safe='')}"
        params = None
    else:
        request_url = f"{base}{api_path}"
        params = {
            "key": api_key,
            "p": page,
            "per_page": page_size,
            "order": order,
        }

    try:
        resp = requests.get(request_url, params=params, timeout=10)
        resp.raise_for_status()

        # 检查响应内容是否为空
        if not resp.text.strip():
            return {"error": "API 返回空响应，请检查接口路径是否正确"}

        try:
            data = resp.json()
        except ValueError:
            # JSON 解析失败，返回原始内容的前200字符
            preview = resp.text[:200] if len(resp.text) > 200 else resp.text
            return {"error": f"API 返回非 JSON 格式: {preview}"}

        # 保存原始返回数据
        raw_response = data

        # 新接口直接返回 {"data": [...]}
        items = data.get("data", [])

        # 强制按 created_at 降序排序（确保最新的在前面）
        # 因为有些 API 不支持 order 参数
        items = sorted(items, key=lambda x: x.get("created_at", 0), reverse=True)

        return {
            "total": len(items),
            "items": items,
            "raw_response": raw_response
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # 测试用法示例
    # test_key = "sk-your-api-key"
    # base_url = "https://your-api-url.com"
    # result = query_balance(test_key, base_url)
    # print("余额:", result)
    pass
