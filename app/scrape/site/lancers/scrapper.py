from ...base.base_scrapper import BaseScrapper
from ....constants.const import PLATFORM_DOMAIN_LANCERS, PLATFORM_URL_LANCERS, PLATFORM_NM_LANCERS, DEBUG_MODE, DEV_STOP_COUNT
from ....schema.schemas import ProjectInfo

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from ...infra.intraction_manager import random_delay, find_element, wait_browser_load

from typing import List

class LancersScrapper(BaseScrapper):

    @property
    def url_prefix(self):
        return PLATFORM_DOMAIN_LANCERS

    def run(self, driver) -> List[ProjectInfo]:
        
        all_projects: List[ProjectInfo] = []
        try:
            # 仕事受注トップページ
            driver.get(PLATFORM_URL_LANCERS)
            
            # 「仕事を探す」を押下
            btn = find_element(driver, By.XPATH, "//span[@class='css-16a2wt1']")
            btn.click()
            
            first_search = True
            
            categories = ["システム開発", "Web制作"]
            
            for category in categories:
                
                print(f"=====  カテゴリー: {category}  ======================================")
                
                # カテゴリーから絞り込む
                category_anchor = find_element(driver, By.XPATH,f"//dl[contains(@class, 'p-search-sidenav__list') and contains(@class, 'js-sp-category-toggle-target')]//a[contains(normalize-space(text()), '{category}')]")
                category_anchor.click()

                random_delay(delay_range=(0.5, 1.0))
                
                # 初回検索時のみ絞り込みを行う
                if first_search:
                    # 仕事スタイルで絞り込む（プロジェクト、コンペ）
                    for checkbox_id in ['type-competition', 'type-project']:
                        target_chb = find_element(driver, By.ID, checkbox_id)
                        driver.execute_script("arguments[0].click();", target_chb)
                        
                    # 絞り込む
                    search_btn = find_element(driver, By.XPATH, "//div[contains(@class, 'p-search-sidenav__refine')]//input[@id='Search']")
                    search_btn.click()
                    
                    random_delay(delay_range=(0.5, 1.0))
                    
                    first_search = False

                current_page = 1
                max_page = 2
            
                while current_page <= max_page:
                    
                    print(f"【{current_page}ページ目】")
                    all_projects.extend(scrape_projects_on_current_page(driver, category))

                    try:
                        next_link = find_element(driver, By.XPATH, "//span[contains(@class, 'c-pager__item--next') and contains(@class, 'c-pager__item')]/a")
                        driver.get(next_link.get_attribute("href"))
                        current_page += 1
                    except Exception as e:
                        print("次ページが見つからないため終了:", e)
                        break

                # 全てのカテゴリーに戻る
                all_category =find_element(driver, By.XPATH, "//a[contains(@class, 'c-link') and contains(normalize-space(text()), 'すべてのカテゴリー')]")
                all_category.click()
                random_delay(delay_range=(1.0, 2.0))
            
        except Exception as e:
            print(f"エラー発生: {e}")
        
        finally:
            return all_projects
        
def scrape_projects_on_current_page(driver: WebDriver, category: str) -> List[ProjectInfo]:
    results: List[ProjectInfo] = []
    
    div_xpath = "//div[contains(@class,'p-search-job-media') and contains(@class, 'c-media--item')]"
    divs = find_element(driver, By.XPATH, div_xpath, multiple=True)
    
    count = 0
    
    for div in divs:
        
        count+=1
        
        if DEBUG_MODE and count > DEV_STOP_COUNT:
            break
        
        div.click()
        random_delay(delay_range=(0.5, 1.0))

        try:
            # タイトル取得
            title_elm = find_element(driver, By.TAG_NAME, "h1")
    
            if not title_elm:
                raise RuntimeError("タイトル取得失敗")
            
            if "閲覧制限" in title_elm.text.strip():
                raise RuntimeError("閲覧制限")
            
            title = title_elm.text.strip()
            print(f"=== 案件名: {title} =========")

            # 価格の数値部分と単位部分をそれぞれ取得
            price_numbers = find_element(driver, By.XPATH, "//span[contains(@class, 'price-block')]//span[contains(@class, 'price-number')]", multiple=True)
            price_units = find_element(driver, By.XPATH, "//span[contains(@class, 'price-block')]//span[contains(@class, 'price-unit')]", multiple=True)
            price = None
            if price_numbers and price_units:
                price = " 〜 ".join([
                    f"{num.text.strip()}{unit.text.strip()}"
                    for num, unit in zip(price_numbers, price_units)
                ])
                print(f"価格: {price}")
            else:
                print("価格取得失敗")

            # 応募締切
            deadline_elm = find_element(driver, By.XPATH, "//span[contains(text(), '締切')]/following-sibling::span[1]")
            deadline = None
            if deadline_elm:
                deadline = deadline_elm.text.strip()
                print(f"応募締切: {deadline}")
            else:
                print("締切取得失敗")
            
            # 希望納期
            delivery_elm = find_element(driver, By.XPATH, "//span[contains(text(), '希望納期')]/following-sibling::span[1]")
            delivery = None
            if delivery_elm:
                delivery = delivery_elm.text.strip()
                print(f"希望納期: {delivery}")
            else:
                print("納期取得失敗")

            # 詳細
            description_elm = find_element(driver, By.XPATH, "//dd[contains(@class, 'p-work-detail-lancer__postscript-description')]")
            description = None
            if description_elm:
                description = description_elm.text.strip()
            else:
                print("詳細取得失敗")
            
            project = ProjectInfo(
                title=title,
                price=price,
                deadline=deadline,
                delivery=delivery,
                detail=description,
                platform=PLATFORM_NM_LANCERS,
                url=driver.current_url,
                category=category
            )  
            results.append(project)

        except Exception as e:
            print("案件詳細取得エラー:", e)
        
        driver.back()
        wait_browser_load(driver)
        random_delay(delay_range=(0.5, 1.0))
        
    return results