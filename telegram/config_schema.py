
from dataclasses import dataclass

@dataclass
class SearchConfig:
    """ Класс определения параметров поиска"""
    search_within: bool = False | None
    emitent: list[str]
    sources: list[str]
    
@dataclass
class News:
    """Класс определяющий вид, в котором будут хранится статьи"""
    time: str
    title: str | None
    tg_name: str
    body: str | None
    
    