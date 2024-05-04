from datetime import datetime

def convert_datestring(date_string):
    date_object = datetime.strptime(date_string, '%m/%d/%Y')
    readable_date = date_object.strftime('%B %d, %Y').replace(' 0', ' ')
    day = date_object.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = 'th'
    else:
        suffix = ['st', 'nd', 'rd'][day % 10 - 1]

    readable_date = readable_date.replace(f' {day} ', f'{day}{suffix}')
    return readable_date
