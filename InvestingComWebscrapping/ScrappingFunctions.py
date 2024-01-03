from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup

def get_training_links(pages):

    driver = webdriver.Firefox()
    links = []

    for page in range(1, pages + 1):

        url_path = f'https://www.investing.com/news/stock-market-news/{page}'
        driver.get(url_path)

        left_column = driver.find_element(by=By.ID, value="leftColumn")
        article_items = left_column.find_elements(by = By.CLASS_NAME, 
                                                    value = "articleItem")
        for article in article_items:
            try:
                link = article.find_element(by=By.CLASS_NAME, value="title")
                links.append(link.get_attribute("href"))
            except:
                continue
            
    driver.quit()
    return links

def get_article_text(link):

    response = requests.get(link)

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('div', class_='WYSIWYG articlePage')
        date = soup.find("div", class_ = "contentSectionDetails")

        if article != None:
            script = article.find("script")
            if script != None:
                script.extract()
            img_carousel = article.find('div', class_='imgCarousel')
            if img_carousel != None:
                img_carousel.extract()
            related_instruments_wrapper = article.find('div', 
                                                        class_='relatedInstrumentsWrapper')
            if related_instruments_wrapper != None:
                related_instruments_wrapper.extract()
            paragraph = article.find("p")
            if paragraph != None:
                em = paragraph.find("em")
                if em != None:
                    paragraph.extract()
            text_inside_div = article.get_text()
            text_inside_div = text_inside_div.strip()
        else:
            text_inside_div = None
            
        if date != None:
            try:
                cont_sect_det = soup.find_all("div", class_ = "contentSectionDetails")
                date = cont_sect_det[1].find("span").text
                date = date[10:-11]
            except:
                date = None
        else:
            date = None
            
        return [text_inside_div, date]
        
    else:
        return [None, None]
    
def get_article_texts(links, tracker = False):
    results = []
    for i, link in enumerate(links):
        results.append(get_article_text(link))
        if tracker:
            print(i + 1, "/", len(links))
    return results

def get_stock_links(search_term, limit = 100):

    driver = webdriver.Firefox()
    
    url_path = f'https://www.investing.com/search/?q={search_term}&tab=news'
    driver.get(url_path)

    links = []

    pos = 0
    while len(driver.find_elements(by=By.CLASS_NAME, value="articleItem")) < limit:
        pos += 500
        driver.execute_script(f'window.scrollTo(0, {pos})')

    article_items = driver.find_elements(by=By.CLASS_NAME, value="articleItem")  
    for article in article_items:
        if article.get_attribute("class") != "js-article-item articleItem     ": 
            link = article.find_element(by=By.CLASS_NAME, value="title")         
            links.append(link.get_attribute("href"))             
            
    driver.quit()
    return links