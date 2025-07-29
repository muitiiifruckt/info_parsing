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
from .e_parser import NewsParser


class CommersantParser(NewsParser):
    def parse_item(self, item: BeautifulSoup, company: str, page=None) -> Optional[NewsItem]:
        try:
            date_block = item.find("p", class_="uho__tag")
            raw_date = date_block.get_text(strip=True)
            news_time = raw_date.split("/")[-1].strip()
            print(news_time)
            
            h2 = item.find("h2", class_="uho__name")
            a_tag = h2.find("a")
            news_title = a_tag.get_text(strip=True)
            news_link = "https://www.kommersant.ru/" + a_tag["href"]
            print(news_link)
            print(news_title)

            if not news_link or not news_title:
                return None

            if news_link.startswith('/'):
                news_link = self.params.source_link + news_link

            article_text = self.get_article_text(page, news_link) if page else None
            print(article_text)

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
            time.sleep(1)
            html = page.content()
            soup = self.get_soup(html)
            paragraphs = soup.select(self.params.article_body_selector)

            # Ключевые слова, по которым будем удалять мусор
            stopwords = [
                "Подписывайтесь", "Промо", "Telegram", "реклама", "©", "АО «Коммерсантъ»",
                "Сетевое издание", "коммерческой основе", "Подробнее", "18+", "Новости компаний",
                "Фото:", "Реклама", "Благотворительный фонд"
            ]

            # Фильтрация текста
            lines = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if not text:
                    continue
                if any(stopword in text for stopword in stopwords):
                    continue
                lines.append(text)

            return '\n\n'.join(lines)

        except Exception as e:
            logging.warning(f"Не удалось получить текст статьи {url}: {e}")
            return ""

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
                    try:
                        logging.info(f"\nПоиск новостей о компании: {company}")
                        page.goto(self.params.search_page)
                        time.sleep(1)
                        page.click("#js-navsearch-submit")
                        time.sleep(1)
                        page.fill(self.params.search_input, company)

                        try:
                            time.sleep(1)
                            page.click("#js-navsearch-submit")

                        except:
                            logging.info("Ошибка при нажатии на поиск")
                        try:
                            page.click("body > main > div > div > section > div.grid-col.grid-col-s3 > form > div.ui-field_pack > label")
                            offset = date.today() - timedelta(hours=config_data.time_delta_hours)
                            date_str = offset.strftime('%Y-%m-%d')
                            page.fill('input[name="dateStart"]', date_str)
                            time.sleep(0.5)
                            page.keyboard.press("Enter")
                            time.sleep(0.5)
                        except Exception as e:
                            logging.warning(f"Не удалось задать дату: {e}")

                        page.wait_for_load_state("networkidle")
                        time.sleep(1)

                        html = page.content()
                        print("html ",len(html))
                        self.parse_news(html, company, page)
                        time.sleep(1)
                    except:
                        logging.error(f"Ошибка при обработке - [{company}]")

                self.print_news()
                save_news_to_txt(self.news_set)
                return self.news_set

            finally:
                browser.close()
    def get_news_items(self, soup: BeautifulSoup) -> List[BeautifulSoup]:
        try:
            container = soup.find('div', class_=self.params.res_news_cls)
            #print(container)
            news = container.find_all("article", class_="uho rubric_lenta__item")
            #print(news)
            return news
        except Exception as e:
            logging.error(f"Ошибка при извлечении списка новостей: {e}")
            return []
if __name__ == '__main__':
    from ..config import commersant_params,interfax_params

    parser = CommersantParser(commersant_params)
    news = parser.run(config)
    save_news_to_txt(news)