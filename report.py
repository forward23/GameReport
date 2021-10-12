import argparse
import datetime
import os
import pandas as pd
import psycopg2
from decouple import config

from log import create_logger
from sql_scripts import get_query_payins

YESTERDAY = format(datetime.date.today() - datetime.timedelta(days=1))
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

conn_info = {
    'database': config('DATABASE'),
    'user': config('USER_NAME'),
    'password': config('PASSWORD'),
    'host': config('HOST'),
    'port': config('PORT')
}

def get_from_db(start, end, currency):
    logger.debug(f'Getting info from DB from {start} to {end} in {currency}')

    # connect to Postgres and get data
    with psycopg2.connect(**conn_info) as conn:
        with conn.cursor() as cur:
            cur.execute(get_query_payins(start, end, currency))
            res = cur.fetchall()

    # convert data to DataFrame
    data_df = pd.DataFrame(res, columns=['Date', 'Installs', 'payment_date', 'rolling_gross_ltv', 'rolling_net_ltv',
                                         'date_number'])

    return data_df


def make_report(data_df):
    logger.debug('Making report')

    # gross report
    df_gross = data_df.pivot_table(columns='date_number', index='Date', values='rolling_gross_ltv', aggfunc='sum') \
        .round(2)
    df_gross_renamed = df_gross.rename({col: f'LTV-{col}' for col in df_gross.columns}, axis=1).reset_index()
    df_gross_installs = data_df.groupby(['Date', 'Installs']) \
        .rolling_gross_ltv.max() \
        .round(2) \
        .reset_index() \
        .rename(columns={'rolling_gross_ltv': 'LTV'})

    gross = df_gross_installs.merge(df_gross_renamed)

    # net report
    df_net = data_df.pivot_table(columns='date_number', index='Date', values='rolling_net_ltv', aggfunc='sum') \
        .round(2)
    df_net_renamed = df_net.rename({col: f'LTV-{col}' for col in df_net.columns}, axis=1).reset_index()
    df_net_installs = data_df.groupby(['Date', 'Installs']) \
        .rolling_net_ltv.max() \
        .round(2) \
        .reset_index() \
        .rename(columns={'rolling_net_ltv': 'LTV'})

    net = df_net_installs.merge(df_net_renamed)

    return gross, net


def sent_result(gross, net):
    logger.debug('Saving report')

    gross.to_csv(os.path.join(BASE_DIR, f'report_gross_{args.currency}.csv'), index=False)
    net.to_csv(os.path.join(BASE_DIR, f'report_net_{args.currency}.csv'), index=False)


def main(start, end, currency):
    logger.debug('<START report>')

    data = get_from_db(start, end, currency)
    sent_result(*make_report(data))

    logger.debug('<FINISH report>')


if __name__ == '__main__':
    # create logger
    logger = create_logger()

    # create args parser
    parser = argparse.ArgumentParser(description='Making report: LTV growth of daily player cohorts by days of life')
    parser.add_argument('-S', '--start', metavar='', help='start date in format yyyy-mm-dd')
    parser.add_argument('-E', '--end', metavar='', help='end date in format yyyy-mm-dd')
    parser.add_argument('-C', '--currency', metavar='', help='currency for report: EUR (default) | USD | RUB')
    args = parser.parse_args()

    # default start date is '2021-01-01'
    if not args.start:
        args.start = '2021-01-01'

    # default end date is YESTERDAY
    if not args.end or args.end > YESTERDAY:
        args.end = YESTERDAY

    # default currency is EUR
    if not args.currency or args.currency not in ('EUR', 'USD', 'RUB'):
        args.currency = 'EUR'

    # Run report
    main(args.start, args.end, args.currency)
