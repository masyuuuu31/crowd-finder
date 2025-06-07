from ...base.base_scrapper import BaseScrapper
from ....constants.const import (
    PLATFORM_DOMAIN_CROWDWORKS, 
    PLATFORM_URL_CROWDWORKS, 
    PLATFORM_NM_CROWDWORKS, 
    DEBUG_MODE, 
    DEV_STOP_COUNT
)

from ....schema.schemas import ProjectInfo

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from ...infra.intraction_manager import random_delay, find_element, wait_browser_load
from selenium.webdriver.support.select import Select

from typing import List

class CrowdWorksScrapper(BaseScrapper):

    @property
    def url_prefix(self):
        return PLATFORM_DOMAIN_CROWDWORKS

    def run(self, driver) -> List[ProjectInfo]:
        
        all_projects: List[ProjectInfo] = []
        
        try:
            # 仕事受注トップページ
            driver.get(PLATFORM_URL_CROWDWORKS)
            
            categories = ["システム開発", "ホームページ制作"]
            
            for category in categories:
                
                
                print(f"=====  カテゴリー: {category}  ======================================")
                
                # リロード
                driver.refresh()
                wait_browser_load(driver)
                random_delay(delay_range=(0.7, 1.5))
                
                
                # カテゴリーから絞り込む
                a_list = find_element(driver, By.XPATH, f"//ul[contains(@class, 'jCNpP')]/li/a", multiple=True)
                for a in a_list:
                    if category in a.text.strip():
                        a.click()
                        break
                
                wait_browser_load(driver)
                random_delay()
                
                
                for checked_value in ['fixed_price', 'competition']:    
                    # 依頼形式
                    target_chb = find_element(driver, By.XPATH, f"//input[@value='{checked_value}']/ancestor::label[contains(@class, 'YWqwp')]")
                    target_chb.click()
                
                random_delay(delay_range=(1.0, 2.0))
                
                search_btn = find_element(driver, By.XPATH, "//button[contains(@class, 'ulqrU') and contains(text(), '絞り込む')]")
                search_btn.click()
                
                wait_browser_load(driver)
                random_delay()
                
                # 新着順に並び替え
                dropdown = find_element(driver, By.XPATH, "//div[contains(@class, 'MKl3X')]//select[contains(@class, 'WkB3D')]")
                select = Select(dropdown)
                select.select_by_index(1)
                
                # 遅延
                random_delay(delay_range=(1.0, 2.0))
                
                current_page = 1
                max_page = 2
                
                while current_page <= max_page:
                    
                    print(f"【{current_page}ページ目】")
                    # 情報取得
                    all_projects.extend(scrape_projects_on_current_page(driver, category))
                    
                    try:
                        tmp = find_element(driver, By.XPATH, "//a[contains(@class, 'de7Z2') and contains(@class, 'oVhqD') and contains(@class, 'H3VWB')]")
                        next_link = tmp.get_attribute("href")
                        driver.get(next_link)
                        current_page +=1
                    except Exception as e:
                        print("次ページが見つかりませんでした。")
                        break
                                
                # リロード
                driver.refresh()
                wait_browser_load(driver)
                random_delay()
                
                # 全てのカテゴリーに戻る
                all_category = find_element(driver, By.XPATH, "//div[contains(@class, 'aPI4e')]/a[contains(@class, 'dBE2G')]")
                all_category.click()
                random_delay(delay_range=(1.0, 2.0))
                
        except Exception as e:
            print(f"エラー発生: {e}")
        
        finally:
            return all_projects
            
            
def scrape_projects_on_current_page(driver: WebDriver, category: str) -> List[ProjectInfo]:

    results = []
    main_handle = driver.current_window_handle
    
    try:
        items = find_element(driver, By.XPATH, "//ul[contains(@class, 'gH9lt') and contains(@class, 'OW4Y6') and contains(@class, 'QH0Pz')]/li", multiple=True) 
        count = 1
    
        for item in items:
                
            # PR案件を除外
            pr_li = find_element(item, By.XPATH, ".//li[contains(@class, 'VXZpw')]", timeout=0.2)
            if pr_li:
                inner_buf = pr_li.text.strip()
                # インナーテキストがPRの場合は次案件へ
                if inner_buf == "PR":
                    print("PR案件のため、スキップ")
                    continue
                    
            if DEBUG_MODE and count > DEV_STOP_COUNT:
                break
            
            link = find_element(item, By.XPATH, ".//a[contains(@class, 'wB71r')]")
            if link:
                link.click()
            else:
                print("リンク取得失敗: 次データへ")
                continue

            count+=1
            
            random_delay(delay_range=(0.5, 1.0))
            
            # ウィンドウハンドルを切り替える
            driver.switch_to.window(driver.window_handles[-1])
            
            try:
                # タイトル取得
                title_elm = find_element(driver, By.XPATH, "//div[contains(@class, 'title_container') and contains(@class, 'title_detail')]//h1")
                if not title_elm:
                    raise RuntimeError("タイトル取得失敗")
                
                title = title_elm.text.strip()
                print(f"=== 案件名: {title} =========")
                
                table_rows = find_element(driver, By.XPATH, "//table[contains(@class, 'cw-table') and contains(@class, 'summary')]//tr", multiple=True)
                
                price = None
                deadline = None
                delivery = None
                
                for row in table_rows:
                    th = find_element(row, By.XPATH, ".//th")
                    th_text = th.text.strip()
                    
                    if "固定報酬制" in th_text or "コンペ" in th_text:
                        price_elm = find_element(row, By.XPATH, ".//td/div")
                        if price_elm:
                            price = price_elm.text.strip()
                            
                        else:
                            print("価格取得失敗")
                        
                    elif "応募期限" in th_text:
                        deadline_elm = find_element(row, By.XPATH, ".//td")
                        if deadline_elm:
                            deadline = deadline_elm.text.strip()
                        else:
                            print("締切取得失敗")
                        
                    elif "納品希望日" in th_text:
                        delivery_elm = find_element(row, By.XPATH, ".//td") 
                        if delivery_elm:
                            delivery = delivery_elm.text.strip()
                            
                            if delivery == "-":
                                delivery = None
                        else:
                            print("納期取得失敗")
                
                description = None
                
                description_elm = find_element(driver, By.XPATH, "//table[contains(@class, 'job_offer_detail_table')]//td[contains(@class, 'confirm_outside_link')]")
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
                    platform=PLATFORM_NM_CROWDWORKS,
                    url=driver.current_url,
                    category=category
                )
                results.append(project)
            
            except Exception as e:
                print(f"案件詳細取得エラー:{e}")
                
            finally:
                driver.close()
                driver.switch_to.window(main_handle)
            
                wait_browser_load(driver)
                random_delay(delay_range=(0.5, 1.0))

    except Exception as e:
        print(f"エラー発生: {e}")

    finally:
        if driver.current_window_handle != main_handle:
            driver.switch_to.window(main_handle)
            
            wait_browser_load(driver)
            random_delay(delay_range=(0.5, 1.0))
        
        return results