import secrets
import requests
import sys
import getopt
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
from colorama import Fore, Style, init

# Inizializza colorama
init(autoreset=True)

# Configura il logging
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Funzione per scaricare la lista di parole
def fetch_word_list(url):
    response = requests.get(url)
    words = response.text.splitlines()
    return words

# Funzione per generare la passphrase
def generate_passphrase(word_list, num_words=4):
    passphrase = [secrets.choice(word_list) for _ in range(num_words)]
    passphrase = ''.join(word.capitalize() for word in passphrase)
    # Aggiungi un numero casuale tra 0 e 99 e un carattere speciale alla fine
    special_chars = "!@#$%^&*()"
    passphrase += str(random.randint(0, 99)) + random.choice(special_chars)
    return passphrase

# Funzione per controllare la forza della password utilizzando Selenium
def check_password_strength(passphrase):
    # Configura Selenium WebDriver per modalità headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Vai al sito di PasswordMeter
        driver.get('https://passwordmeter.com/')
        
        # Chiudi il popup dei cookie
        cookie_button = driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[1]/div[2]/div[2]/button[2]')
        cookie_button.click()
        time.sleep(1)  # Aggiungi un breve ritardo per assicurarti che il popup sia chiuso

        # Trova il campo di input della password e scorrere fino ad esso
        input_field = driver.find_element(By.XPATH, '/html/body/div[2]/form/table[1]/tbody/tr[2]/td[1]/input[1]')
        driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
        time.sleep(1)  # Aggiungi un breve ritardo per assicurarti che lo scrolling sia completato
        
        # Inserisci la passphrase simulando la digitazione
        actions = ActionChains(driver)
        actions.move_to_element(input_field)
        actions.click(input_field)
        actions.send_keys(passphrase)
        actions.perform()
        
        # Attendi 10 secondi
        time.sleep(1)
        
        # Trova l'elemento che contiene la forza della password
        score_element = driver.find_element(By.XPATH, '/html/body/div[2]/form/table[1]/tbody/tr[4]/td/div/div[1]')
        score = score_element.text
        
        print(Fore.GREEN + f"Password Strength Score: {score}")
        logging.info(f"Password Strength Score: {score}")
        return score
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()

# Funzione principale
def main(language='english', passphrase=None, num_words=4):
    word_list_urls = {
        'english': 'https://www.mit.edu/~ecprice/wordlist.10000',
        'italian': 'https://raw.githubusercontent.com/napolux/paroleitaliane/master/paroleitaliane/660000_parole_italiane.txt'
    }

    if language not in word_list_urls:
        raise ValueError(Fore.RED + f"Unsupported language: {language}")
    
    if passphrase is None:
        word_list_url = word_list_urls[language]
        word_list = fetch_word_list(word_list_url)
        passphrase = generate_passphrase(word_list, num_words)
        print(Fore.CYAN + f"Generated {language.capitalize()} Passphrase: {passphrase}")
    else:
        print(Fore.CYAN + f"Using provided passphrase: {passphrase}")

    # Verifica la forza della password
    score = check_password_strength(passphrase)
    return passphrase, score

if __name__ == "__main__":
    language = 'english'
    passphrase = None

    # Analisi degli argomenti da riga di comando
    try:
        opts, args = getopt.getopt(sys.argv[1:], "itenp:", ["language=", "passphrase="])
    except getopt.GetoptError as err:
        print(Fore.RED + str(err))
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-it"):
            language = 'italian'
        elif opt in ("-eng"):
            language = 'english'
        elif opt in ("-p", "--passphrase"):
            passphrase = arg
    
    print(Fore.YELLOW + f"Language selected: {language}")
    passphrase, score = main(language=language, passphrase=passphrase)
    print(Fore.MAGENTA + f"Passphrase: {passphrase}\nPassword Strength Score: {score}")
