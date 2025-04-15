from .site.lancers.scrapper import LancersScrapper
from .site.coconala.scrapper import CoconaraScrapper
from .site.crowdworks.scrapper import CrowdWorksScrapper
from ..constants.const import PLATFORM_NM_LANCERS, PLATFORM_NM_CROWDWORKS, PLATFORM_NM_COCONALA

def get_scrapper(site_name):
    return {
        PLATFORM_NM_LANCERS: LancersScrapper(),
        PLATFORM_NM_CROWDWORKS: CrowdWorksScrapper(),
        PLATFORM_NM_COCONALA: CoconaraScrapper()
    }.get(site_name)
