import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import os
from config.settings import SCREENSHOT_DIR

class ScreenshotCapturer:
    def __init__(self):
        # Créer le dossier si nécessaire
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    def capture_repository(self, url: str, output_filename: str) -> str:
        """
        Capture une capture d'écran du dépôt GitHub
        Retourne le chemin du fichier
        """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1200,800")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=options)

        try:
            driver.get(url)
            time.sleep(3)  # Attendre le chargement

            # Scroll pour capturer le contenu
            driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(1)

            # Sauvegarder
            filepath = f"{SCREENSHOT_DIR}{output_filename}"
            driver.save_screenshot(filepath)

            # Optimiser pour Twitter
            self._optimize_for_twitter(filepath)

            return filepath

        finally:
            driver.quit()

    def _optimize_for_twitter(self, filepath: str):
        """Optimise l'image pour Twitter"""
        try:
            img = Image.open(filepath)
            # Recadrer pour un format plus carré
            width, height = img.size
            left = 0
            top = 0
            right = min(width, 1000)
            bottom = min(height, 600)
            cropped = img.crop((left, top, right, bottom))
            cropped.save(filepath)
        except Exception as e:
            print(f"Erreur optimisation image: {e}")
