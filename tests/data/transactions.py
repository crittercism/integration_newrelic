TRANSACTIONS_DETAILS_DATA = [{
    u'groups': [
        {u'name': 'bogusName1', u'link': 'bogusLink1'},
        {u'name': 'bogusName2', u'link': 'bogusLink2'},
        {u'name': 'bogusName3', u'link': 'bogusLink3'},
        {u'name': 'bogusName4', u'link': 'bogusLink4'},
    ]
}]

TRANSACTIONS_GROUPS_DATA = {
    'bogusLink1/traces/PT8008M' : [
        { u'traces': [
            {
                u'username': 'bogusUsername1',
                u'traceTs': '2011-09-02T12:12:12.000Z',
                u'breadcrumbCount': 0,
                u'foregroundSeconds': 300,
                u'appVersion': 'bogusAppVersion1',
                u'valueAtRisk': 100.73,
                u'device': 'bogusDevice1',
                u'os': 'bogusOS1',
                u'id': '23423',
                u'completionState': 'crashed',
            },
            {
                u'username': 'bogusUsername1.2',
                u'traceTs': '2011-09-02T12:12:12.000Z',
                u'breadcrumbCount': 0,
                u'foregroundSeconds': 300,
                u'appVersion': 'bogusAppVersion1.2',
                u'valueAtRisk': 100.73,
                u'device': 'bogusDevice1.2',
                u'os': 'bogusOS1',
                u'id': '23424',
                u'completionState': 'crashed',
            },
            ]
        }
    ],
    'bogusLink2/traces/PT8008M': [
        {u'traces': []
        }
    ],
    'bogusLink3/traces/PT8008M': [
        {u'traces': [
            {
                u'username': 'bogusUsername3',
                u'traceTs': '2011-09-03T12:12:12.000Z',
                u'breadcrumbCount': 0,
                u'foregroundSeconds': 3,
                u'appVersion': 'bogusAppVersion3',
                u'valueAtRisk': 19900.73,
                u'device': 'bogusDevice3',
                u'os': 'bogusOS3',
                u'id': '9',
                u'completionState': 'success',
            },
        ]
        }
    ],
    'bogusLink4/traces/PT8008M': [
        {u'traces': [
            {
                u'username': 'bogusUsername1',
                u'traceTs': '2011-09-02T12:12:12.000Z',
                u'breadcrumbCount': 0,
                u'foregroundSeconds': 300,
                u'appVersion': 'bogusAppVersion1',
                u'valueAtRisk': 100.73,
                u'device': 'bogusDevice1',
                u'os': 'bogusOS1',
                u'id': '666',
                u'completionState': 'crashed',
            },
            {
                u'username': 'bogusUsername1',
                u'traceTs': '2011-09-02T12:13:12.000Z',
                u'breadcrumbCount': 6,
                u'foregroundSeconds': 6,
                u'appVersion': 'bogusAppVersion1',
                u'valueAtRisk': 6.66,
                u'device': 'bogusDevice1',
                u'os': 'bogusOS1',
                u'id': '6666',
                u'completionState': 'crashed',
            },
            {
                u'username': 'bogusUsername1',
                u'traceTs': '2011-09-02T12:14:12.000Z',
                u'breadcrumbCount': 6,
                u'foregroundSeconds': 6,
                u'appVersion': 'bogusAppVersion1',
                u'valueAtRisk': 6.66,
                u'device': 'bogusDevice1',
                u'os': 'bogusOS1',
                u'id': '66666',
                u'completionState': 'crashed',
            },
            {
                u'username': 'bogusUsername1',
                u'traceTs': '2011-09-02T12:15:12.000Z',
                u'breadcrumbCount': 6,
                u'foregroundSeconds': 6,
                u'appVersion': 'bogusAppVersion1',
                u'valueAtRisk': 6.66,
                u'device': 'bogusDevice1',
                u'os': 'bogusOS1',
                u'id': '66666',
                u'completionState': 'crashed',
            },
        ]
        }
    ],
}