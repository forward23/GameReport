import pandas
import psycopg2
from log import create_logger

def get_from_db():
    logger.debug('Getting info from DB')
    pass

def make_report(data):
    logger.debug('Making report')
    pass

def sent_result(report):
    logger.debug('Saving report')
    pass


def main():
    data = get_from_db()
    report = make_report(data)
    sent_result(report)


if __name__ == '__main__':
    logger = create_logger()
    main()