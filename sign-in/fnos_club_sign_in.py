import os
import notify  # 不可删除
import httpx
import logging
import asyncio
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 固定签到地址
sign_in_url = "https://club.fnnas.com/plugin.php?id=zqlj_sign&sign=318dca41"

# 定义常量
COOKIE_ENV = 'FNOS_COOKIE'

def get_cookie_from_env():
    """从环境变量中读取 Cookie """
    cookie_string = os.environ.get(COOKIE_ENV, '')
    if not cookie_string:
        try:
            from qlpanel.some_module import get_env_variable
            cookie_string = get_env_variable(COOKIE_ENV)
        except ImportError:
            logging.error("未找到环境变量 %s，请确保已正确设置。", COOKIE_ENV)
            raise ValueError("未找到 Cookie")
    return cookie_string


async def check_response_status(response):
    """检查响应状态码并返回相应的消息"""
    if response.status_code == 200:
        if "您今天已经打过卡了，请勿重复操作！" in response.text:
            logging.info("今天已经签到过了，无需重复操作！")
            return "今天已经签到过了，无需重复操作！"
        elif "恭喜您，打卡成功！" in response.text:
            logging.info("恭喜您，打卡成功！")
            return "恭喜您，打卡成功！"
        else:
            logging.warning("未知响应内容，可能签到失败。")
            logging.debug("响应内容: %s", response.text)
            return "未知响应内容，可能签到失败。"
    else:
        logging.error("打卡失败！")
        logging.error("状态码: %s", response.status_code)
        logging.error("响应内容: %s", response.text)
        return f"打卡失败！状态码: {response.status_code}"


async def sign_in(sign_in_url, cookie_string):
    """执行签到操作"""
    if not cookie_string:
        logging.error("未找到 Cookie，无法进行签到。")
        return "未找到 Cookie，无法进行签到。"

    headers = {'Cookie': cookie_string}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(sign_in_url, headers=headers)
            return await check_response_status(response)  # 调用新方法
        except httpx.RequestError as e:
            logging.error("请求异常: %s", e)
            return f"请求异常: {e}"


async def send_notification(summary_message):
    """异步发送通知"""
    try:
        notify.send("飞牛OS论坛签到情况", summary_message)
    except Exception as e:
        logging.error("通知发送失败: %s", e)


async def main():
  
    try:
        # 编译代码
        cookie_string = get_cookie_from_env()
        logging.info("读取到的 Cookie: %s", cookie_string)
    except ValueError as e:
        logging.error(e)
        return

    # 执行签到
    sign_result = await sign_in(sign_in_url, cookie_string)

    # 生成通知内容
    summary_message = f"签到结果：{sign_result}"

    # 发送请求
    await send_notification(summary_message)


if __name__ == "__main__":
    asyncio.run(main())