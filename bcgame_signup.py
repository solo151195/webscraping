import asyncio
import os
import random
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync
from faker import Faker
import functions as fn

async def type_with_typo_and_correction(page, selector, value):
    locator = page.locator(selector)
    # Type full name
    await locator.type(value, delay=random.randint(100, 200))
    await asyncio.sleep(random.uniform(0.5, 1.2))  # Pause

    # Move cursor to start
    await locator.press("Home")
    await asyncio.sleep(random.uniform(0.2, 0.4))

    # Press Delete 3 times to remove "mal"
    for _ in range(3):
        await locator.press("Delete")
        await asyncio.sleep(random.uniform(0.1, 0.3))

async def bcgame_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()

    phone_number = "+" + number
    password = fake.password(length=random.randint(12, 15))

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://bc.game/login/regist", timeout=60000)
        await page.wait_for_load_state("load")
        await fn.human_delay(2, 4)
        # await page.wait_for_selector('xpath=/html/body/div[2]/div/div[2]/div/button[3]', timeout=30000)
        # close alert
        if await fn.check_element_exists(page, 'xpath=/html/body/div[7]/div[2]/div[1]/button'):
            await fn.safe_click(page, 'xpath=/html/body/div[7]/div[2]/div[1]/button')
        # sign up button
        # await fn.safe_click(page, 'xpath=/html/body/div[2]/div/div[2]/div/button[3]')
        # phone number and password
        await type_with_typo_and_correction(page, 'xpath=/html/body/div[5]/div/div/div/div/div/div/div[2]/form/div[1]/div/input', phone_number)
        await fn.safe_fill(page, 'xpath=/html/body/div[5]/div/div/div/div/div/div/div[2]/form/div[2]/input', password)
        # signup
        await fn.safe_click(page, 'xpath=/html/body/div[5]/div/div/div/div/div/div/div[2]/form/button')
        await fn.human_delay(5, 10)
        try:
            await page.wait_for_selector('xpath=/html/body/div[5]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/input', timeout=20000)
            code = await fn.wait_for_sms_code(number)
            if code:
                await fn.safe_fill(page, 'xpath=/html/body/div[5]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/input', code)
                await fn.safe_click(page, 'xpath=/html/body/div[5]/div/div[2]/div/div[2]/div/div/div[2]/button')
                await fn.human_delay(10, 15)

                os.makedirs("results", exist_ok=True)
                with open("results/bcgame-signup-success.txt", "a") as file:
                    file.write(number + "\n")

                if queue:
                    queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})
            else:
                if queue:
                    queue.put({"status": "fail", "message": f"{index} - {number} Failed to get code"})

        except PlaywrightTimeoutError:
            if queue:
                queue.put({"status": "fail", "message": f"{index} - {number} Code field did not appear"})

    except Exception as e:
        print(e)
        if queue:
            queue.put({"status": "fail", "message": f"{index} - {number} Failed to load or submit page"})

    finally:
        await context.clear_cookies()
        for page in context.pages:
            await page.evaluate("localStorage.clear(); sessionStorage.clear();")
        await context.clear_permissions()
        await context.close()
        await browser.close()