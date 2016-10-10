#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys
import os
import re
import unittest
from lib.etl.dispatcher import ETLDispatcher
from lib.history.dao import create_tables
from lib.new_relic.client import NewRelicClient
from tests.test_app_loads import AppLoadsTestCase
from tests.test_errors import ExceptionsTestCase, CrashesTestCase
from tests.test_history import HistoryTestCase
from tests.test_performance import PerformanceTestCase
from tests.test_transactions import TransactionsTestCase
from tests.test_app_versions import AppVersionsTestCase

sys.path.insert(0, os.path.abspath('..'))

from clint.arguments import Args
from clint.textui import puts, colored, indent

all_args = Args()

logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().setLevel(logging.DEBUG)

NR_ACCOUNT_ID = str(os.environ.get('NR_ACCOUNT_ID'))
NR_INSERT_KEY = str(os.environ.get('NR_INSERT_KEY'))

MODE_SPECIFIER = ('^test|upload$')
with indent(4, quote='>>>'):
    puts(colored.green('Arguments passed in: ') + str(all_args.all))

    args = all_args.not_flags

    if not len(args):
        puts(colored.red('Mode Required. Valid input: %s' % MODE_SPECIFIER))
        raise Exception('Invalid Input')

    puts(colored.green('Mode: ') + str(args[0]))
    if not re.match(MODE_SPECIFIER, args[0]):
        puts(colored.red('Invalid Mode. Valid input: %s' % MODE_SPECIFIER))
        raise Exception('Invalid Input')

    if re.match('^test$', args[0]):
        for tc in (HistoryTestCase, TransactionsTestCase, ExceptionsTestCase, CrashesTestCase, PerformanceTestCase,
                   AppLoadsTestCase, AppVersionsTestCase):
            suite = unittest.TestLoader().loadTestsFromTestCase(tc)
            unittest.TextTestRunner(verbosity=2).run(suite)
        exit()

    structured_args = {
        'mode': str(args[0]),
        'verbose': bool(len(all_args.flags.all_with('verbose'))),
    }

    create_tables()

    id_list = None
    if len(args) > 1:
        id_list = args[1:]
        puts(colored.blue('Ids: ') + id_list)
        structured_args['ids'] = id_list

    if structured_args['mode'] == 'upload':
        logging.getLogger().info('Beginning Upload app_ids=%s', id_list)
        nrc = NewRelicClient(NR_ACCOUNT_ID, NR_INSERT_KEY)
        for app_id in id_list:
            dispatcher = ETLDispatcher(nrc, app_id)
            dispatcher.handle_etl()




