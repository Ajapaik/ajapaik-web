from ajapaik.ajapaik.models import Dating


def parse_fotis_timestamp_data(date_accuracy_in: str):
    if date_accuracy_in == 'Sajand':
        date_accuracy = Dating.CENTURY
        date_format = '%Y'
    elif date_accuracy_in == 'Kümnend':
        date_accuracy = Dating.DECADE
        date_format = '%Y'
    elif date_accuracy_in == 'Aasta':
        date_accuracy = Dating.YEAR
        date_format = '%Y'
    elif date_accuracy_in == 'Kuu':
        date_accuracy = Dating.MONTH
        date_format = '%Y.%m'
    elif date_accuracy_in == 'Kuupäev':
        date_accuracy = Dating.DAY
        date_format = '%Y.%m.%d'
    else:
        date_accuracy = None
        date_format = '%Y.%m.%d'

    return date_accuracy, date_format
