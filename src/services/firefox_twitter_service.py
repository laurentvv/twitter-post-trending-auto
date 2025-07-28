"""Service Firefox pour l'automatisation Twitter via Selenium."""
import time
import re
from typing import Optional, Dict, Any
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException,
    WebDriverException
)
from webdriver_manager.firefox import GeckoDriverManager
from ..core.firefox_config import firefox_config
from ..core.logger import logger, log_step

class FirefoxTwitterService:
    """Service d'automatisation Twitter via Firefox."""

    def __init__(self):
        self.config = firefox_config.get_config()
        self.driver: Optional[webdriver.Firefox] = None
        self._setup_driver()

    def _setup_driver(self) -> None:
        """Configure le driver Firefox."""
        if not self.config["enabled"]:
            logger.warning("Firefox service désactivé ou profil non trouvé", 
                          **log_step("firefox_disabled"))
            return

        try:
            logger.info("Configuration du driver Firefox", 
                       **log_step("firefox_setup", profile_path=self.config["profile_path"]))
            # Configuration des options Firefox
            options = Options()
            # Mode headless
            if self.config["headless"]:
                options.add_argument("--headless")
            # Profil utilisateur
            options.add_argument("-profile")
            options.add_argument(self.config["profile_path"])
            # Service avec GeckoDriver automatique
            service = Service(GeckoDriverManager().install())
            # Initialisation du driver
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_page_load_timeout(self.config["timeout"])
            logger.info("Driver Firefox initialisé avec succès", 
                       **log_step("firefox_ready"))
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation Firefox: {e}", 
                        **log_step("firefox_error", error=str(e)))
            self.driver = None

    def _wait_and_find_element(self, by: By, value: str, timeout: int = 10):
        """Attend et trouve un élément avec timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                element = self.driver.find_element(by, value)
                return element
            except NoSuchElementException:
                time.sleep(0.5)
        raise TimeoutException(f"Élément non trouvé: {value}")

    def _safe_click(self, element, description: str = ""):
        """Clic sécurisé avec retry."""
        for attempt in range(3):
            try:
                element.click()
                time.sleep(self.config["wait_between_actions"])
                return True
            except Exception as e:
                logger.warning(f"Tentative {attempt + 1} échouée pour {description}: {e}")
                time.sleep(1)
        return False

    def _safe_send_keys(self, element, text: str, description: str = ""):
        """Envoi de texte sécurisé avec retry."""
        for attempt in range(3):
            try:
                element.clear()
                element.send_keys(text)
                time.sleep(self.config["wait_between_actions"])
                return True
            except Exception as e:
                logger.warning(f"Tentative {attempt + 1} échouée pour {description}: {e}")
                time.sleep(1)
        return False

    def _get_latest_tweet_id(self) -> Optional[str]:
        """Récupère l'ID du dernier tweet publié via le profil public."""
        try:
            # Aller sur la page d'accueil pour s'assurer qu'on est connecté
            self.driver.get("https://x.com/home")
            time.sleep(3)

            # Cliquer sur le lien du profil
            profile_link = self._wait_and_find_element(By.XPATH, "//a[@data-testid='AppTabBar_Profile_Link']")
            profile_link.click()
            time.sleep(3)

            # Attendre le chargement du fil
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//article[@data-testid='tweet']"))
            )

            # Premier tweet = le plus récent
            first_tweet = self.driver.find_element(By.XPATH, "//article[@data-testid='tweet']")
            tweet_link = first_tweet.find_element(By.XPATH, ".//a[contains(@href, '/status/')]").get_attribute("href")

            match = re.search(r"/status/(\d+)", tweet_link)
            if match:
                tweet_id = match.group(1)
                logger.info(f"✅ ID récupéré via profil : {tweet_id}")
                return tweet_id
        except Exception as e:
            logger.warning(f"Impossible de récupérer l'ID via le profil : {e}")
        return None

    def post_tweet(self, text: str, reply_text: Optional[str] = None) -> Optional[str]:
        """
        Poste un tweet via Firefox automation.
        Args:
            text: Texte du tweet principal
            reply_text: Texte de la réponse (optionnel)
        Returns:
            Tweet ID si succès, None sinon
        """
        if not self.driver:
            logger.error("Driver Firefox non initialisé", 
                        **log_step("firefox_not_ready"))
            return None

        start_time = time.time()
        try:
            logger.info("Début du post Firefox", 
                       **log_step("firefox_post_start", text_length=len(text)))

            # Navigation vers Twitter
            self.driver.get("https://x.com")
            time.sleep(3)

            # Clic sur le bouton "Nouveau tweet"
            try:
                new_tweet_button = self._wait_and_find_element(
                    By.XPATH, "//a[@data-testid='SideNav_NewTweet_Button']"
                )
                if not self._safe_click(new_tweet_button, "bouton nouveau tweet"):
                    raise Exception("Impossible de cliquer sur le bouton nouveau tweet")
            except Exception as e:
                logger.warning(f"Bouton nouveau tweet non trouvé, tentative alternative: {e}")
                # Tentative alternative
                time.sleep(3)
                new_tweet_button = self._wait_and_find_element(
                    By.XPATH, "//a[@data-testid='SideNav_NewTweet_Button']"
                )
                if not self._safe_click(new_tweet_button, "bouton nouveau tweet (retry)"):
                    raise Exception("Échec du clic sur le bouton nouveau tweet")

            time.sleep(2)

            # Saisie du texte du tweet
            try:
                textbox = self._wait_and_find_element(By.XPATH, "//div[@role='textbox']")
                if not self._safe_send_keys(textbox, text, "saisie texte tweet"):
                    raise Exception("Impossible de saisir le texte du tweet")
            except Exception as e:
                logger.warning(f"Textbox non trouvée, tentative alternative: {e}")
                time.sleep(2)
                textbox = self._wait_and_find_element(By.XPATH, "//div[@role='textbox']")
                if not self._safe_send_keys(textbox, text, "saisie texte tweet (retry)"):
                    raise Exception("Échec de la saisie du texte du tweet")

            time.sleep(1)

            # Envoi du tweet
            textbox.send_keys(Keys.ENTER)
            tweet_button = self._wait_and_find_element(By.XPATH, "//button[@data-testid='tweetButton']")
            if not self._safe_click(tweet_button, "bouton tweet"):
                raise Exception("Impossible de cliquer sur le bouton tweet")

            logger.info("Tweet principal posté via Firefox", 
                       **log_step("firefox_post_success", duration=f"{time.time() - start_time:.2f}s"))

            # === 🔍 Tenter d'extraire l'ID depuis l'URL ===
            tweet_id = None
            current_url = self.driver.current_url
            if "/status/" in current_url:
                match = re.search(r"/status/(\d+)", current_url)
                if match:
                    tweet_id = match.group(1)
                    logger.info(f"✅ ID du tweet récupéré depuis l'URL : {tweet_id}")
            else:
                logger.warning("❌ Pas de /status/ dans l'URL, tentative via profil...")
                tweet_id = self._get_latest_tweet_id()

            # === Répondre si demandé ===
            if reply_text and tweet_id:
                self._post_reply_with_id(tweet_id, reply_text)
            elif reply_text:
                logger.warning("Impossible de répondre : aucun ID disponible")
                self._post_reply(reply_text)

            # === Retourner l'ID ou None ===
            return tweet_id

        except Exception as e:
            logger.error(f"Erreur lors du post Firefox: {e}", 
                        **log_step("firefox_post_error", error=str(e), duration=f"{time.time() - start_time:.2f}s"))
            return None

    def _post_reply(self, reply_text: str) -> Optional[str]:
        """Poste une réponse au tweet principal - VERSION CORRIGÉE."""
        try:
            logger.info("Post de la réponse via Firefox", 
                       **log_step("firefox_reply_start", reply_length=len(reply_text)))

            # Attendre que le tweet soit posté et que la page se charge
            time.sleep(5)

            # Méthode 1: Chercher le bouton réponse dans l'article du tweet
            reply_button = None
            try:
                # Utiliser CSS selector plus moderne et fiable
                reply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='reply']"))
                )
                logger.info("Bouton réponse trouvé avec data-testid='reply'")
            except TimeoutException:
                # Fallback vers XPath si CSS échoue
                try:
                    reply_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='reply']"))
                    )
                    logger.info("Bouton réponse trouvé avec XPath")
                except TimeoutException:
                    logger.warning("Bouton réponse non trouvé avec les sélecteurs standards")

            # Si toujours pas trouvé, essayer de cliquer directement sur l'icône de réponse
            if not reply_button:
                try:
                    # Chercher l'icône SVG de réponse
                    reply_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//svg[contains(@class, 'r-4qtqp9') or contains(@class, 'r-yyyyoo')]/../.."))
                    )
                    logger.info("Bouton réponse trouvé via icône SVG")
                except TimeoutException:
                    raise Exception("Aucun bouton de réponse trouvé avec toutes les méthodes")

            # Scroll vers le bouton et clic
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reply_button)
            time.sleep(1)

            if not self._safe_click(reply_button, "bouton réponse"):
                # Dernière tentative avec JavaScript
                self.driver.execute_script("arguments[0].click();", reply_button)
                time.sleep(2)

            # Attendre l'ouverture de la modal de réponse
            time.sleep(3)

            # Saisir le texte de la réponse
            try:
                # Chercher la nouvelle textbox de réponse
                reply_textbox = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='textbox' and @contenteditable='true']"))
                )
                # S'assurer que c'est bien la textbox de réponse (pas celle du tweet original)
                textboxes = self.driver.find_elements(By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
                if len(textboxes) > 1:
                    reply_textbox = textboxes[-1]  # Prendre la dernière (celle de la réponse)
            except TimeoutException:
                raise Exception("Textbox de réponse non trouvée")

            if not self._safe_send_keys(reply_textbox, reply_text, "saisie texte réponse"):
                raise Exception("Impossible de saisir le texte de la réponse")

            time.sleep(2)

            # Envoyer la réponse
            try:
                # Chercher le bouton "Répondre" (pas "Tweet")
                reply_send_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='tweetButton']"))
                )
                if not self._safe_click(reply_send_button, "bouton envoyer réponse"):
                    # Tentative avec JavaScript
                    self.driver.execute_script("arguments[0].click();", reply_send_button)
            except TimeoutException:
                # Fallback avec Ctrl+Enter
                logger.info("Bouton réponse non trouvé, utilisation de Ctrl+Enter")
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()

            time.sleep(3)
            logger.info("Réponse postée via Firefox", 
                       **log_step("firefox_reply_success"))
            return "firefox_reply_success"

        except Exception as e:
            logger.error(f"Erreur lors du post de la réponse Firefox: {e}", 
                        **log_step("firefox_reply_error", error=str(e)))
            return None

    def post_reply(self, tweet_id: str, reply_text: str) -> Optional[str]:
        """Poste une réponse à un tweet spécifique - VERSION CORRIGÉE."""
        try:
            logger.info("Post de réponse à un tweet spécifique via Firefox", 
                       **log_step("firefox_reply_to_tweet", tweet_id=tweet_id))

            # Si c'est un ID Firefox (pas un vrai ID Twitter), utiliser la méthode directe
            if tweet_id == "firefox_tweet_success":
                return self._post_reply(reply_text)

            # Sinon, naviguer vers le tweet spécifique
            tweet_url = f"https://x.com/i/status/{tweet_id}"
            self.driver.get(tweet_url)
            time.sleep(4)

            # Attendre que la page soit chargée
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-testid='tweet']"))
            )

            # Trouver le bouton de réponse
            reply_button = None
            try:
                reply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='reply']"))
                )
                logger.info("Bouton réponse trouvé avec data-testid='reply'")
            except TimeoutException:
                try:
                    reply_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='reply']"))
                    )
                    logger.info("Bouton réponse trouvé avec XPath")
                except TimeoutException:
                    raise Exception("Bouton de réponse non trouvé")

            # Scroll et clic sur le bouton de réponse
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reply_button)
            time.sleep(1)

            if not self._safe_click(reply_button, "bouton réponse"):
                self.driver.execute_script("arguments[0].click();", reply_button)
                time.sleep(2)

            # Attendre l'ouverture de la modal
            time.sleep(3)

            # Saisir le texte de la réponse
            try:
                reply_textbox = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='textbox' and @contenteditable='true']"))
                )
                # S'assurer que c'est la textbox de réponse
                textboxes = self.driver.find_elements(By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
                if len(textboxes) > 1:
                    reply_textbox = textboxes[-1]  # Dernière textbox = textbox de réponse
            except TimeoutException:
                raise Exception("Textbox de réponse non trouvée")

            if not self._safe_send_keys(reply_textbox, reply_text, "saisie texte réponse"):
                raise Exception("Impossible de saisir le texte de la réponse")

            time.sleep(2)

            # Envoyer la réponse
            try:
                reply_send_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='tweetButton']"))
                )
                if not self._safe_click(reply_send_button, "bouton envoyer réponse"):
                    self.driver.execute_script("arguments[0].click();", reply_send_button)
            except TimeoutException:
                # Fallback avec Ctrl+Enter
                logger.info("Utilisation de Ctrl+Enter pour envoyer la réponse")
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()

            time.sleep(3)
            logger.info("Réponse postée via Firefox", 
                       **log_step("firefox_reply_success"))
            return "firefox_reply_success"

        except Exception as e:
            logger.error(f"Erreur lors du post de la réponse Firefox: {e}", 
                        **log_step("firefox_reply_error", error=str(e)))
            return None

    def _post_reply_direct(self, reply_text: str) -> Optional[str]:
        """Poste une réponse directement après le tweet principal."""
        return self._post_reply(reply_text)

    def _post_reply_with_id(self, tweet_id: str, reply_text: str) -> Optional[str]:
        """Poste une réponse à un tweet spécifique en utilisant l'ID."""
        return self.post_reply(tweet_id, reply_text)

    def close(self):
        """Ferme le driver Firefox."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver Firefox fermé", **log_step("firefox_closed"))
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture Firefox: {e}")
            finally:
                self.driver = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
