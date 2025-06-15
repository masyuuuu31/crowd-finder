from ...base.base_scrapper import BaseScrapper
from ....constants.const import PLATFORM_DOMAIN_LANCERS, PLATFORM_URL_LANCERS, PLATFORM_NM_LANCERS, DEBUG_MODE, DEV_STOP_COUNT
from ....schema.schemas import ProjectInfo

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from ...infra.intraction_manager import random_delay, find_element, wait_browser_load, safe_click

from typing import List

from ....utils.logger import setup_logger
from ....config import BASE_DIR
import os

log_file = os.path.join(BASE_DIR, "logs", "server.log")

# 共通ロガーをセットアップ
logger = setup_logger(__name__, log_file=log_file)

class LancersScrapper(BaseScrapper):
    
    def __init__(self):
        super().__init__()

    @property
    def url_prefix(self):
        return PLATFORM_DOMAIN_LANCERS

    def run(self, driver) -> List[ProjectInfo]:
        proc_name = "run"
          
        all_projects: List[ProjectInfo] = []
        
        try:
            logger.info(f"[{proc_name}] Lancersスクレイピング開始")
            
            # 仕事受注トップページ
            driver.get(PLATFORM_URL_LANCERS)
            
            # 「仕事を探す」を押下
            btn = find_element(driver, By.XPATH, "//span[@class='css-16a2wt1']")
            safe_click(driver, btn)
            logger.debug(f"[{proc_name}] 『仕事を探す』ボタン押下")
            
            first_search = True
            
            categories = ["システム開発", "Web制作"]
            
            for category in categories:
                logger.info(f"[{proc_name}] カテゴリ開始: {category}")
                
                # カテゴリーから絞り込む
                category_anchor = find_element(driver, By.XPATH,f"//dl[contains(@class, 'p-search-sidenav__list') and contains(@class, 'js-sp-category-toggle-target')]//a[contains(normalize-space(text()), '{category}')]")
                safe_click(driver, safe_click)
                logger.debug(f"[{proc_name}] カテゴリ選択クリック: {category}")

                random_delay(delay_range=(0.5, 1.0))

                # 初回検索時のみ絞り込みを行う
                if first_search:
                    logger.info(f"[{proc_name}/{category}] 初回絞り込み開始")
                    # 仕事スタイルで絞り込む（プロジェクト、コンペ）
                    for checkbox_id in ['type-competition', 'type-project']:
                        target_chb = find_element(driver, By.ID, checkbox_id)
                        safe_click(driver, target_chb)
                        logger.debug(f"[{proc_name}/{category}] チェックボックスON: {checkbox_id}")
                        
                    # 絞り込む
                    search_btn = find_element(driver, By.XPATH, "//div[contains(@class, 'p-search-sidenav__refine')]//input[@id='Search']")
                    safe_click(driver, search_btn)
                    logger.debug(f"[{proc_name}/{category}] 絞り込みボタンクリック")
                    random_delay(delay_range=(0.5, 1.0))
                    
                    first_search = False

                current_page = 1
                max_page = 2
                
                while current_page <= max_page:
                    logger.info(f"[{proc_name}/{category}] {current_page}ページ目開始")
                    
                    results = self.scrape_projects_on_current_page(driver, category)
                    all_projects.extend(results)
                    logger.info(f"[{proc_name}/{category}] {len(results)}件取得")

                    try:
                        next_link = find_element(driver, By.XPATH, "//span[contains(@class, 'c-pager__item--next') and contains(@class, 'c-pager__item')]/a")
                        driver.get(next_link.get_attribute("href"))
                        current_page += 1
                    except Exception as e:
                        logger.info(f"[{proc_name}/{category}] 次ページなし、ループ終了")
                        break

                # 全てのカテゴリーに戻る
                all_category =find_element(driver, By.XPATH, "//a[contains(@class, 'c-link') and contains(normalize-space(text()), 'すべてのカテゴリー')]")
                safe_click(driver, all_category)
                random_delay(delay_range=(1.0, 2.0))
        
        except Exception as e:
            print(f"エラー発生: {e}")
        
        finally:
            return all_projects

    def scrape_projects_on_current_page(self, driver: WebDriver, category: str) -> List[ProjectInfo]:
        proc_name = "scrape_projects_on_current_page"
        results: List[ProjectInfo] = []
        
        div_xpath = "//div[contains(@class,'p-search-job-media') and contains(@class, 'c-media--item')]"
        divs = find_element(driver, By.XPATH, div_xpath, multiple=True)
        
        logger.info(f"[{proc_name}/{category}] 案件数: {len(divs)}件")
        count = 0
        
        for div in divs:
            
            count+=1
            
            if DEBUG_MODE and count > DEV_STOP_COUNT:
                logger.debug(f"[{proc_name}/{category}] DEBUG_MODEにより中断")
                break
            
            logger.debug(f"[{proc_name}/{category}] 案件{count}: リンククリック")
            safe_click(driver, div)
            random_delay(delay_range=(0.5, 1.0))

            try:
                # タイトル取得
                title_elm = find_element(driver, By.TAG_NAME, "h1")
                
                if not title_elm:
                    raise RuntimeError("タイトル取得失敗")
                
                if "閲覧制限" in title_elm.text.strip():
                    raise RuntimeError("閲覧制限")
                
                title = title_elm.text.strip()
                logger.info(f"[{proc_name}/{category}] 案件名: {title}")

                # 価格の数値部分と単位部分をそれぞれ取得
                price_numbers = find_element(driver, By.XPATH, "//span[contains(@class, 'price-block')]//span[contains(@class, 'price-number')]", multiple=True)
                price_units = find_element(driver, By.XPATH, "//span[contains(@class, 'price-block')]//span[contains(@class, 'price-unit')]", multiple=True)
                price = None
                if price_numbers and price_units:
                    price = " 〜 ".join([
                        f"{num.text.strip()}{unit.text.strip()}"
                        for num, unit in zip(price_numbers, price_units)
                    ])
                    logger.debug(f"[{proc_name}/{category}] 価格: {price}")
                else:
                    logger.warning(f"[{proc_name}/{category}] 価格取得失敗")

                # 応募締切
                deadline_elm = find_element(driver, By.XPATH, "//span[contains(text(), '締切')]/following-sibling::span[1]")
                deadline = None
                if deadline_elm:
                    deadline = deadline_elm.text.strip()
                    logger.debug(f"[{proc_name}/{category}] 締切: {deadline}")
                else:
                    logger.warning(f"[{proc_name}/{category}] 締切取得失敗")
                
                # 希望納期
                delivery_elm = find_element(driver, By.XPATH, "//span[contains(text(), '希望納期')]/following-sibling::span[1]")
                delivery = None
                if delivery_elm:
                    delivery = delivery_elm.text.strip()
                    logger.debug(f"[{proc_name}/{category}] 納期: {delivery}")
                else:
                    logger.warning(f"[{proc_name}/{category}] 納期取得失敗")

                # 詳細
                description_elm = find_element(driver, By.XPATH, "//dd[contains(@class, 'p-work-detail-lancer__postscript-description')]")
                description = None
                if description_elm:
                    description = description_elm.text.strip()
                else:
                    logger.warning(f"[{proc_name}/{category}] 詳細取得失敗")
                
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
                logger.error(f"[{proc_name}/{category}] 案件詳細取得エラー: {e}", exc_info=True)
            
            driver.back()
            wait_browser_load(driver)
            random_delay(delay_range=(0.5, 1.0))
            
        return results