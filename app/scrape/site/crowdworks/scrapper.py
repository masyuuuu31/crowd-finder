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
from ...infra.intraction_manager import random_delay, find_element, wait_browser_load, safe_click
from selenium.webdriver.support.select import Select

from typing import List

from ....utils.logger import setup_logger

from ....config import BASE_DIR
import os

log_file = os.path.join(BASE_DIR, "logs", "server.log")

# 共通ロガーをセットアップ
logger = setup_logger(__name__, log_file=log_file)

class CrowdWorksScrapper(BaseScrapper):
    
    def __init__(self):
        super().__init__()
    
    @property
    def url_prefix(self):
        return PLATFORM_DOMAIN_CROWDWORKS

    def run(self, driver) -> List[ProjectInfo]:
        proc_name = "run"

        self.clear_seen_jobs()    
        all_projects: List[ProjectInfo] = []
        
        try:
            logger.info(f"[{proc_name}] CroudWorksスクレイピング開始")
            # 仕事受注トップページ
            driver.get(PLATFORM_URL_CROWDWORKS)
            
            categories = ["システム開発", "ホームページ制作"]
            
            for category in categories:
                logger.info(f"[{proc_name}] カテゴリ開始: {category}")
                
                # リロード
                driver.refresh()
                wait_browser_load(driver)
                random_delay(delay_range=(0.7, 1.5))
                
                
                # カテゴリーから絞り込む
                a_list = find_element(driver, By.XPATH, f"//ul[contains(@class, 'jCNpP')]/li/a", multiple=True)
                for a in a_list:
                    if category in a.text.strip():
                        logger.debug(f"[{proc_name}/{category}] カテゴリボタンクリック: {a.text.strip()}")
                        safe_click(driver, a)
                        break
                
                wait_browser_load(driver)
                random_delay()
                
                
                for checked_value in ['fixed_price', 'competition']:    
                    # 依頼形式
                    target_chb = find_element(driver, By.XPATH, f"//input[@value='{checked_value}']/ancestor::label[contains(@class, 'YWqwp')]")
                    safe_click(driver, target_chb)
                    logger.debug(f"[{proc_name}/{category}] 依頼形式クリック: {checked_value}")
                
                random_delay(delay_range=(1.0, 2.0))
                
                search_btn = find_element(driver, By.XPATH, "//button[contains(@class, 'ulqrU') and contains(text(), '絞り込む')]")
                safe_click(driver, search_btn)
                logger.debug(f"[{proc_name}/{category}] 絞り込みボタンをクリック")
                
                wait_browser_load(driver)
                random_delay()
                
                # 新着順に並び替え
                dropdown = find_element(driver, By.XPATH, "//div[contains(@class, 'MKl3X')]//select[contains(@class, 'WkB3D')]")
                select = Select(dropdown)
                select.select_by_index(1)
                logger.debug(f"[{proc_name}] 新着順に並び替え完了")
                
                current_page = 1
                max_page = 2
                
                while current_page <= max_page:
                    
                    logger.info(f"[{proc_name}/{category}]{current_page}ページ目開始")
                    
                    # 情報取得
                    results = self.scrape_projects_on_current_page(driver, category) 
                    all_projects.extend(results)
                    logger.info(f"[{proc_name}/{category}] {len(results)}件取得")
                    
                    try:
                        tmp = find_element(driver, By.XPATH, "//a[contains(@class, 'de7Z2') and contains(@class, 'oVhqD') and contains(@class, 'H3VWB')]")
                        next_link = tmp.get_attribute("href")
                        driver.get(next_link)
                        current_page +=1
                    except Exception as e:
                        logger.info(f"[{proc_name}/{category}] 次ページなし、ループ終了")
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
            logger.error(f"[{proc_name}] スクレイピング中にエラー発生", exc_info=True)
        
        finally:
            logger.info(f"[{proc_name}] CroudWorksスクレイピング終了")
            return all_projects
            
            
    def scrape_projects_on_current_page(self, driver: WebDriver, category: str) -> List[ProjectInfo]:
        proc_name = "scrape_projects_on_current_page"
        results = []
        main_handle = driver.current_window_handle
        
        try:
            items = find_element(driver, By.XPATH, "//ul[contains(@class, 'gH9lt') and contains(@class, 'OW4Y6') and contains(@class, 'QH0Pz')]/li", multiple=True)
            logger.info(f"[{proc_name}/{category}] 案件数: {len(items)}件")
            count = 1
        
            for item in items:
                    
                # PR案件を除外
                pr_li = find_element(item, By.XPATH, ".//li[contains(@class, 'VXZpw')]", timeout=0.2)
                if pr_li:
                    inner_buf = pr_li.text.strip()
                    # インナーテキストがPRの場合は次案件へ
                    if inner_buf == "PR":
                        logger.debug(f"[{proc_name}/{category}] PR案件のためスキップ")
                        continue
                
                if DEBUG_MODE and count > DEV_STOP_COUNT:
                    logger.debug(f"[{proc_name}/{category}] DEBUG_MODE制御により処理中断")
                    break
                
                link = find_element(item, By.XPATH, ".//a[contains(@class, 'wB71r')]")
                if link:
                    
                    href = link.get_attribute("href")
                    job_id = href.split("/")[-1]
                    
                    if self.is_duplicate(job_id):
                        logger.debug(f"[{proc_name}/{category}] 重複案件のためスキップ: {job_id}")
                        continue
                    
                    self.mark_as_seen(job_id)
                    
                    logger.debug(f"[{proc_name}/{category}] 案件{count}: リンククリック")
                    safe_click(driver, link)
                else:
                    logger.warning(f"[{proc_name}/{category}] 案件{count}: リンク取得失敗 -> スキップ")
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
                    logger.info(f"[{proc_name}/{category}] 案件名: {title}")
                    
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
                                logger.debug(f"[{proc_name}/{category}] 価格: {price}")
                            else:
                                logger.warning(f"[{proc_name}/{category}] {title}: 価格取得失敗")
                            
                        elif "応募期限" in th_text:
                            deadline_elm = find_element(row, By.XPATH, ".//td")
                            if deadline_elm:
                                deadline = deadline_elm.text.strip()
                                logger.debug(f"[{proc_name}/{category}] 応募期限: {deadline}")
                            else:
                                logger.warning(f"[{proc_name}/{category}] {title}: 応募期限取得失敗")
                            
                        elif "納品希望日" in th_text:
                            delivery_elm = find_element(row, By.XPATH, ".//td") 
                            if delivery_elm:
                                delivery = delivery_elm.text.strip()
                                
                                if delivery == "-":
                                    delivery = None
                                else:
                                    logger.debug(f"[{proc_name}/{category}] 納品希望日: {delivery}")
                            else:
                                logger.warning(f"[{proc_name}/{category}] {title}: 納品希望日取得失敗")
                    
                    description = None
                    
                    description_elm = find_element(driver, By.XPATH, "//table[contains(@class, 'job_offer_detail_table')]//td[contains(@class, 'confirm_outside_link')]")
                    if description_elm:
                        description = description_elm.text.strip()
                    else:
                        logger.warning(f"[{proc_name}/{category}] {title}: 詳細取得失敗")
                    
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
                    logger.error(f"[{proc_name}/{category}] 案件取得エラー", exc_info=True)
                
                finally:
                    driver.close()
                    driver.switch_to.window(main_handle)
                
                    wait_browser_load(driver)
                    random_delay(delay_range=(0.5, 1.0))

        except Exception as e:
            logger.error(f"[{proc_name}] ページ全体での取得エラー", exc_info=True)

        finally:
            if driver.current_window_handle != main_handle:
                driver.switch_to.window(main_handle)
                
                wait_browser_load(driver)
                random_delay(delay_range=(0.5, 1.0))
            
            return results