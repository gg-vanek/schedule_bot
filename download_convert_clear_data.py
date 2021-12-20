import requests
import regex as re
import tabula
import pandas as pd
import glob
import numpy as np
import json


def download():
    # скачивает файл с сайта и возвращает его имя в формате типа такого "*** Расписание *** .pdf"
    url = 'https://www.1511.ru/info/study/40'

    pattern = '<a href="(.*?)".*?>(.*?Расписание учеников.pdf.*?)</a>'

    site = requests.get(url).text

    match_obj = re.search(pattern, site)
    file_name = match_obj[2]
    timetable_url = match_obj[1]

    # print(requests.get('https://www.1511.ru' + timetable_url).text)
    with open('data/pdf/' + file_name, 'wb') as f:
        f.write(requests.get('https://www.1511.ru' + timetable_url).content)
    return file_name


def convert():
    pdf_files = glob.glob('data/pdf/*.pdf')

    pdf_pages = tabula.read_pdf(pdf_files[-1], pages='all', multiple_tables=True, pandas_options={'header': None})

    # start1, end1, start2, end2 = map(int, input("Введите (start1, end1, start2, end2)").split())
    start1, end1, start2, end2 = 31, 37, 38, 43

    last_start1, last_end1, last_start2, last_end2, last_start3, last_end3 = 1, 2, 3, 28, 29, 35

    timetable = {}
    for page_number, page in enumerate(pdf_pages):
        if page.shape == (44, 17):
            page = pd.concat([page.iloc[:, 0:5], page.iloc[:, 0], page.iloc[:, 5:]], axis='columns')
            page.iloc[0, 4], page.iloc[0, 5] = np.NaN, page.iloc[0, 4]
            page.columns = range(0, 18)

        if page.shape == (44, 18):
            # сктроки с start1 по end1 включительно сдвинуть на 1 ячейку вправо
            # строки с start2 по end2 сдвинуть на 2 ячейки в право
            first_part = page.iloc[0:start1]  # для 0-start1 оставим также

            # для start1-end1+1 отрежем последний столбец и приканкатим в начало
            second_part = pd.concat([page.iloc[start1:end1 + 1, -1:], page.iloc[start1:end1 + 1, 0:-1]], axis=1)

            # для start2-end2+1 отрежем 2 столбца в конце и приканкатим в начало
            third_part = pd.concat([page.iloc[start2:end2 + 1, -2:], page.iloc[start2:end2 + 1, 0:-2]], axis=1)

            # сделаем одинаковые названия колонок
            second_part.columns = first_part.columns
            third_part.columns = first_part.columns

            # склеим получим чистую страницу
            clear_page = pd.concat([first_part, second_part, third_part], axis=0)

            # далее еще первая строка странн опрочиталась, ее нужно полностью переделать
            # получим номера классов которые есть на этой странице
            page_classes = clear_page.iloc[0].values
            page_classes = [item for item in page_classes if not (pd.isnull(item))]

            # ['Дн', 'Урок', '8А1', '8А2', '8Б1', '8Б2']
            # они выглядят вот так поэтому возьмем срез [2:]
            page_classes = page_classes[2:]

            first_row = [np.NaN, np.NaN, np.NaN, 'Урок', 'Время',
                         page_classes[0], 'Предмет', 'Кабинет',
                         page_classes[1], 'Предмет', 'Кабинет',
                         page_classes[2], 'Предмет', 'Кабинет',
                         page_classes[3], 'Предмет', 'Кабинет',
                         np.NaN]

            clear_page.iloc[0] = first_row

            if page_number > 0 and page_number < 8:
                clear_page.loc[38:, 7] = clear_page.loc[38:, 6]
                clear_page.loc[31:, 6] = clear_page.loc[31:, 5]
                clear_page.loc[31:, 5] = clear_page.loc[31:, 8]

            # далее удалим лишние стобцы
            clear_page = clear_page.drop([0, 1, 2, 17], axis='columns').drop([1], axis='index')
        if page.shape == (44, 10):
            # сктроки с start1 по end1 включительно сдвинуть на 3 ячейку влево
            # строки с start2 по end2 сдвинуть на 2 ячейки в право
            first_part = page.iloc[0:1]  # для 0-start1 оставим также

            # для start1-end1+1 отрежем последний столбец и приканкатим в начало
            second_part = pd.concat(
                [page.iloc[last_start1:last_end1 + 1, 3:], page.iloc[last_start1:last_end1 + 1, :3]],
                axis=1)

            # для start2-end2+1 отрежем 2 столбца в конце и приканкатим в начало
            third_part = pd.concat([page.iloc[last_start2:last_end2 + 1, 2:], page.iloc[last_start2:last_end2 + 1, :2]],
                                   axis=1)

            # для start2-end2+1 отрежем 2 столбца в конце и приканкатим в начало
            forth_part = pd.concat([page.iloc[last_start3:last_end3 + 1, 1:], page.iloc[last_start3:last_end3 + 1, :1]],
                                   axis=1)

            fith_part = page.iloc[last_end3 + 1:, :]
            # сделаем одинаковые названия колонок
            second_part.columns = first_part.columns
            third_part.columns = first_part.columns
            forth_part.columns = first_part.columns
            fith_part.columns = first_part.columns

            clear_page = pd.concat([first_part, second_part, third_part, forth_part, fith_part], axis=0)

            clear_page = pd.concat([clear_page.iloc[:, 0:2], clear_page.iloc[:, -1], clear_page.iloc[:, 2:]],
                                   axis='columns')
            clear_page.columns = range(0, 11)

            page_classes = ['11И1', "11И2"]

            clear_page.iloc[0] = ['Урок', 'Время',
                                  page_classes[0], 'Предмет', 'Кабинет',
                                  page_classes[1], 'Предмет', 'Кабинет', np.NaN, np.NaN, np.NaN]

            clear_page = clear_page.drop([8, 9, 10], axis='columns').drop([1], axis='index')

        # далее тактика такая: отступаем 2 столбца
        # берем 3 следующих стобца (класс, предмет, кабинет)
        # приклеиваем их к предыдущим двум
        # записываем в словарь
        # {класс1: {день1: список уроков, день2: список уроков ...}}, класс2: {...}}

        class_column_groups = [[2, 3, 4], [5, 6, 7]]
        if len(page_classes) == 4:
            class_column_groups.append([8, 9, 10])
            class_column_groups.append([11, 12, 13])

        for class_columns in class_column_groups:
            single_class_timetable_df = clear_page.iloc[:, [0, 1] + class_columns]
            single_class_timetable_dict = {'Понедельник': {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}},
                                           'Вторник': {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}},
                                           'Среда': {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}},
                                           'Четверг': {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}},
                                           'Пятница': {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}},
                                           'Суббота': {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}}}

            iterations_dict = [list(range(1, 8)),
                               list(range(8, 15)),
                               list(range(15, 22)),
                               list(range(22, 29)),
                               list(range(29, 36)),
                               list(range(36, 43))]
            for iteration_day_id, day in enumerate(single_class_timetable_dict):
                for i in range(1, 8):
                    single_class_timetable_dict[day][i]["Время"] = single_class_timetable_df.iloc[
                        iterations_dict[iteration_day_id][i - 1], 1]
                    single_class_timetable_dict[day][i]["Предмет"] = single_class_timetable_df.iloc[
                        iterations_dict[iteration_day_id][i - 1], -2]
                    single_class_timetable_dict[day][i]["Кабинет"] = single_class_timetable_df.iloc[
                        iterations_dict[iteration_day_id][i - 1], -1]
            timetable[single_class_timetable_df.iloc[0, 2]] = single_class_timetable_dict

    # exit_file_name = 'data/json/' + pdf_files[-1].split('\\')[-1][:-4] + '.json'
    exit_file_name = 'data/json/schedule.json'
    # clear_data(timetable)
    with open(exit_file_name, 'w', encoding="cp1251") as f:
        json.dump(timetable, f)

    return exit_file_name


def clear_data(path):
    with open(path, 'r') as f:
        timetable = json.load(f)

    week_days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    time_subj_room_keys = ['Время', 'Предмет', 'Кабинет']

    for class_name in ['11И1', '11И2']:
        t = timetable[class_name]
        for n, i in enumerate(week_days[:-1]):
            times = t[i]['7'][time_subj_room_keys[0]].split('\r')
            subjects = t[i]['7'][time_subj_room_keys[1]].split('\r')
            classrooms = t[i]['7'][time_subj_room_keys[2]].split('\r')
            if len(times) == 3:
                times = [times[0]] + [times[2]]
                subjects = [np.NaN] + [subjects[1]]
            if len(subjects) == 1:
                subjects = [np.NaN] + [subjects[0]]
            if len(classrooms) == 1:
                classrooms = [np.NaN] + [classrooms[0]]
            if len(times) == 2:
                t[i]['7'][time_subj_room_keys[0]] = times[0]
                t[i]['7'][time_subj_room_keys[1]] = subjects[0]
                t[i]['7'][time_subj_room_keys[2]] = classrooms[0]

                t[week_days[n + 1]]['1'][time_subj_room_keys[0]] = times[1]
                t[week_days[n + 1]]['1'][time_subj_room_keys[1]] = subjects[1]
                t[week_days[n + 1]]['1'][time_subj_room_keys[2]] = classrooms[1]
    with open(path, 'w') as f:
        json.dump(timetable, f)


def main():
    download()
    exit_file_name = convert()
    clear_data(exit_file_name)

    return exit_file_name


if __name__ == '__main__':
    main()
