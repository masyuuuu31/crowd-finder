from ...base.base_scrapper import BaseScrapper
from ....constants.const import PLATFORM_DOMAIN_CROWDWORKS

class CrowdWorksScrapper(BaseScrapper):

    @property
    def url_prefix(self):
        return PLATFORM_DOMAIN_CROWDWORKS

    def run(self, driver):
        pass
        