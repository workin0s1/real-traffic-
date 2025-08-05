from flask import Flask, render_template, request
import asyncio
from playwright.async_api import async_playwright
import random

app = Flask(__name__)

# Load proxy and user-agent lists
def load_list(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

proxies = load_list('proxy_list.txt')
user_agents = load_list('user_agents.txt')

async def visit_site(url, proxy=None, user_agent=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True,
                                          proxy={"server": proxy} if proxy else None)
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(random.randint(15000, 30000))
            await page.mouse.wheel(0, 1000)
            await page.wait_for_timeout(random.randint(10000, 20000))
            with open("visits.log", "a") as log:
                log.write(f"Visited: {url} via {proxy or 'No Proxy'} | {user_agent}\n")
        except Exception as e:
            with open("visits.log", "a") as log:
                log.write(f"Failed: {url} via {proxy or 'No Proxy'} | {user_agent} | Error: {e}\n")
        await browser.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        count = int(request.form['count'])
        asyncio.create_task(run_visits(url, count))
        return f'Started {count} visits to {url} in background.'
    return render_template('index.html')

async def run_visits(url, count):
    tasks = []
    for _ in range(count):
        proxy = random.choice(proxies) if proxies else None
        user_agent = random.choice(user_agents) if user_agents else None
        tasks.append(visit_site(url, proxy, user_agent))
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
