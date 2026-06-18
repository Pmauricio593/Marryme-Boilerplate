import logging

from apify_client import ApifyClient as ApifySDK
from django.conf import settings

logger = logging.getLogger("marryme.integrations.apify")


class ApifyClient:
    # Actor IDs dos scrapers utilizados
    INSTAGRAM_SCRAPER = "apify/instagram-scraper"
    INSTAGRAM_PROFILE = "apify/instagram-profile-scraper"

    def __init__(self):
        self.client = ApifySDK(settings.APIFY_API_TOKEN)

    def buscar_perfis_instagram(self, usernames: list[str]) -> list[dict]:
        """
        Busca dados públicos de perfis do Instagram.
        Retorna seguidores, bio, posts recentes.
        """
        logger.info(f"Apify buscando {len(usernames)} perfis")
        try:
            run = self.client.actor(self.INSTAGRAM_PROFILE).call(run_input={"usernames": usernames})
            resultados = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                resultados.append(item)

            logger.info(f"Apify retornou {len(resultados)} perfis")
            return resultados
        except Exception as e:
            logger.error(f"Erro Apify perfis: {e}")
            raise

    def scraper_por_nicho(self, hashtags: list[str], limite: int = 50) -> list[dict]:
        """
        Busca posts por hashtag para prospecção por nicho.
        Ex: hashtags=['fotografodecasamento', 'bandadecasamento']
        """
        logger.info(f"Apify scraping hashtags: {hashtags}")
        try:
            run = self.client.actor(self.INSTAGRAM_SCRAPER).call(
                run_input={
                    "directUrls": [
                        f"https://www.instagram.com/explore/tags/{tag}/" for tag in hashtags
                    ],
                    "resultsLimit": limite,
                }
            )
            resultados = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                resultados.append(item)

            logger.info(f"Apify retornou {len(resultados)} posts")
            return resultados
        except Exception as e:
            logger.error(f"Erro Apify scraping: {e}")
            raise
