from ...base.base_scrapper import BaseScrapper
from ....constants.const import PLATFORM_DOMAIN_COCONALA, PLATFORM_URL_COCONALA, PLATFORM_NM_COCONALA, DEBUG_MODE, DEV_STOP_COUNT
from ....schema.schemas import ProjectInfo

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from ...infra.intraction_manager import random_delay, find_element, wait_browser_load

from typing import List


class CoconaraScrapper(BaseScrapper):

    @property
    def url_prefix(self):
        return PLATFORM_DOMAIN_COCONALA
    
    def run(self, driver) -> List[ProjectInfo]:
        
        all_projects: List[ProjectInfo] = []
        
        try:
            # 仕事受注トップページ
            driver.get(PLATFORM_URL_COCONALA)
            
            categories = ["IT・プログラミング・開発", "Webサイト制作・Webデザイン"]
            first_search = True
            
            for category in categories:
                
                print(f"=====  カテゴリー: {category}  ======================================")
                
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
                max_page = 2
                
                while current_page <= max_page:
                    
                    print(f"【{current_page}ページ目】")
                    all_projects.extend(scrape_projects_on_current_page(driver, category))
                    
                    try:
                        # parent_a = find_element(
                        #     driver, 
                        #     By.XPATH, 
                        #     "//a[contains(@class, 'pagination-next') and contains(@class, 'nuxt-link-active')]")                    
                        # if not parent_a:
                        #     raise RuntimeError("リンクaタグの取得に失敗")
                        
                        # child_i = find_element(parent_a, By.XPATH, "./i[contains(@class, '-chevron-right')]")
                        # if not child_i:
                        #     raise RuntimeError("子要素のiタグの取得に失敗")
                            
                        # aタグをクリック
                        # driver.execute_script("arguments[0].click();", parent_a)
                        
                        next_btn = driver.find_element(
                            By.XPATH,
                            # 「pagination-next」クラスを持ち、
                            "//a[contains(concat(' ', normalize-space(@class), ' '), ' pagination-next ')]"
                            # かつ直下に chevron-right アイコンを持つ
                            + "[./i[contains(concat(' ', normalize-space(@class), ' '), ' -chevron-right ')]]"
                            )
                        
                        driver.execute_script("arguments[0].click();", next_btn)
                    
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
        
        except Exception as e:
            print(f"エラー発生: {e}")
        
        finally:
            return all_projects


def scrape_projects_on_current_page(driver: WebDriver, category: str) -> List[ProjectInfo]:
    proc_name = "scrape_projects_on_current_page"
    
    results = []
    main_handle = driver.current_window_handle
    
    try:
        items_xpath = "//div[contains(@class, 'searchItemWrapper') and contains(@class, 'c-searchItemWrapper-hoverShadow')]/a[contains(@class, 'c-searchItem_detailLink')]"
        items = find_element(driver, By.XPATH, items_xpath, multiple=True)
        count = 0
        
        for item in items:
            
            count+=1
            
            if DEBUG_MODE and count > DEV_STOP_COUNT:
                break
                                
            item.click()               
            random_delay(delay_range=(0.5, 1.0))
            
            # ウィンドウハンドルを切り替える
            driver.switch_to.window(driver.window_handles[-1])
            
            try:
                
                # ランダム遅延
                random_delay()
                
                # タイトル取得
                title_elm = find_element(driver, By.TAG_NAME, "h1")

                if not title_elm:
                    raise RuntimeError("タイトル取得失敗")
                
                title = title_elm.text.strip()
                print(f"=== 案件名: {title} =========")
                
                content_rows = find_element(driver, By.XPATH, "//div[@class='c-requestOutline']//div[contains(@class, 'c-requestOutlineRow_content')]", multiple=True)
                
                price = None
                price_parts = []
                deadline = None
                delivery = None
                
                for i, row in enumerate(content_rows):
                    
                    # 予算
                    if i == 0:
                        price_elms = find_element(row, By.XPATH, ".//div[contains(@class, 'd-requestBudget')]//span[contains(@class, 'd-requestBudget_emphasis')]", multiple=True)
                        if price_elms:
                            for elm in price_elms:
                                text = elm.text.strip()
                                if text:
                                    price_parts.append(text)
                            if price_parts:
                                price = "~".join(price_parts)
                                print(f"価格: {price}")
                        else:
                            print("価格取得失敗")
                    
                    # 希望納品日
                    elif i == 1:
                        delivery_elm = find_element(row, By.XPATH, ".//span")
                        if delivery_elm:
                            delivery = delivery_elm.text.strip()
                            print(f"希望納期: {delivery}")
                        else:
                            print("納期取得失敗")
                    
                    # 応募締切
                    elif i == 2:
                        deadline_elm = find_element(row, By.XPATH, ".//span[contains(@class, 'c-requestOutlineRowContent_additional')]/span[contains(text(), '締切日')]")
                        if deadline_elm:
                            deadline = deadline_elm.text.strip()[3:-1]
                            print(f"応募締切: {deadline[3:-1]}")
                        else:
                            print("応募締切取得失敗")

                
                description = None
                
                description_elm = find_element(driver, By.XPATH, "//div[contains(@class, 'c-detailRowContentText')]")
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
                    platform=PLATFORM_NM_COCONALA,
                    url=driver.current_url,
                    category=category
                )
                results.append(project)
            
            
            except Exception as e:
                print("案件詳細取得エラー:", e)
            
            finally:
                driver.close()
                driver.switch_to.window(main_handle)
                
                wait_browser_load(driver)
                random_delay()
        
    except Exception as e:
        print(f"エラー発生: {e}")
    
    finally:
        if driver.current_window_handle != main_handle:
            driver.switch_to.window(main_handle)
            
            wait_browser_load(driver)
            random_delay(delay_range=(0.5, 1.0))
            
        return results