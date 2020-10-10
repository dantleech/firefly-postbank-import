Firefly III Postbank Importer
=============================

This script will attempt to import a Postbank CSV file to a [Firefly
III](https://github.com/firefly-iii/firefly-iii) instance.

Installation
------------

Checkout this repository and install the deps using `pipenv`:

```
$ pipenv install
```

Configuration
-------------

Create `config.ini` (or copy `config.ini.example`):

```
[Firefly]
url=http://firefly.example.com
personal_access_token=xxxx

[Account]
name=PostbankAccountName
```

### Firefly

- **url**: The base URL of your firefly instance.
- **personal_access_token**: Your [personal access token](https://firefly-iii.gitbook.io/firefly-iii-bunq-importer/installing-and-running/configure#personal-access-token)

### Account

- **name**: Name of the Firefly account in which to import the transactions

Running
-------

Import your CSV file as follows:

```
$ python3 import-postbank.py Umsatzauskunft_KtoNrxxxxxxx26_10-10-2020_10-07-33.csv
```
