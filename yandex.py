import os
from playwright_stealth import stealth_sync
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
import functions as fn
from functions import human_delay


async def yandex_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)

    phone_number = number[3:]

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://passport.yandex.com/auth/reg")
        await page.wait_for_load_state("load")
        await fn.human_delay(2, 4)

        await page.wait_for_selector('input#passp-field-phone', timeout=30000)
        if await fn.check_element_exists(page, '#gdpr-popup-v3-button-mandatory'):
            await fn.safe_click(page, '#gdpr-popup-v3-button-mandatory')
        await fn.safe_click(page, 'button.IntPhoneInput-countryButton')
        # Always fill first and last name first
        await fn.safe_fill(page, 'input[name="country"]', country[:5])
        await fn.safe_click(page, 'li[data-code="+992"]')
        await fn.safe_fill(page, 'input#passp-field-phone', phone_number)
        await fn.safe_click(page, 'button[type="submit"]')

        try:
            await page.wait_for_selector('input[name="phoneCode"]', timeout=15000)
            code = await fn.wait_for_sms_code(number)

            if code:
                await fn.safe_fill(page, 'input[name="phoneCode"]', code)
                os.makedirs("results", exist_ok=True)
                with open("results/yandex-signup-success.txt", "a") as file:
                    file.write(number + "\n")
                if queue:
                    queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})
                await human_delay(5,7)
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
        await context.clear_permissions()
        await context.close()
        await browser.close()