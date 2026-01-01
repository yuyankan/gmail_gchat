import os
from playwright.sync_api import sync_playwright

PBI_URL = "https://app.powerbi.com/singleSignOn?ru=https%3A%2F%2Fapp.powerbi.com%2F%3FnoSignUpCheck%3D1"
AUTH_JSON = "auth.json"

USERNAME = os.getenv("PBI_USERNAME", "caren.kan@averydennison1.onmicrosoft.com")
PASSWORD = os.getenv("PBI_PASSWORD", "Hihi202612345678")

if not USERNAME or not PASSWORD:
    print("❌ 错误：请设置 PBI_USERNAME 和 PBI_PASSWORD 环境变量。")
    exit(1)

def automated_login():
    browser = None
    try:
        with sync_playwright() as p:
            proxy_server = "http://127.0.0.1:9000"
            print(f"✅ 浏览器将使用代理: {proxy_server}")

            browser = p.chromium.launch(
                headless=False,
                proxy={"server": proxy_server}
            )
            
            context = browser.new_context()
            page = context.new_page()

            print("🔐 正在执行自动化登录...")
            page.goto(PBI_URL, wait_until="domcontentloaded", timeout=60000)
            
            # 等待邮箱输入框出现并填写
            email_locator = page.get_by_placeholder("Enter email") 
            email_locator.wait_for(state="visible", timeout=60000)
            email_locator.fill(USERNAME)
            print(f"✅ 已填写邮箱: {USERNAME}")
            
            # 点击“下一步”或提交按钮
            page.get_by_role("button", name="Submit").click()
            #page.click('input[type="submit"]')
            
            # 等待密码输入框出现并填写
            password_locator = page.get_by_placeholder("Password") # 根据你的密码输入框占位符进行修改
            password_locator.wait_for(state="visible", timeout=60000)
            password_locator.fill(PASSWORD)
            print("✅ 已填写密码")

            page.click('input[type="submit"]')

            page.get_by_role("button", name="Yes").click()
            
            # 等待页面跳转到 Power BI 主页
            page.wait_for_url("https://app.powerbi.com/home*", timeout=60000)
            
            # 检查是否登录成功
            if "Workspaces" in page.text_content("body"):
                print("✅ 登录成功，正在保存会话状态到 auth.json")
                context.storage_state(path=AUTH_JSON)
                print("✅ 会话状态已成功保存。")
            else:
                print("❌ 登录失败，请检查用户名或密码。")
                exit(1)

    except Exception as e:
        print(f"❌ 发生错误: {e}")
        exit(1)

    finally:
        if browser:
            browser.close()

if __name__ == "__main__":
    automated_login()