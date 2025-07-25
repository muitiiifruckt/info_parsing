from dataclasses import dataclass
from typing import List, Optional
@dataclass
class SearchConfig:
    """ Класс определения параметров поиска"""
    search_within: bool
    emitent: list[str]
    sources: list[str]
    search_sections: list[str]
    time_delta_hours: int
    
@dataclass
class NewsItem:
    """Класс определяющий вид, в котором будут хранится статьи"""
    time: str
    title: str
    link: str
    source: str
    description: str | None = None
    emitent: str | None = None
    body: str | None = None
    
    
    ### для того чтобы можно было закидывать статьи в set
    def __eq__(self, other):
        if not isinstance(other, NewsItem):
            return False
        return self.link == other.link
    
    def __hash__(self):
        return hash(self.link) 
     ### для того чтобы можно было закидывать статьи в set
    
@dataclass
class SectionsUrlRSS:
    main: str
    economics: str | None
    business: str | None
    financess: str | None
    # другие подразделы, на данный момент нет нужды
    
    
@dataclass
class src_prms:
    """ Определение параметров поиска по источнику (разметка и остальное)"""
    search_page = str 
    search_form = str
    search_input = str
    search_evalute = str
    res_news_cls = str
    res_news_item_cl = str 
    res_item_date  = str
    links_tag = str
    source_link = str
    # параметры для извлечения текста статьи
    
    
    
    
    
    

    
    