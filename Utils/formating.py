def format_ending(num: int) -> str:
    sec = num % 10
    if sec == 1:
        return 'у'
    elif sec in [2, 3, 4] and num not in [12, 13, 14]:
        return 'ы'
    else:
        return ''
