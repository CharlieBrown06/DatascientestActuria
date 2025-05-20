import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Configurer les options pour Chromium
chrome_options = Options()
chrome_options.binary_location = "/snap/bin/chromium"  # Chemin de Chromium Snap
chrome_options.add_argument("--headless")  # Mode sans interface graphique
chrome_options.add_argument("--no-sandbox")  # Requis pour Snap
chrome_options.add_argument("--disable-dev-shm-usage")  # Évite les problèmes de mémoire partagée
chrome_options.add_argument("--disable-gpu")  # Désactive l'accélération GPU
chrome_options.add_argument("--remote-debugging-port=9222")  # Port pour DevTools
chrome_options.add_argument("--disable-extensions")  # Désactive les extensions
chrome_options.add_argument("--disable-setuid-sandbox")  # Désactive le sandbox setuid

# Spécifier le chemin de ChromeDriver
service = Service("/usr/local/bin/chromedriver")

# Initialiser le driver
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)

# URL de la page principale
url = "https://www.institutdesactuaires.com/se-documenter/memoires/memoires-d-actuariat-4651"

# Liste pour stocker les données
data = []

try:
    # Accéder à la page principale
    driver.get(url)
    print("Page principale chargée.")

    # Attendre que les liens des titres soient présents
    title_links = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.view-content a"))
    )

    # Stocker les URLs des mémoires pour éviter les problèmes de "stale element"
    title_urls = [link.get_attribute("href") for link in title_links]

    # Parcourir chaque URL de mémoire
    for index, title_url in enumerate(title_urls, 1):
        print(f"Traitement du mémoire {index}/{len(title_urls)} : {title_url}")

        # Accéder à la page du mémoire
        driver.get(title_url)
        time.sleep(1)  # Pause pour assurer le chargement

        # Extraire les informations
        try:
            # Titre
            title = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.page-title"))
            ).text.strip()

            # Auteur(s)
            try:
                author = driver.find_element(By.CSS_SELECTOR, "div.field-name-field-auteur div.field-item").text.strip()
            except NoSuchElementException:
                author = "Non spécifié"

            # Société
            try:
                company = driver.find_element(By.CSS_SELECTOR, "div.field-name-field-societe div.field-item").text.strip()
            except NoSuchElementException:
                company = "Non spécifiée"

            # Année
            try:
                year = driver.find_element(By.CSS_SELECTOR, "div.field-name-field-annee div.field-item").text.strip()
            except NoSuchElementException:
                year = "Non spécifiée"

            # Résumé
            try:
                summary = driver.find_element(By.CSS_SELECTOR, "div.field-name-field-resume div.field-item").text.strip()
            except NoSuchElementException:
                summary = "Non spécifié"

            # URL de la pièce jointe
            try:
                attachment = driver.find_element(By.CSS_SELECTOR, "div.field-name-field-file a").get_attribute("href")
            except NoSuchElementException:
                attachment = "Aucune pièce jointe"

            # Ajouter les données à la liste
            data.append({
                "Titre": title,
                "Auteur(s)": author,
                "Société": company,
                "Année": year,
                "Résumé": summary,
                "URL Pièce Jointe": attachment
            })

            print(f"Données extraites pour : {title}")

        except TimeoutException as e:
            print(f"Erreur de chargement pour {title_url} : {e}")
            continue

except Exception as e:
    print(f"Erreur lors du traitement de la page principale : {e}")

finally:
    # Fermer le navigateur
    driver.quit()

# Créer un DataFrame pandas
df = pd.DataFrame(data)

# Exporter en CSV
output_file = "memoires_actuariat.csv"
df.to_csv(output_file, index=False, encoding="utf-8")
print(f"Données exportées dans {output_file}")

# Afficher un aperçu du tableau
print("\nAperçu des données :")
print(df)
