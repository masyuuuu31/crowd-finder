from ...base.base_scrapper import BaseScrapper
from ....constants.const import PLATFORM_DOMAIN_COCONALA, PLATFORM_URL_COCONALA, PLATFORM_NM_COCONALA
from ....schema.schemas import ProjectInfo

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from ...infra.intraction_manager import random_delay, find_element, wait_browser_load

from typing import List


class CoconaraScrapper(BaseScrapper):

    @property
    def url_prefix(self):
        return PLATFORM_DOMAIN_COCONALA
    
    def run(self, driver):
        # 仕事受注トップページ
        driver.get(PLATFORM_URL_COCONALA)
        
        all_projects: List[ProjectInfo] = []
        categories = ["IT・プログラミング・開発", "Webサイト制作・Webデザイン"]
        first_search = True
        
        for category in categories:
            
            # リロード
            driver.refresh()
            wait_browser_load(driver)
            
            # カテゴリーから絞り込む
            category_btn = find_element(driver, By.XPATH,
                f"//button[contains(@class, 'c-searchCategory-button') and .//span[contains(@class, 'category-name') and contains(normalize-space(), '{category}')]]")
            category_btn.click()
            
            random_delay(delay_range=(0.5, 1.0))
            
            # 初回検索時のみ「募集中の仕事」に絞り込む
            if first_search:
                target_chb = find_element(driver, By.XPATH, 
                                          "//div[@class='c-searchRecruiting']//input[@class='check' and @type='checkbox']")
                target_chb.click()
                random_delay(delay_range=(0.5, 1.0))
                
                first_search = False
            
            current_page = 1
            max_page = 3
            
            while current_page <= max_page:
                
                print(f"【{current_page}ページ目】")
                all_projects.extend(scrape_projects_on_current_page(driver, category))
                
                try:
                    tmp = find_element(
                        driver, 
                        By.XPATH, 
                        "//a[contains(@class, 'pagination-next') and not(@disabled) and .//i[contains(@class, 'coconala-icon') and contains(@class, '-chevron-right')]]")
                    if not tmp:
                        raise RuntimeError("次ページへのリンクが見つかりません")
                    
                    next_link =  tmp.get_attribute("href")
                    current_page += 1
                except Exception as e:
                    print("次ページが見つからないため終了:", e)
                    break
            
            # リロード
            driver.refresh()
            wait_browser_load(driver)
            
            all_category = find_element(driver, By.XPATH, 
                                        "//button[@class='c-searchCategory-button' and .//span[@class='category-name' and contains(normalize-space(), 'すべてのカテゴリ')]]")
            all_category.click()
            random_delay(delay_range=(1.0, 2.0))


def scrape_projects_on_current_page(driver: WebDriver, category: str) -> List[ProjectInfo]:

    results = []
    items_xpath = "//div[contains(@class, 'searchItemWrapper') and contains(@class, 'c-searchItemWrapper-hoverShadow')]/a[contains(@class, 'c-searchItem_detailLink')]"
    items = find_element(driver, By.XPATH, items_xpath, multiple=True)
    hrefs = []
    for item in items:
        hrefs.append(item.get_attribute("href"))

    for href in hrefs:
                                                
        driver.get(href)                    
        random_delay(delay_range=(0.5, 1.0))
        
        try:
            # タイトル取得
            title_elm = find_element(driver, By.TAG_NAME, "h1")

            if not title_elm:
                raise RuntimeError("タイトル取得失敗")
            
            title = title_elm.text.strip()
            print(title)
            
            
            content_rows = find_element(driver, By.XPATH, "//div[@class='c-requestOutline']//div[contains(@class, 'c-requestOutlineRow_content')]", multiple=True)
            
            for i, row in enumerate(content_rows):
                
                # 予算
                if i == 0:
                    price_elms = find_element(row, By.XPATH, ".//div[contains(@class, 'd-requestBudget')]//span[contains(@class, 'd-requestBudget_emphasis')]", multiple=True)
                    if price_elms:
                        for v in price_elms:
                            print(v.text.strip())
                    else:
                        pass
                
                # 希望納品日
                elif i == 1:
                    delivery_elm = find_element(row, By.XPATH, ".//span")
                    if delivery_elm:
                        print(delivery_elm.text.strip())
                    else:
                        pass
                
                # 応募締切
                elif i == 2:
                    deadline_elm = find_element(row, By.XPATH, ".//span[contains(@class, 'c-requestOutlineRowContent_additional')]/span[contains(text(), '締切日')]")
                    if deadline_elm:
                        print(deadline_elm.text.strip())
                    else:
                        pass
                
            description_elm = find_element(driver, By.XPATH, "//div[contains(@class, 'c-detailRowContentText')]")
            if description_elm:
                print(description_elm.text.strip())
            else:
                pass
            
        except Exception as e:
            print("案件詳細取得エラー:", e)
            
        driver.back()
        random_delay()