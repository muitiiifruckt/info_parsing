from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional
from datetime import date, timedelta,datetime
from agregator.config_schema import NewsItem, src_prms  # Импортируйте общий NewsItem
from ..config import ag_conf_1 as config
from .rss_parser import save_news_to_txt
import logging


class NewsParser:
    def __init__(self, params: src_prms):
        self.params = params
        self.news_set: set[NewsItem] = set()

    def get_soup(self, html_content: str) -> BeautifulSoup:
        return BeautifulSoup(html_content, 'html.parser')

    def get_news_items(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        try:
            container = soup.find('div', class_=self.params.res_news_cls)
            print(container)
            
            return container.find_all('div', recursive=False) if container else []
        except Exception as e:
            logging.error(f"Ошибка при извлечении списка новостей: {e}")
            return []

    def parse_item(self, item: BeautifulSoup, company: str, page=None) -> Optional[NewsItem]:
        try:
            time_tag = item.find("time")
            news_time = time_tag.text.strip() if time_tag else None

            all_links = item.find_all("a")
            news_title = all_links[-1].text.strip() if all_links else None
            news_link = all_links[-1]["href"] if all_links and all_links[-1].has_attr("href") else None

            if not news_link or not news_title:
                return None

            if news_link.startswith('/'):
                news_link = self.params.source_link + news_link

            article_text = self.get_article_text(page, news_link) if page else None

            return NewsItem(
                time=news_time,
                title=news_title,
                link=news_link,
                source=self.params.source_name,
                description=None,
                emitent=company,
                body=article_text
            )
        except Exception as e:
            logging.error(f"Ошибка при разборе статьи: {e}")
            return None

    def get_article_text(self, page, url: str) -> str:
        try:
            page.goto(url)
            page.wait_for_load_state('networkidle')
            html = page.content()
            soup = self.get_soup(html)
            paragraphs = soup.select(self.params.article_body_selector)
            return '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        except Exception as e:
            logging.warning(f"Не удалось получить текст статьи {url}: {e}")
            return ""

    def parse_news(self, html_content: str, company: str, page=None) -> List[NewsItem]:
        soup = self.get_soup(html_content)
        print("soup", len(soup))
        # print(soup)
        news_items = self.get_news_items(soup)
        
        for item in news_items:
            news = self.parse_item(item, company, page)
            if news:
                self.news_set.add(news)
        return self.news_set

    def print_news(self):
        logging.info("\nНайденные новости:")
        for news in self.news_set:
            logging.info(f"{news.time} | {news.emitent} | {news.title} | {news.link}")

    def run(self, config_data):
        """Главная логика запуска парсера"""
        logging.basicConfig(level=logging.INFO)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            )
            page = context.new_page()

            try:
                for company in config_data.emitent:
                    logging.info(f"\nПоиск новостей о компании: {company}")
                    page.goto(self.params.search_page)
                    time.sleep(1)

                    page.fill(self.params.search_input, company)

                    try:
                        offset = date.today() - timedelta(hours=config_data.time_delta_hours)
                        page.fill('input#from', offset.strftime('%d.%m.%Y'))
                    except Exception as e:
                        logging.warning(f"Не удалось задать дату: {e}")
                    try:
                        if self.params.search_form:
                            page.locator(self.params.search_form).evaluate("form => form.submit()")
                        else:
                            page.press(self.params.search_input, "Enter")
                    except:
                        logging.info("Ошибка при нажатии на поиск")

                    page.wait_for_load_state("networkidle")
                    time.sleep(1)

                    html = page.content()
                    print("html ",len(html))
                    self.parse_news(html, company, page)
                    time.sleep(1)

                self.print_news()
                save_news_to_txt(self.news_set)
                return self.news_set

            finally:
                browser.close()



if __name__ == '__main__':
    from ..config import commersant_params,interfax_params

    parser = NewsParser(commersant_params)
    news = parser.run(config)
    save_news_to_txt(news)