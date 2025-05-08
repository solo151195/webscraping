import time
from playwright_stealth import stealth_sync
from playwright.async_api import Playwright
import functions as fn

async def test_page(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy if proxy else None
    browser, context = await fn.get_browser(playwright, country, proxy_url)

    page = await context.new_page()
    # stealth_sync(page)
    try:
        # await page.goto("https://nowsecure.nl")
        await page.goto("https://bot.sannysoft.com")
        # await page.goto("https://www.jackpot50.de/")
        await page.wait_for_load_state("load")


        await fn.human_delay(2, 4)
        print("start test")
        time.sleep(600000)
    except Exception as e:
        print(f'Exception : {e}')
    finally:
        await context.close()
        await browser.close()
