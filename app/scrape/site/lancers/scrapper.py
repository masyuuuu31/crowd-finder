from ...base.base_scrapper import BaseScrapper
from ....constants.const import PLATFORM_DOMAIN_LANCERS, PLATFORM_URL_LANCERS
from ....schema.schemas import ProjectInfoListResponse, ProjectInfo

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.remote.webdriver import WebDriver

import time

class LancersScrapper(BaseScrapper):

    @property
    def url_prefix(self):
        return PLATFORM_DOMAIN_LANCERS

    def run(self, driver) -> ProjectInfoListResponse:
        # 仕事受注トップページ
        driver.get(PLATFORM_URL_LANCERS)
        
        # 「仕事を探す」を押下
        btn = driver.find_element(By.XPATH, "//span[@class='css-16a2wt1']")
        btn.click()
        
        first_search = True
        
        categories = ["システム開発", "Web制作"]
        for category in categories:
            
            # カテゴリーから絞り込む
            category_anchor = driver.find_element(By.XPATH, f"//dl[contains(@class, 'p-search-sidenav__list') and contains(@class, 'js-sp-category-toggle-target')]//a[contains(normalize-space(text()), '{category}')]")
            category_anchor.click()

            time.sleep(1)
            
            # 初回検索時のみ絞り込みを行う
            if first_search:
                # 仕事スタイルで絞り込む（プロジェクト、コンペ）
                for checkbox_id in ['type-competition', 'type-project']:
                    target_chb = driver.find_element(By.ID, checkbox_id)
                    driver.execute_script("arguments[0].click();", target_chb)
                    
                # 絞り込む
                search_btn = driver.find_element(By.XPATH, "//div[contains(@class, 'p-search-sidenav__refine')]//input[@id='Search']")
                search_btn.click()
                
                time.sleep(3)
                
                first_search = False

            current_page = 1
            max_page = 3
        
            while current_page <= max_page:
                
                print(f"【{current_page}ページ目】")
                scrape_projects_on_current_page(driver)

                try:
                    next_link = driver.find_element(By.XPATH, "//span[contains(@class, 'c-pager__item--next') and contains(@class, 'c-pager__item')]/a")
                    driver.get(next_link.get_attribute("href"))
                    current_page += 1
                except Exception as e:
                    print("次ページが見つからないため終了:", e)
                    break

        
            # 全てのカテゴリーに戻る
            all_category = driver.find_element(By.XPATH, "//a[contains(@class, 'c-link') and contains(normalize-space(text()), 'すべてのカテゴリー')]")
            all_category.click()
            time.sleep(3)
        
def scrape_projects_on_current_page(driver: WebDriver):
    
    div_xpath = "//div[contains(@class,'p-search-job-media') and contains(@class, 'c-media--item')]"
    divs = driver.find_elements(By.XPATH, div_xpath)

    for i in range(len(divs)):
        divs = driver.find_elements(By.XPATH, div_xpath)
        div = divs[i]
        div.click()
        time.sleep(1.5)

        try:
            title = driver.find_element(By.TAG_NAME, "h1").text.strip()
            print("タイトル:", title)

            prices = [
                f"{num.text.strip()}{unit.text.strip()}"
                for num, unit in zip(
                    driver.find_elements(By.XPATH, "//span[contains(@class, 'price-number')]"),
                    driver.find_elements(By.XPATH, "//span[contains(@class, 'price-unit')]")
                )
            ]
            print("価格:", prices)

            deadline = driver.find_element(By.XPATH, "//span[contains(text(), '締切')]/following-sibling::span[1]").text.strip()
            delivery = driver.find_element(By.XPATH, "//span[contains(text(), '希望納期')]/following-sibling::span[1]").text.strip()
            print(f"締切: {deadline} / 納期: {delivery}")

            description = driver.find_element(By.XPATH, "//dd[contains(@class, 'p-work-detail-lancer__postscript-description')]")
            print("詳細:", description.text)

        except Exception as e:
            print("案件詳細取得エラー:", e)

        driver.back()
        time.sleep(1.5)