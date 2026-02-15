import datetime


def get_first_day_of_next_month(my_date):
    next_month = my_date.replace(day=28) + datetime.timedelta(days=4)
    first_day_of_next_month = datetime.date(next_month.year, next_month.month, 1)
    return first_day_of_next_month


def get_last_day_of_month(my_date):
    first_day_of_next_month = get_first_day_of_next_month(my_date)
    last_day_of_month = first_day_of_next_month - datetime.timedelta(days=1)
    return last_day_of_month


def get_last_day_of_next_month(my_date):
    first_day_of_next_month = get_first_day_of_next_month(my_date)
    last_day_of_next_month = get_last_day_of_month(first_day_of_next_month)
    return last_day_of_next_month


def get_first_day_of_month(my_date):
    first_day_of_month = datetime.date(my_date.year, my_date.month, 1)
    return first_day_of_month