from io import StringIO
from pprint import pprint
import argparse
import configparser
import datetime
import hashlib
import json
import locale
import pandas
import requests
import string

def post_transactions(config, data, context):
    headers = {
        'Authorization': 'Bearer %s' % config.get('Firefly', 'personal_access_token'),
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }

    response = requests.post(
        '%s/api/v1/transactions' % config.get('Firefly', 'url'),
        headers=headers,
        data=json.dumps(build_payload(config, data, context))
    )

    if response.status_code != 200:
        print(json.dumps(json.loads(response.text), indent=4))
        quit(0)

def build_payload(config, data, context):
    payload = {
        'error_if_duplicate_hash': not config.getboolean('Firefly', 'ignore_error_on_duplicate'),
        'group_title': 'Postbank import %s (%s)' % (datetime.date.today().strftime('%Y/%m/%d'), context),
        'transactions': []
    }

    for index, row in data.iterrows():
        if row['Amount'] > 0:
            payload['transactions'].append({
                'type': 'deposit',
                'description': row['Buchungsdetails'],
                'amount': abs(row['Amount']),
                'date': row['Buchungsdatum'],
                'currency_code': 'EUR',
                'destination_name': config.get('Account', 'name'),
                'source_name': row['Auftraggeber'],
                'external_id': hashlib.md5(
                    ('%s%s%s' % (
                        str(row['Amount']),
                        row['Buchungsdatum'],
                        row['Buchungsdetails']
                    )).encode('utf-8')
                ).hexdigest()
                })
            continue

        payload['transactions'].append({
            'type': 'withdrawal',
            'description': row['Buchungsdetails'],
            'amount': abs(row['Amount']),
            'date': row['Buchungsdatum'],
            'currency_code': 'EUR',
            'destination_name': row['Empfänger'],
            'source_name': config.get('Account', 'name')
        })

    return payload

def main():
    locale.setlocale(locale.LC_ALL, 'de_DE')
    config = configparser.ConfigParser()
    parser = argparse.ArgumentParser(description='Export Postbank CSV to Firefly III')
    parser.add_argument('path', type=str, help='Postbank CSV')
    parser.add_argument('--ignore-error-on-duplicate', help='Allow duplicates to be added', default=False, action='store_true')
    args = parser.parse_args()
    config['Firefly'] = {
            'ignore_error_on_duplicate': 'true' if args.ignore_error_on_duplicate else 'false'
    }
    config.read('config.ini')

    with open(args.path, 'r', encoding='latin1') as handle:
        data = handle.read().splitlines(True)

    data = pandas.DataFrame(
            pandas.read_table(StringIO(''.join(data[14:])), encoding='iso-8859-1', delimiter=';')
    ).astype(str).rename(columns={
        'Betrag (\x80)': 'Amount',
    })

    data['Amount'] = data['Amount'].apply(lambda x: locale.atof(x.replace('\x80', '')))
    data['Buchungsdatum'] = data['Buchungsdatum'].apply(lambda x: datetime.datetime.strptime(x, '%d.%m.%Y').isoformat())

    post_transactions(config, data[data['Amount'] > 0], 'deposit')
    post_transactions(config, data[data['Amount'] < 0], 'withdrawal')

main()
