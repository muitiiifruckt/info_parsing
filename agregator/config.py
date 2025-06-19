from .config_schema import SearchConfig



############
# First config
ag_conf_1 = SearchConfig(
sources = [],
emitent = ['Газпром', 'Сбербанк', 'Лукойл'],
search_within = True,
search_sections = ["business","economics","financess"],
time_delta_hours = 24)
#################