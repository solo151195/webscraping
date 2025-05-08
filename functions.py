import asyncio
import re
import string
from datetime import datetime, timezone, timedelta
import requests
import random
from requests import RequestException
from urllib.parse import urlparse
from undetected_playwright import Malenia
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
import configs as config

def parse_proxy_line(line: str) -> None | dict[str, str | None] | dict[str, str]:
    line = line.strip()
    if not line:
        return None

    # Authenticated proxy (contains @)
    if "@" in line:
        if not line.startswith("http://") and not line.startswith("https://"):
            line = "http://" + line  # ensure it's a valid URL format

        parsed = urlparse(line)
        return {
            "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
            "username": parsed.username,
            "password": parsed.password
        }

    # IP-whitelisted proxy
    else:
        return {
            "server": f"http://{line}"
        }

async def get_browser(playwright, country, proxy_url=None):
    browser = await playwright.chromium.launch(
        headless=False,
        proxy=parse_proxy_line(proxy_url) if proxy_url else None,
        args=[
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--disable-popup-blocking',
        ],
    )
    context = await  browser.new_context(
        viewport=random.choice(config.screen_resolutions),
        user_agent=random.choice(config.CHROME_USER_AGENTS),
        bypass_csp=True,
        java_script_enabled=True,
        device_scale_factor=1,
        has_touch=False,
        is_mobile=False,
        locale='en-US',
        permissions=["geolocation"],
        color_scheme="light",
    )
    await Malenia.apply_stealth(context)
    await context.add_init_script(config.stealth_script_chromium)
    return browser, context


async def human_typing(locator, text):
    for char in text:
        await locator.type(char, delay=random.randint(*config.TYPING_DELAY))
    await human_delay()

async def human_mouse_movement(page, locator):
    await locator.scroll_into_view_if_needed(timeout=5000)
    box = await locator.bounding_box()
    if not box:
        raise ValueError("Bounding box not found for the element")

    # Get center of the element
    target_x = box["x"] + box["width"] / 2
    target_y = box["y"] + box["height"] / 2

    # Get current mouse position (Playwright doesn't track this, so start somewhere)
    curr_x, curr_y = random.randint(0, 200), random.randint(0, 200)
    await page.mouse.move(curr_x, curr_y)
    await human_delay()

    # Simulate step-by-step movement to target
    steps = random.randint(10, 15)
    for step in range(1, steps + 1):
        intermediate_x = curr_x + (target_x - curr_x) * step / steps
        intermediate_y = curr_y + (target_y - curr_y) * step / steps
        await page.mouse.move(intermediate_x, intermediate_y)
        await asyncio.sleep(random.uniform(0.01, 0.03))

    # Final small hover for realism
    await locator.hover(timeout=3000)
    await human_delay()

async def human_delay(a=config.MIN_DELAY, b=config.MAX_DELAY):
    await asyncio.sleep(random.uniform(a, b))

async def safe_click(page, selector):
    """Safely click an element with error handling."""
    locator = page.locator(selector)
    await human_mouse_movement(page, locator)
    await locator.click(timeout=config.TIMEOUT)
    await human_delay()

async def safe_fill(page, selector, value):
    """Safely fill an input field with error handling."""
    locator = page.locator(selector)
    await human_mouse_movement(page, locator)
    await human_typing(locator, value)

async def safe_select(page, selector, value):
    """Safely select an option from a dropdown."""
    locator = page.locator(selector)
    await human_mouse_movement(page, locator)
    await locator.select_option(value=value)
    await human_delay()

async def check_element_exists(page, selector, timeout=10000):
    """Check if an element exists within a timeout."""
    try:
        await page.locator(selector).first.wait_for(timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        return False

def load_lines_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

async def wait_for_sms_code(number):
    utc_time = (datetime.now(timezone.utc) - timedelta(minutes=1)).strftime("%H:%M")
    url = "url" + utc_time
    await human_delay(12, 15)
    try:
        response = requests.get(url).json()
        if response:
            for resp in response:
                if number == resp[2]:
                    code = ''.join(re.findall(r'\d', resp[3]))
                    return code
        return None
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            RequestException):
        return None

def generate_password(length=8):
    # Define character pools
    letters = string.ascii_letters
    digits = string.digits
    specials = string.punctuation

    # Ensure at least one of each requirement
    password = [
        random.choice(letters),
        random.choice(digits),
        random.choice(specials)
    ]

    # Fill the rest with random choices from all pools
    all_chars = letters + digits + specials
    password += random.choices(all_chars, k=length - 3)

    # Shuffle to avoid predictable patterns
    random.shuffle(password)

    return ''.join(password)
