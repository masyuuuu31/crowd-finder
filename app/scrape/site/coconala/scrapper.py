from ...base.base_scrapper import BaseScrapper
from ....constants.const import PLATFORM_DOMAIN_COCONALA

class CoconaraScrapper(BaseScrapper):

    @property
    def url_prefix(self):
        return PLATFORM_DOMAIN_COCONALA
    
    def run(self, driver):
        print("CoconaradScrapper 実行開始")
        pass