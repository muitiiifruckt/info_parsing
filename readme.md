Порядок работы скрипта

Есть конфиг в котором прописывается основыные параметры которые включают в себя:
1) Эмитентный список поиска
2) Список ресурсов для поиска (из возможных)
3) Флаг - идет ли поиск внутри статьи
4) Список, который определяет типы статей (экономика, бизнес и т.д.)


Стратегия работы:
1) По конфигу поиск статей по ресурсу по эмитентным спискам.
2) Сначала поиск по наличию слов внутри названии статьи.Если есть поиск внутри статьи, то получение самой статьи, и затем поиск. Оставляем эти статьи
3) Возможно сопоставление статей __!__!__!__!__!
4) Обработка самых статей и выслать.


Стади  работы: 
1) Пока более менее определены методы поиска, текущая задача продумать общий вид  и по порядку привести все коннекторы (питон файлы для поиска по опредделному сайту) к ним 
2) Почти дописал для "Коммерсант" осталось дописать поиск и правильно все оформить
3) Поправка по методу сбора статей, сбор раз в день не очень подходит, в 
некоторых сайтах хранятся записи за последнее часов только (30 шт) РБК например, в таком скрипт должен собирать данные с некторых сайтов с частотой в несколько часов, в остальных можно и так оставить.
4) Коммерсант почти доделал, работает по конфигу, осталось привести к единому виду
5) У РБК не все так просто, отдельной RSS по категориям у него нет, а так же там только 30 новостей которые не покрывают наши ожидания - из варинатов мониторить RSS с чеком категории, или сделать поиск по РБК по эмитентам???
6) У ТАСС тоже статьи за очень короткий период - похоже все таки надо мониторить каждые 1-2 часа или меньше, большинтсво сайтов подстроено под такие условия, каждые полчаса.
7) У "Ведомости" также как и коммерсант - несколько разделов и статьи за последние 2-3 дня в RSS, написал также как и в коммерсанте -работает. Теперь надо написать скрипт, который достает каждые полчаса у сайтов, RSS которых хранит только последние новости. Это "ТАСС", "РБК"
8) Написал, теперь достаются новости из выешеперечисленных сайтов по короткому таймингу. 
9) Надо рассмотреть разметку текста у РИА и РОССИЙСКАЯ ГАЗЕТА

TODO:
ВРЕМЯ ГОТОВНОСТИ ВСЕХ СТАТЕЙ - 8:00 каждый день.


Также нужно  определить общее хранилище для статей уже после селекции по эмитентам, и организовать добавление туда и очистку после отправки.
Определить промежуточное хранилище, чтобы отсеивать ненужные статьи - копии - хранить только сами ссылки.


Интерфакс, Ведомости, Коммерсант - запускать синхронно (недолго выполняются)


Что работает уже нормально:
1) Интерфакс - модуль работает нормально, новости получаются за день, происходит слелекция по эмитентам, дубликаты убираются, записи хранится НАЗВАНИЕ, ВРЕМЯ, ССЫЛКА, СТАТЬЯ - все что нужно. 
2) Ведомости - модуль работает нормально, новости можно получить за день (регулирются), происходит селекция по эмитентам.
3) Коммерсант- - модуль работает нормально, новости можно получить за день (регулирются), происходит селекция по эмитентам.
4) У ТАСС РИА РБК РУССКАЯГАЗЕТА - новости хранятся за последние ~ 10 минут, нужно их каждые 10 минут доставать, проводить селекцию по эмитентам и сохранять в файл. Так как новости нужны только за день, то после отправки их нужно удалять. 
По скорости вроде нормально - около 2 минут на весь сбор и селекцию - можно оставить синхронный вариант
________________________________________________________

ТГ - порядок работы

Стратегия работы тг агрегатора

Есть конфиг в котором прописывается основыные параметры которые включают в себя:
1) Эмитентный список поиска
2) Список ресурсов для поиска (из возможных), тг-каналы
3) Флаг - идет ли поиск внутри статьи


Стратегия работы:
1) Получение всех статей запоследние n дней.
2) Поиск эмитентов в названиях статей, затем (если есть флаг) поиск эмитентов в теле статей


