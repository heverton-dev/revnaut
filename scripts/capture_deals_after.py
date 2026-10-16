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
        
        # Realiza autenticacao com credenciais padrao
        user_input = page.locator("#login-username")
        pass_input = page.locator("#login-password")
        if await user_input.count() > 0:
            await user_input.fill("heverton")
            await pass_input.fill("admin123")
            await page.locator("button[type='submit']").click()
            await page.wait_for_timeout(1500)
            
        print("Navegando para #deals...")
        await page.goto("https://revnaut.vpsconexao.org/#deals", wait_until="networkidle")
        await page.wait_for_timeout(2500)
        
        deals_shot = dest_dir / "screenshot_deals_after.png"
        await page.screenshot(path=str(deals_shot))
        print(f"Salvo: {deals_shot}")
        
        # Clica na visualizacao em tabela
        table_btn = page.locator("#btn-table")
        if await table_btn.count() > 0:
            await table_btn.click()
            await page.wait_for_timeout(1000)
            table_shot = dest_dir / "screenshot_table_after.png"
            await page.screenshot(path=str(table_shot))
            print(f"Salvo: {table_shot}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
