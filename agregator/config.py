from .config_schema import SearchConfig, src_prms



############
# First config
ag_conf_1 = SearchConfig(
sources = [],
emitent = ['Газпром', "Норникель", 'Лукойл',"МТС","Башнефть","Роснефть","Транснефть","ФСК Россети","Слфвянск ЭКО","Сегежа","Гидромашсервис","Уралкалий","Русал",
           "Эн+Гидро", "Альфа-лизинг", "Альфа банк", "Мегафон", "Билайн","РОссети","ГТЛК", "Татнефть","Аэрофлот","ЭН+ГРуп","ТЛК", "Селектел",
           "ICL"],
search_within = True,
search_sections = ["business","economics","financess"],
time_delta_hours = 72)
#################
interfax_params = src_prms(
    search_page="https://www.interfax.ru/search/",
    search_form=".sPageForm",
    search_input="main input[name='phrase']",
    search_evalute="form => form.submit()",
    res_news_cls="sPageResult",
    res_news_item_cl="sPageResult__item",
    item_date_selector="time",
    item_title_selector = "div > a:nth-of-type(2)",  # уточни селектор
    item_link_selector = "div > a:nth-of-type(2)",   # уточни селектор
    source_link="https://www.interfax.ru",
    article_body_selector="p",
    source_name="interfax"
    ) 
commersant_params = src_prms(
    search_page="https://www.kommersant.ru/",
    search_form=".sPageForm",
    search_input = "input[name='search_query']",
    search_evalute = "form => form.submit()",
    res_news_cls="rubric_lenta search_lenta",
    res_news_item_cl="sPageResult__item",
    item_date_selector="time",
    item_title_selector = "div > a:nth-of-type(2)",  # уточни селектор
    item_link_selector = "div > a:nth-of-type(2)",   # уточни селектор
    source_link="https://www.kommersant.ru/",
    article_body_selector="p",
    source_name="commersant"
    )