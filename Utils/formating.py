"""Some formatting functions"""
from datetime import timedelta


def format_ending(num: int) -> str:
    """Formatting ending of the word 'секунда'"""
    sec = num % 10
    if sec == 1:
        return 'у'
    elif sec in [2, 3, 4] and num not in [12, 13, 14]:
        return 'ы'
    else:
        return ''


def format_resources_list(resources_list: list) -> str:
    """Formatting string output"""
    formatted_string = ' - '
    for resource in resources_list:
        formatted_string += f'<em><b>{resource[1]}</b></em>' + ', '
    return formatted_string[:-2]


def time_format(delta: timedelta) -> tuple:
    """Formatting time output"""
    days, seconds = delta.days, delta.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds
