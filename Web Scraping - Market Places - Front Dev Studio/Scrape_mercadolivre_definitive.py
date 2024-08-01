from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style

init(autoreset=True)

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--block-new-web-contents")



# Função principal
def scrape_mercadolivre(cep, produto, num_paginas):
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.mercadolivre.com.br/navigation/addresses-hub?go=https%3A%2F%2Fwww.mercadolivre.com.br%2F"
    driver.get(url)
    try:
        sleep(3)
        inserir_cep = driver.find_element(By.NAME, "zipcode")
        sleep(2)
        inserir_cep.send_keys(cep)
        sleep(2)
        botao_confirmar = driver.find_element(By.XPATH, '//button[@class="andes-button zip-code__use-button andes-button--medium andes-button--loud"]')
        botao_confirmar.click()
        print("Cep inserido.")
        sleep(10)
        campo_busca = driver.find_element(By.XPATH, '//input[@class="nav-search-input"]')  
        campo_busca.send_keys(produto)    
        sleep(2)
        botao_pesquisa = driver.find_element(By.XPATH, '//button[@class="nav-search-btn"]')
        botao_pesquisa.click()
        sleep(4)
    except:
        print("Não foi possível inserir o frete.")
        driver.get(f'https://lista.mercadolivre.com.br/{produto}') 
    dic_produtos = {'Modelo': [], 'Preço': [], 'Link': [], 'Marketplace': [],'Vendedor':[], 'Termo Pesquisado': [], 'Dia da Busca': [], 'Hora da Busca': [], 'Frete': [], 'Ordem': [], 'Patrocinado': [], 'Avaliação': [], 'Num Avaliações': []}
    n = 1

    # Obtém a quantidade de resultados
    qtd_itens = driver.find_element(By.XPATH, '//span[contains(@class, "ui-search-search-result__quantity-results")]').text.strip()
    print(f'{Fore.GREEN}{qtd_itens} encontrados')

    for pagina in range(num_paginas):
        print(f"{Fore.LIGHTYELLOW_EX}Raspando página {pagina + 1} de {num_paginas}...")

        produtos = driver.find_elements(By.XPATH, '//div[@class="ui-search-result__wrapper"]')

        for produto in produtos:
            # Encontra os produtos, preços e links.
            marca = produto.find_element(By.XPATH, './/h2[contains(@class, "item__title")]').text.strip()
            preco = produto.find_element(By.XPATH, './/span[contains(@class, "ui-search-price__")]').text.strip()
            link = produto.find_element(By.XPATH, './/a[contains(@class, "search-link")]').get_attribute('href')
            link_completo = urljoin(url, link)
            
            # Faz uma validação dos dados(N.avaliaçõs, frete, valor do frete, patrocínio...). 
            # Se encontrados, são adicionados ao dicionário!
            try:
                avaliacoes = produto.find_element(By.XPATH, './/span[contains(@class, "rating-number")]').text.strip()
            except:
                avaliacoes = 'Não possui avaliações'


            try:
                num_avaliacoes = produto.find_element(By.XPATH, './/span[contains(@class, "reviews__amount")]').text.strip()
            except:
                num_avaliacoes = 'Não possui num.avaliações' 

                
            try:
                patrocinado = produto.find_element(By.XPATH, './/label[@class="ui-search-styled-label ui-search-item__pub-label"]').text.strip()  
            except:
                patrocinado = 'Não'


            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link_completo)
            sleep(5)
            try:    
                frete = driver.find_element(By.XPATH, '//div[@class="ui-pdp-media ui-pdp-generic-summary ui-pdp-generic-summary--md ui-vpp-shipping_summary ui-pdp-color--BLACK ui-pdp-generic-summary--black-price"]').text.strip()
            
            except:
                frete = 'Não foi possível identificar o frete'

            try: 
                vendedor = driver.find_element(By.XPATH, '//button[@class="ui-pdp-seller__link-trigger-button non-selectable"]').text.strip()
            
            except:
                vendedor = 'Vendedor não encontrado!'

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
                
            print(f"{n}. {marca} // {preco} // {link_completo} // {avaliacoes} // {num_avaliacoes} // {frete} // {vendedor}")

            # Dicionário com as informações que serão adiconadas à tabela.
            dic_produtos['Modelo'].append(marca)
            dic_produtos['Preço'].append(preco)
            dic_produtos['Link'].append(link_completo)
            dic_produtos['Avaliação'].append(avaliacoes)  
            dic_produtos['Num Avaliações'].append(num_avaliacoes) 
            dic_produtos['Vendedor'].append(vendedor)
            dic_produtos['Frete'].append(frete) 
            dic_produtos['Marketplace'].append('Mercado Livre')
            dic_produtos['Termo Pesquisado'].append(escolha_do_usuario)
            dic_produtos['Dia da Busca'].append(datetime.now().strftime("%d-%m-%Y"))
            dic_produtos['Hora da Busca'].append(datetime.now().strftime("%H:%M:%S"))
            dic_produtos['Ordem'].append(n)
            dic_produtos['Patrocinado'].append(patrocinado) 
            
            n += 1
        # Navega para a próxima página se não for a última
        if pagina < num_paginas - 1:
            try:
                if pagina == 0:
                    cookie_banner = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@class="cookie-consent-banner-opt-out__action cookie-consent-banner-opt-out__action--primary cookie-consent-banner-opt-out__action--key-accept"]')))
                    cookie_banner.click()
                    print("Cookie banner closed.")
                proxima_pagina = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//li[@class="andes-pagination__button andes-pagination__button--next"]/a')))
                sleep(3)
                proxima_pagina.click()
                sleep(5)
                
            except:
                print("Não foi possível encontrar o botão 'Seguinte'.")
                break

    # Cria DataFrame e salva em CSV e em excel
    tabela = pd.DataFrame(dic_produtos)
    print(tabela)
    tabela.to_csv('Resultados_da_pesquisa_selenium_Mercado_Livre.csv', index=False)
    tabela.to_excel('Resultados_da_pesquisa__Mercado_Livre.xlsx', index=False)
    
    # Fecha o WebDriver
    driver.quit()

# Entrada do usuário
cep = int(input('Qual é o seu cep? '))
escolha_do_usuario = input('Qual produto deseja buscar no Mercado Livre? ')
num_paginas = int(input('Quantas páginas deseja percorrer? '))
scrape_mercadolivre(cep,escolha_do_usuario, num_paginas)

