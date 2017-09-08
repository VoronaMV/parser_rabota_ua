import datetime


def clear_digit(string):
    if not isinstance(string, str):
        raise TypeError
    for symb in string:
        if not symb.isdecimal():
            string = string.replace(symb, '')
    return string


def lang_level_gerade(level):
    if not isinstance(level, str):
        raise TypeError
    grade_dict = {u'базовый': 1,
                  u'базовий': 1,
                  u'elementary': 1,
                  u'ниже среднего': 2,
                  u'нижче середнього': 2,
                  u'lower intermediate': 2,
                  u'средний': 3,
                  u'середній': 3,
                  u'intermediate': 3,
                  u'выше среднего': 4,
                  u'вище середнього': 4,
                  u'upper intermediate': 4,
                  u'продвинутый': 5,
                  u'поглиблений': 5,
                  u'advanced': 5,
                  u'свободно': 6,
                  u'вільно': 6,
                  u'fluent': 6,
                  u'родной': 6,
                  u'рідна': 6,
                  u'native': 6
                  }
    return grade_dict[level]

# Transform date strings to format required by database
def date_transform(date_str):
    if not isinstance(date_str, str):
        raise TypeError
    date_str = date_str.lower()
    date_arr = date_str.split('-')
    date_arr[0] = date_arr[0].strip()
    end_date = date_arr[1].split('(')[0]
    if 'настоящее время' in end_date or 'present time' in end_date:
        end_date = datetime.datetime.now().strftime("%m-%d-%Y")
    end_date = end_date.strip()
    date_arr[1] = end_date
    ru = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
    ua = ['січ', 'лют', 'бер', 'кві', 'тра', 'чер', 'лип', 'сер', 'вер', 'жов', 'лис', 'гру']
    en = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    numb_months = [i for i in range(1, 13)]
    numb_months = list(map(lambda i: '0' + str(i) if i < 10 else str(i), numb_months))
    for j in range(12):
        for i, date in enumerate(date_arr):
            if ru[j] in date:
                date_arr[i] = date.replace(ru[j], numb_months[j])
            if ua[j] in date:
                date_arr[i] = date.replace(ua[j], numb_months[j])
            if en[j] in date:
                date_arr[i] = date.replace(en[j], numb_months[j])
    date_arr = list(map(lambda date: date.replace(' ', '-01-'), date_arr))
    (begin_date, end_date) = date_arr
    return (begin_date, end_date)


def check_alpha(string):
    flag = False
    for symb in string:
        if symb.isalpha():
            flag = True
    return flag