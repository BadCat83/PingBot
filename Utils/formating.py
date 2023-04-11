def format_ending(num: int) -> str:
    sec = num % 10
    if sec == 1:
        return 'у'
    elif sec in [2, 3, 4] and num not in [12, 13, 14]:
        return 'ы'
    else:
        return ''

def get_resources_list(resources_list: list) -> str:
    formatted_string = ' - '
    for resource in resources_list:
        formatted_string += f'<em><b>{resource[1]}</b></em>' + ', '
    return formatted_string[:-2]
