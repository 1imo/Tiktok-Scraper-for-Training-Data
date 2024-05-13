from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import time
import json
from tiktok_uploader.auth import AuthBackend


class Tiktok:
    def __init__(self, cookie_path: str) -> None:
        driver = webdriver.Chrome()
        auth_backend = AuthBackend(cookies=cookie_path)
        self.driver = auth_backend.authenticate_agent(driver)

    def scrape(
        self,
        query: str,
        output_path: str = "scraped_results.json",
        target_results: int = 10,
    ) -> None:
        query = urllib.parse.quote(query)
        url = f"https://www.tiktok.com/search?q={query}"
        self.driver.get(url)

        scraped_results = []
        result_count = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while result_count < target_results:
            search_results = self.driver.find_elements(
                By.CSS_SELECTOR, 'div[class*="DivItemContainerForSearch"]'
            )

            for result in search_results:
                try:
                    caption_element = result.find_element(
                        By.CSS_SELECTOR, "div.css-1iy6zew-DivContainer.ejg0rhn0"
                    )
                    caption = caption_element.text.strip()

                    if caption:
                        scraped_results.append(caption)
                        result_count += 1

                    if result_count >= target_results:
                        break
                except Exception as e:
                    print(f"Error: {e}")
                    continue

            if result_count >= target_results:
                break

            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

            last_height = new_height

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(scraped_results, file, ensure_ascii=False, indent=4)

        print(f"Scraped {len(scraped_results)} results.")
        self.driver.quit()


if __name__ == "__main__":
    tiktok = Tiktok(cookie_path="../config/cookies.txt")
    tiktok.scrape(query="cars", target_results=5000)
