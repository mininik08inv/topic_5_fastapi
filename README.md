Приложение, которые будет использовать данные из таблицы «spimex_trading_results»
и отдавать их в формате JSON.
Функции для реализации: *
· get_last_trading_dates – список дат последних торговых дней (фильтрация по кол-ву последних торговых дней).
· get_dynamics – список торгов за заданный период (фильтрация по oil_id, delivery_type_id, delivery_basis_id,
start_date, end_date).
· get_trading_results – список последних торгов (фильтрация по oil_id, delivery_type_id, delivery_basis_id)