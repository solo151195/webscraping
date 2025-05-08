import os
import random
from playwright_stealth import stealth_sync
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from faker import Faker
import functions as fn

async def gofundme_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()
    gender = random.choice(["2", "1"])
    first_name = fake.first_name_female() if gender == "1" else fake.first_name_male()
    last_name = fake.last_name()
    email = first_name+"."+last_name+str(random.randint(1000,9999))+"@"+random.choice(['gmail.com','hotmail.com','outlook.com'])
    phone_number = number[3:]
    prefix = "+992"
    password = fake.password(length=random.randint(12, 20))
    page = await context.new_page()
    # stealth_sync(page)
    try:
        await page.goto("https://www.gofundme.com/sign-in", timeout=60000)
        await page.wait_for_load_state("load")

        await page.wait_for_selector('vaadin-email-field[id="3bFziHITxY"]', timeout=30000)
        await fn.human_delay(2, 4)
        await page.evaluate("""
            const blocker = document.getElementById('transcend-consent-manager');
            if (blocker) blocker.remove();
        """)
        await fn.human_delay(2, 4)

        await fn.safe_click(page, 'vaadin-email-field[id="3bFziHITxY"]')
        await fn.safe_fill(page, 'input[name="email"]', email)
        await fn.safe_click(page, 'vaadin-button[id="8nBgcJmDpl"]')

        await page.wait_for_selector('vaadin-text-field[name="firstName"]', timeout=15000)
        await fn.safe_click(page, 'vaadin-text-field[name="firstName"]')
        await fn.safe_fill(page, 'input[name="firstName"]', first_name)
        await fn.safe_click(page, 'descope-text-field[name="lastName"]')
        await fn.safe_click(page, 'vaadin-text-field[name="lastName"]')
        await fn.safe_fill(page, 'input[name="lastName"]', last_name)
        await fn.safe_click(page, 'descope-password[data-id="password"]')
        await fn.safe_click(page, 'vaadin-password-field[data-id="password"]')
        await fn.safe_fill(page, '#input-vaadin-password-field-23', password)
        await fn.safe_click(page, 'vaadin-button[id="8nBgcJmDpl"]')

        await page.wait_for_selector('vaadin-combo-box[label="Code"]', timeout=15000)
        await fn.safe_click(page, 'vaadin-combo-box[label="Code"]')
        code_field = page.locator('#input-vaadin-combo-box-42')
        await code_field.press('Control+A')
        await code_field.press('Backspace')
        await fn.safe_fill(page,"#input-vaadin-combo-box-42",prefix)
        await fn.safe_click(page, 'vaadin-combo-box-item[id="vaadin-combo-box-item-0"]')

        await fn.safe_click(page, 'descope-text-field[name="phone"]')
        await fn.safe_click(page, '#input-vaadin-text-field-37 >> vaadin-text-field[name="phone"]')
        await fn.safe_fill(page, 'input[name="phone"]', phone_number)
        await fn.safe_click(page, 'vaadin-button[id="ODpHRNvD-L"]')

        try:
            await page.wait_for_selector('vaadin-text-field[data-id="0"]', timeout=60000)
            code = await fn.wait_for_sms_code(number)
            if code:
                for index, value in enumerate(range(86, 108, 4)):
                    # await fn.safe_click(page, f'vaadin-text-field[data-id="{str(index)}"]')
                    await fn.safe_fill(page, f'input#input-vaadin-text-field-{str(value)}', code[index])
                os.makedirs("results", exist_ok=True)
                with open("results/gofundme-signup-success.txt", "a") as file:
                    file.write(number + "\n")
                if queue:
                    queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})
                await page.wait_for_selector('#home-start-cta', timeout=10000)
            else:
                if queue:
                    queue.put({"status": "fail", "message": f"{index} - {number} Failed to get code"})

        except PlaywrightTimeoutError:
            if queue:
                queue.put({"status": "error", "message": f"{index} - {number} Code field did not appear"})
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