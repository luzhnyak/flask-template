from datetime import datetime


def transliterate(text, *ex):

    slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'д': 'd', 'е': 'e', 'ё': 'e',
              'ж': 'zh', 'з': 'z', 'и': 'y', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ia', 'А': 'a', 'Б': 'b', 'В': 'v', 'Г': 'h', 'Д': 'd', 'Е': 'e', 'Ё': 'e',
              'Ж': 'zh', 'З': 'z', 'И': 'y', 'Й': 'y', 'К': 'k', 'Л': 'l', 'М': 'm', 'Н': 'n',
              'О': 'o', 'П': 'p', 'Р': 'r', 'С': 's', 'Т': 't', 'У': 'u', 'Ф': 'f', 'Х': 'h',
              'Ц': 'ts', 'Ч': 'ch', 'Ш': 'sh', 'Щ': 'shch', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'e',
              'Ю': 'u', 'Я': 'ya', ',': '', '?': '', ' ': '-', '~': '', '!': '', '@': '', '#': '',
              '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '=': '', '+': '',
              ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
              '[': '', ']': '', '{': '', '}': '', 'ґ': 'g', 'і': 'i', 'ї': 'i', 'Ґ': 'g', 'І': 'i', 'Ї': 'i', 'є': 'ie',
              'Є': 'ye', '.': '-', '–': '-', '---': '-', '----': '-', '--': '-', '«': '', '»': ''}

    for key in ex:
        del slovar[key]

    for key in slovar:
        text = text.replace(key, slovar[key])

    for key in slovar:
        text = text.replace(key, slovar[key])

    return text.lower()


def timeNow(format_date):
    if format_date == "d":
        return datetime.strftime(datetime.now(), "%d.%m.%Y")
    elif format_date == "t":
        return datetime.strftime(datetime.now(), "%H:%M:%S")
    elif format_date == "u":
        return datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    elif format_date == "ud":
        return datetime.strftime(datetime.now(), "%Y-%m-%d")
    elif format_date == "y":
        return datetime.strftime(datetime.now(), "%Y")
    else:
        return datetime.strftime(datetime.now(), "%d-%m-%Y %H:%M:%S")
