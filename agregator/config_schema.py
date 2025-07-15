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
    
@dataclass
class SectionsUrlRSS:
    main: str
    economics: str | None
    business: str | None
    financess: str | None
    # другие подразделы, на данный момент нет нужды
    

    
    