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
chrome_options.add_argument("--block-new-web-contents")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--window-position=36,68")
chrome_options.add_argument("--window-size=1100,750")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")


# Função principal
def scrape_americanas(produto):
    driver = webdriver.Chrome(options=chrome_options)
    url = f"https://www.americanas.com.br/busca/{produto}"
    driver.get(url)
    
    dic_produtos = {'Modelo': [], 'Preço': [], 'Link': [], 'Marketplace': [], 'Termo Pesquisado': [], 'Termo de Filtro': [], 'Dia da Busca': [], 'Hora da Busca': [], 'Frete': [], 'Vendedor': [], 'Ordem': [], 'Patrocinado': [], 'Avaliação': [], 'Num Avaliações': []}
    n = 1
    try:
        banner = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="styles__CloseButton-sc-1yh2j4k-1 iwYXw"]')))
        banner.click()
    except:
        print('Sem banner')
        sleep(3)
    try:
        cookie_banner = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="lgpd-message-box__Button-sc-v4fjru-3 kTBvxF"]')))
        cookie_banner.click()
        print("Cookie banner closed.")
    except:
        print('Sem cookie banner!')
    try:
        frete_xpath = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//p[@class="cep__Text-sc-1cuzzxo-3 eFrHoi"]')))
        frete_xpath.click()
        sleep(3)
        inserir_cep = driver.find_element(By.XPATH, '//input[@class="src__InputUI-sc-es0u0k-0 fuZRVi"]')
        inserir_cep.send_keys('01153000')
        sleep(3)
        botao_confirmar = driver.find_element(By.XPATH, '//button[@class="src__ButtonUI-sc-es0u0k-1 fesAEB"]')
        botao_confirmar.click()
        print('Cep inserido!')
        sleep(10)
    except:
        print('Erro ao inserir o frete')
    
    # Obtém a quantidade de resultados
    try:
        qtd_itens = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//span[@class="search-result__TotalText-sc-gvih6f-3 cGSdqo"]'))).text.strip()
        print(f'{Fore.GREEN}{qtd_itens} encontrados')
    except:
        print('Não foi possível encontrar a quantidade de itens')

    for pagina in range(1, 2):
        print(f"{Fore.LIGHTYELLOW_EX}Raspando página {pagina + 1} de ...")

        produtos = driver.find_elements(By.XPATH, '//div[@class="inStockCard__Wrapper-sc-1ngt5zo-0 iRvjrG"]')

        for produto in produtos:
            # Encontra os produtos, preços e links.
            marca = produto.find_element(By.XPATH, './/h3[@class="styles__Name-sc-1e4r445-0 fYqJrQ product-name"]').text.strip()
            preco = produto.find_element(By.XPATH, './/span[@class="src__Text-sc-154pg0p-0 styles__PromotionalPrice-sc-yl2rbe-0 dthYGD list-price"]').text.strip()
            link = produto.find_element(By.XPATH, './/a[@class="inStockCard__Link-sc-1ngt5zo-1 JOEpk"]').get_attribute('href')
            link_completo = urljoin(url, link)
            try:
                patrocinado = WebDriverWait(driver, 10).until((EC.presence_of_element_located(By.XPATH, '//span[@class="styles__Text-sc-qjesan-1 iGLno ads-badge-text"]'))).text.strip()
            except:
                patrocinado = 'Não patrocinado!'
            # Acesse a página do produto para obter mais detalhes
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link_completo)
            sleep(5)

            try:
                # Obter valor do frete
                frete = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="src__Text-sc-154pg0p-0 styles__TextUI-sc-4u976a-6 llSqRj freight-option-price"]'))).text.strip()
                
            except:
                frete = 'Não foi possível identificar o frete!'
            
            try:
                avaliacoes = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="src__RatingAverageStyle-sc-gi2cko-2 biDJrW"]'))).text.strip()
            except:
                avaliacoes = 'Não possui avaliações!'

            try:
                num_avaliacoes = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="src__Count-sc-gi2cko-1 laMxpU"]'))).text.strip()
            except:
                num_avaliacoes = 'Não possui num. avaliações!'
            
            try:
                vendedor = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="offers-box__Wrapper-sc-8o518a-0 krMqzo"]'))).text.strip()
            except:
                vendedor = 'Não foi possível encontrar o vendedor!'

            # Fechar a aba do produto e voltar para a aba principal
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
            
            dic_produtos['Modelo'].append(marca)
            dic_produtos['Preço'].append(preco)
            dic_produtos['Link'].append(link_completo)
            dic_produtos['Avaliação'].append(avaliacoes)
            dic_produtos['Num Avaliações'].append(num_avaliacoes)
            dic_produtos['Frete'].append(frete)
            dic_produtos['Marketplace'].append('Americanas')
            dic_produtos['Termo Pesquisado'].append(escolha_do_usuario)
            dic_produtos['Termo de Filtro'].append('')
            dic_produtos['Dia da Busca'].append(datetime.now().strftime("%d-%m-%Y"))
            dic_produtos['Hora da Busca'].append(datetime.now().strftime("%H:%M:%S"))
            dic_produtos['Vendedor'].append(vendedor)
            dic_produtos['Ordem'].append(n)
            dic_produtos['Patrocinado'].append(patrocinado)
            
            print(f"{n}. {marca} // {preco} // {link_completo} // {frete} // {avaliacoes} // {num_avaliacoes} // {vendedor}")
            n += 1

    tabela = pd.DataFrame(dic_produtos)
    print(tabela)
    tabela.to_csv('Resultados_da_pesquisa_americanas.csv', index=False)
    tabela.to_excel('Resultados_da_pesquisa_americanas.xlsx', index=False)

    driver.quit()
escolha_do_usuario = input('Qual produto deseja buscar na Americanas? ')
scrape_americanas(escolha_do_usuario)

