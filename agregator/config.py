from .config_schema import SearchConfig



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