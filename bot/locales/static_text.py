
def accepted_language(language):
    match language:
        case "Русский":
            return 'Язык подтвержден'
        case "English":
            return 'Language accepted'
        case _:
            return None
        
def select_tel_number(language):
    match language:
        case "Русский":
            return 'Введите номер телефона или отправьте его с помощью бота'
        case "English":
            return 'Select tel number'
        case _:
            return None