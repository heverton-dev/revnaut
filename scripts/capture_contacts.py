import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def main():
    dest_dir = Path("docs/reconstruct_rvops")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        
        print("Acessando pagina de login...")
        await page.goto("https://revnaut.vpsconexao.org/#login", wait_until="networkidle")
        
        user_input = page.locator("#login-username")
        pass_input = page.locator("#login-password")
        if await user_input.count() > 0:
            await user_input.fill("heverton")
            await pass_input.fill("admin123")
            await page.locator("button[type='submit']").click()
            await page.wait_for_timeout(1500)
            
        print("Navegando para #contacts...")
        await page.goto("https://revnaut.vpsconexao.org/?v=contacts#contacts", wait_until="networkidle")
        await page.wait_for_timeout(2500)
        
        shot_path = dest_dir / "screenshot_contacts_after.png"
        await page.screenshot(path=str(shot_path))
        print(f"Salvo com sucesso: {shot_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
