"""
Selection - консольное приложение, позволяющее делать выборку данных Excel/CSV
Последовательность выполнения приложения:

1. Запись пути до файла с данными
    1.1 Выбор между CSV и Excel файла +
    1.2 Возврат данных в формате pandas DataFrame +

2 Выборка
    2.1.1 Выбрать по какой(им) колонке(ам) сделать выборку
    2.1.2 Ввести параметры для выборки
    2.1.3 Создать файл с выбранными данными и завершить работу

"""

from __future__ import annotations
import pandas as pd
from pandas import DataFrame

pd.options.mode.chained_assignment = None
FileName = None
ColToDel = []


def CheckInt(number):
    """
    Возвращает строку для метода eval в которую входит число и преобразование в int, если значение можно
    преобразовать в int, если нет - возвращается False
    :param number:
    :return:
    """
    try:
        int(number)
    except ValueError:
        return False
    return f'int({number})'


def CheckFloat(number):
    """
    Возвращает строку для метода eval в которую входит число и преобразование в float, если значение можно
    преобразовать в float, если нет - возвращается False
    :param number:
    :return:
    """
    try:
        float(number)
    except ValueError:
        return False
    return f'float({number})'


def MicroCorrect(part):
    """

    :param part: Часть из условия отбора, которую нужно разделить на операнд и значение
    :return:
    """
    return [part[:2], part[2:]] if part[1] == '=' else [part[0], part[1:]]


class Selection:
    """
    Класс выборки данных из таблицы
    """

    def __init__(self,
                 data: DataFrame,
                 Columns: list,
                 Types: list):

        self.data = data
        self.col_types = {k: v for k, v in zip(Columns, Types)}

    def getType(self, Name):
        """
        Возвращает тип колонки
        :param Name: Имя колонки
        :return:
        """
        return self.col_types[Name]

    def MakeNewCol(self, TypeOf, name):
        """
        Метод который создает новую колонку в таблице с целью возможности выборки из типа колонки - object
        :param TypeOf: Тип значение в логической операции
        :param name: Название колонки
        :return:
        """

        self.data = self.data.loc[
            self.data[f'{name}'] != 'Unknown']  # Отбираются строки, у которых нет 'Unknown' в колонке {name}
        if TypeOf == 'int':
            buff = self.data[f'{name}'][6].split(
                ' ')  # Буфферная переменная хранящая в себе строку для поиска float значения
            for i in range(len(buff)):
                if CheckFloat(buff[i]):
                    self.data[f'{name}1'] = self.data[f'{name}'].apply(lambda x: str(x).split(' ')[i]).astype(
                        float)  # В новую колонку name1 отбираются нужные данные из строки
                    break
        else:
            buff = self.data[f'{name}'][6].split(' ')
            for i in range(len(buff)):
                if not CheckFloat(buff[i]):
                    self.data[f'{name}1'] = self.data[f'{name}'].apply(lambda x: str(x).split(' ')[i])
                    break

    def MakeSequence(self, sequence, colName):
        """
        Метод, в зависимости от типа данных второй части условия, корректирует все выражение, чтобы не выкидывало ошибку
        :param sequence: Выражение начиная с операнда
        :param colName: Название колонки для которой проводится выборка
        :return: кортеж состоящий из строкового выражения и названия колонки
        """
        listOfSel = sequence.split(' ')  # Создается список из строки формата {операнд}''/' '{Условие}

        if len(listOfSel) == 1:  # Если между операндом и условием нет пробела - с помощью дополнительного метода исправляется
            corr = MicroCorrect(part=listOfSel[0])

            listOfSel[0] = corr[0]
            listOfSel.append(corr[1])
        Type = Selection.getType(self, colName)
        if Type == 'object':
            if CheckFloat(listOfSel[1]):
                Selection.MakeNewCol(self, 'int', colName)
            else:
                Selection.MakeNewCol(self, 'str', colName)
                listOfSel[1] = f'"{listOfSel[1]}"'

            colName = f'{colName}1'
            ColToDel.append(colName)
        elif Type == 'float64':
            listOfSel[1] = CheckFloat(listOfSel[1])
            while not listOfSel[1]:
                listOfSel[1] = CheckFloat(input("Input float number: "))
        elif Type == 'int64':
            listOfSel[1] = CheckInt(listOfSel[1])
            while not listOfSel[1]:
                listOfSel[1] = CheckInt(input("Input integer number: "))

        return ' '.join(listOfSel), colName

    def dropUnknown(self):
        for col in self.data.columns:
            self.data = self.data.loc[self.data[f'{col}'] != 'Unknown']

    def selection(self):
        sequence = []
        self.data = self.data.dropna()
        Selection.dropUnknown(self)
        for k, v in self.col_types.items():
            seq = input(f"Input sequence for {k} column (start with operand): ")
            seq, k = Selection.MakeSequence(self, seq, k)
            sequence.append(f'(self.data["{k}"] {seq})')

        if len(sequence) > 1:
            sequence = ' & '.join(sequence)
        else:
            sequence = sequence[0]
        self.data = self.data[eval(sequence, {'self': self})]
        self.data = self.data.drop(ColToDel, axis=1)
        self.data.to_excel(f'Selection {FileName}', index=False, sheet_name='Selection')


def set_colNames(i: int = 0) -> list:
    """
    Функция определения названий колонок
    :param i: parameter for name loop
    :return ColNames: list of column names
    """
    ColNames = []

    print('Input columns names. Empty input for the end:')

    while True:
        i += 1
        ColNames.append(input(f'{i} column: '))
        if not ColNames[-1]:
            break

    return ColNames[:-1]


def set_types(columns, DF) -> list:
    """
    Функция определения типов данных в колонках
    :param DF: data in DataFrame
    :param columns: A list of column names
    :return TypeNames: list of column types
    """
    TypeNames = []
    for i in columns:
        Types = DF.dtypes.to_dict()
        inTypeArr = str(Types[f'{i}'])
        TypeNames.append(inTypeArr)

    return TypeNames


def to_df(file_url: str,
          file_type: str,
          colNames: list | tuple | set | None = None) \
        -> DataFrame:
    """
    Функция для конвертации файла XLSX или CSV в pandas DataFrame
    :param file_url: Direction of file
    :param file_type: Type of file (xlsx or csv)
    :param colNames: Column names
    :return: DataFrame
    """
    data = None

    if file_type == 'csv':
        separ = input('Input separator in CSV-file: ')
        data = pd.read_csv(file_url, sep=separ)
    elif file_type == 'xlsx':
        sh_name = input('Input active sheet name: ')
        if sh_name:
            data = pd.read_excel(file_url, sheet_name=sh_name)
        else:
            data = pd.read_excel(file_url)

    NeedCol = int(input('Did you need a columns? (1 - Yes, 0 - No): '))
    if NeedCol:
        colNames = set_colNames()

    return DataFrame(data=data, columns=colNames)


if __name__ == '__main__':
    url = input(r'Input way to Excel/CSV table: ')
    ftype = url.split(r'\\')[-1].split('.')[-1]
    FileName = url.split('\\')[-1]

    df = to_df(file_url=url,
               file_type=ftype)

    SelColNames = set_colNames()
    print('Column names for selection\n', SelColNames)
    __choose__ = Selection(data=df,
                           Columns=SelColNames,
                           Types=set_types(SelColNames, df))
    __choose__.selection()

