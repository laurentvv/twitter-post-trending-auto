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
            self.driver.get("https://twitter.com")
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
            
            # Récupérer l'URL du tweet posté pour obtenir l'ID
            time.sleep(3)
            current_url = self.driver.current_url
            tweet_id = None
            
            # Extraire l'ID du tweet depuis l'URL
            if "/status/" in current_url:
                tweet_id = current_url.split("/status/")[1].split("?")[0].split("/")[0]
                logger.info(f"ID du tweet récupéré: {tweet_id}")
            
            # Gestion de la réponse si fournie
            reply_id = None
            if reply_text and tweet_id:
                reply_id = self._post_reply_with_id(tweet_id, reply_text)
            elif reply_text:
                reply_id = self._post_reply(reply_text)
            
            return tweet_id or "firefox_tweet_success"  # Retourner l'ID réel si disponible
            
        except Exception as e:
            logger.error(f"Erreur lors du post Firefox: {e}", 
                        **log_step("firefox_post_error", error=str(e), duration=f"{time.time() - start_time:.2f}s"))
            return None
    
    def _post_reply(self, reply_text: str) -> Optional[str]:
        """Poste une réponse au tweet principal."""
        try:
            logger.info("Post de la réponse via Firefox", 
                       **log_step("firefox_reply_start", reply_length=len(reply_text)))
            
            # Attendre que le tweet soit posté
            time.sleep(4)
            
            # Trouver le bouton de réponse sur le tweet posté avec plusieurs sélecteurs
            reply_button = None
            selectors = [
                "//div[@data-testid='reply']",
                "//div[contains(@class, 'css-175oi2r') and contains(@class, 'r-xoduu5')]",
                "//button[contains(@class, 'css-175oi2r')]//div[contains(@class, 'r-xoduu5')]",
                "//*[contains(@id, 'reply')]//div[contains(@class, 'r-xoduu5')]"
            ]
            
            for selector in selectors:
                try:
                    reply_button = self._wait_and_find_element(By.XPATH, selector)
                    if reply_button:
                        logger.info(f"Bouton réponse trouvé avec le sélecteur: {selector}")
                        break
                except:
                    continue
            
            if not reply_button:
                raise Exception("Aucun bouton de réponse trouvé avec les sélecteurs disponibles")
            
            if not self._safe_click(reply_button, "bouton réponse"):
                raise Exception("Impossible de cliquer sur le bouton réponse")
            
            time.sleep(2)
            
            # Saisir le texte de la réponse
            reply_textbox = self._wait_and_find_element(By.XPATH, "//div[@role='textbox']")
            if not self._safe_send_keys(reply_textbox, reply_text, "saisie texte réponse"):
                raise Exception("Impossible de saisir le texte de la réponse")
            
            time.sleep(1)
            
            # Envoyer la réponse
            reply_textbox.send_keys(Keys.ENTER)
            reply_tweet_button = self._wait_and_find_element(By.XPATH, "//button[@data-testid='tweetButton']")
            if not self._safe_click(reply_tweet_button, "bouton tweet réponse"):
                raise Exception("Impossible de cliquer sur le bouton tweet réponse")
            
            logger.info("Réponse postée via Firefox", 
                       **log_step("firefox_reply_success"))
            
            return "firefox_reply_success"
            
        except Exception as e:
            logger.error(f"Erreur lors du post de la réponse Firefox: {e}", 
                        **log_step("firefox_reply_error", error=str(e)))
            return None
    
    def post_reply(self, tweet_id: str, reply_text: str) -> Optional[str]:
        """Poste une réponse à un tweet spécifique."""
        try:
            logger.info("Post de réponse à un tweet spécifique via Firefox", 
                       **log_step("firefox_reply_to_tweet", tweet_id=tweet_id))
            
            # Si c'est un ID Firefox (pas un vrai ID Twitter), utiliser la méthode directe
            if tweet_id == "firefox_tweet_success":
                return self._post_reply_direct(reply_text)
            
            # Sinon, naviguer vers le tweet spécifique
            tweet_url = f"https://twitter.com/i/status/{tweet_id}"
            self.driver.get(tweet_url)
            time.sleep(3)
            
            # Trouver le bouton de réponse avec plusieurs sélecteurs
            reply_button = None
            selectors = [
                "//div[@data-testid='reply']",
                "//div[contains(@class, 'css-175oi2r') and contains(@class, 'r-xoduu5')]",
                "//button[contains(@class, 'css-175oi2r')]//div[contains(@class, 'r-xoduu5')]",
                "//*[contains(@id, 'reply')]//div[contains(@class, 'r-xoduu5')]"
            ]
            
            for selector in selectors:
                try:
                    reply_button = self._wait_and_find_element(By.XPATH, selector)
                    if reply_button:
                        logger.info(f"Bouton réponse trouvé avec le sélecteur: {selector}")
                        break
                except:
                    continue
            
            if not reply_button:
                raise Exception("Aucun bouton de réponse trouvé avec les sélecteurs disponibles")
            
            if not self._safe_click(reply_button, "bouton réponse"):
                raise Exception("Impossible de cliquer sur le bouton réponse")
            
            time.sleep(2)
            
            # Saisir le texte de la réponse
            reply_textbox = self._wait_and_find_element(By.XPATH, "//div[@role='textbox']")
            if not self._safe_send_keys(reply_textbox, reply_text, "saisie texte réponse"):
                raise Exception("Impossible de saisir le texte de la réponse")
            
            time.sleep(1)
            
            # Envoyer la réponse
            reply_textbox.send_keys(Keys.ENTER)
            reply_tweet_button = self._wait_and_find_element(By.XPATH, "//button[@data-testid='tweetButton']")
            if not self._safe_click(reply_tweet_button, "bouton tweet réponse"):
                raise Exception("Impossible de cliquer sur le bouton tweet réponse")
            
            logger.info("Réponse postée via Firefox", 
                       **log_step("firefox_reply_success"))
            
            return "firefox_reply_success"
            
        except Exception as e:
            logger.error(f"Erreur lors du post de la réponse Firefox: {e}", 
                        **log_step("firefox_reply_error", error=str(e)))
            return None
    
    def _post_reply_direct(self, reply_text: str) -> Optional[str]:
        """Poste une réponse directement après le tweet principal."""
        try:
            logger.info("Post de la réponse directe via Firefox", 
                       **log_step("firefox_reply_direct_start", reply_length=len(reply_text)))
            
            # Attendre que le tweet soit posté
            time.sleep(4)
            
            # Naviguer vers la page de composition de tweet avec l'URL de réponse
            # L'URL de réponse Twitter utilise le format: https://twitter.com/compose/tweet?reply_to_id=...
            compose_url = "https://twitter.com/compose/tweet"
            self.driver.get(compose_url)
            time.sleep(3)
            
            logger.info("Navigation vers la page de composition de tweet")
            
            # Saisir le texte de la réponse
            reply_textbox = self._wait_and_find_element(By.XPATH, "//div[@role='textbox']")
            if not self._safe_send_keys(reply_textbox, reply_text, "saisie texte réponse"):
                raise Exception("Impossible de saisir le texte de la réponse")
            
            time.sleep(1)
            
            # Envoyer la réponse avec Ctrl+Enter (raccourci pour poster)
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
            logger.info("Raccourci Ctrl+Enter utilisé pour poster")
            
            time.sleep(2)
            
            logger.info("Réponse postée via Firefox", 
                       **log_step("firefox_reply_success"))
            
            return "firefox_reply_success"
            
        except Exception as e:
            logger.error(f"Erreur lors du post de la réponse Firefox: {e}", 
                        **log_step("firefox_reply_error", error=str(e)))
            return None
    
    def _post_reply_with_id(self, tweet_id: str, reply_text: str) -> Optional[str]:
        """Poste une réponse à un tweet spécifique en utilisant l'ID."""
        try:
            logger.info("Post de la réponse avec ID via Firefox", 
                       **log_step("firefox_reply_with_id_start", tweet_id=tweet_id, reply_length=len(reply_text)))
            
            # Naviguer directement vers le tweet
            tweet_url = f"https://twitter.com/i/status/{tweet_id}"
            self.driver.get(tweet_url)
            time.sleep(3)
            
            logger.info(f"Navigation vers le tweet: {tweet_url}")
            
            # Trouver et cliquer sur le bouton de réponse avec plusieurs sélecteurs
            reply_button = None
            selectors = [
                "//div[@data-testid='reply']",
                "//div[contains(@class, 'css-175oi2r') and contains(@class, 'r-xoduu5')]",
                "//button[contains(@class, 'css-175oi2r')]//div[contains(@class, 'r-xoduu5')]",
                "//*[contains(@id, 'reply')]//div[contains(@class, 'r-xoduu5')]",
                "//*[@id='id__1z7seo87ph8']//div[contains(@class, 'r-xoduu5')]",
                "//*[contains(@id, 'id__')]//div[contains(@class, 'r-xoduu5')]"
            ]
            
            for selector in selectors:
                try:
                    reply_button = self._wait_and_find_element(By.XPATH, selector)
                    if reply_button:
                        logger.info(f"Bouton réponse trouvé avec le sélecteur: {selector}")
                        break
                except:
                    continue
            
            if not reply_button:
                raise Exception("Aucun bouton de réponse trouvé avec les sélecteurs disponibles")
            
            if not self._safe_click(reply_button, "bouton réponse"):
                raise Exception("Impossible de cliquer sur le bouton réponse")
            
            time.sleep(2)
            
            # Saisir le texte de la réponse
            reply_textbox = self._wait_and_find_element(By.XPATH, "//div[@role='textbox']")
            if not self._safe_send_keys(reply_textbox, reply_text, "saisie texte réponse"):
                raise Exception("Impossible de saisir le texte de la réponse")
            
            time.sleep(1)
            
            # Envoyer la réponse avec Ctrl+Enter (raccourci pour poster)
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
            logger.info("Raccourci Ctrl+Enter utilisé pour poster la réponse")
            
            time.sleep(2)
            
            logger.info("Réponse postée via Firefox avec ID", 
                       **log_step("firefox_reply_with_id_success"))
            
            return "firefox_reply_success"
            
        except Exception as e:
            logger.error(f"Erreur lors du post de la réponse Firefox avec ID: {e}", 
                        **log_step("firefox_reply_with_id_error", error=str(e)))
            return None
    
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