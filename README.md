# NewRelic Integration
## Setup

pip install -r requirements.txt

## Usage

`./new_relic_connector.py upload <app_id> [<app_id>...]`

### Environment Variables: 
#### Required:
* `CR_USERNAME` - Your Crittercism username 
* `CR_PASSWORD` - Your Crittercism password 
* `CR_CLIENT_ID` - Your Crittercism Client ID
* `NR_ACCOUNT_ID` - Your New Relic account ID 
* `NR_INSERT_KEY` - Your New Relic Secret Insert Key 

#### Optional:
* `DATA_ACTION=debug|upload` - Defaults=upload. debug will just output a random sample of events to log instead of uploading to new relic. 
* `LOOKBACK_MINUTES` - Default=15. Number of minutes to look back. See below for details. Recommended value=15. 

#### Examples:

`CR_USERNAME=<username> CR_PASSWORD=<pw> CR_CLIENT_ID=<client_id> NR_ACCOUNT_ID=<nr_account_id> NR_INSERT_KEY=<nr_key> ./new_relic_connector.py upload <app_id> [<app_id>...]` 

##### Dry run with no upload:

`DATA_ACTION=debug CR_USERNAME=<username> CR_PASSWORD=<pw> CR_CLIENT_ID=<client_id> NR_ACCOUNT_ID=<nr_account_id> NR_INSERT_KEY=<nr_key> ./new_relic_connector.py upload <app_id> [<app_id>...]`

## Overview

### 5 data pipelines being ingested
1. Performance 
2. Exceptions
3. Crashes
4. App Loads
5. Transactions

### Ingestion Flow
1. Retrieve data from the Crittercism API
1. Translate it into a list of Events
1. Upload them in bulk to New Relic.
    * New Relic upload supports up to 1000 events per upload.

### Data In/Data Out
1. Performance data becomes Mobile events
1. Exceptions data becomes Exception events
1. Crashes data becomes Crash events
1. App Loads data becomes `App Load` events
1. Transactions data becomes Transaction events

## Data Downloading
LOOKBACK_MINUTES can be specified as an environment variable. If not, it defaults to 15.

### Performance
Performance data is queried with the lookback minutes specified. If that is not a valid lookback, it defaults to 15.
We query the following metrics:

1. errors
1. dataOut
1. dataIn
1. latency

Grouped By:

1. appVersion
1. os
1. carrier
1. device
1. service

By querying all of these permutations, we can discern how to form individual "Performance" events that result in an aggregate that matches what we queried from Crittercism.

### Exceptions

Exception data is only available as an aggregate. 
In other words, when we query exceptions, we only receive an aggregate of counts of all exception types that are known. 
We can filter this by restricting the time when it first occurred or last occurred.
We filter it to only include exceptions that LAST occurred in the lookback period. 
This means if exceptions didn't occur in the lookback period, they will not be returned. 
This saves us work, for knowing that it hasn't occurred since we last ran the script means there's nothing new to upload.
However, when we find exceptions, the aggregate data returned by Crittercism is for ALL TIME, not just the lookback period. 
In other words, we are being more efficient by filtering to the lookback period, but we need to do bookkeeping to 
only upload deltas of counts of exceptions, thereby ensuring we don't double upload to New Relic.

Implications:

    * Even if there was only one occurrence of the exception in the lookback period, we will upload as many as we think we are lacking.
    * Example 1: 
        * Exception A has occurred 200 times a year ago before the script was ever run.
        * Exception A occurs once in the last 15 minutes. 
        * When we query the API, we see that Exception A has occurred 201 times.
        * We check the database, and we have never uploaded this exception to New Relic.
        * We upload 201 events of this type to New Relic.
    * Example 2:
        * Exception B has occurred 20 times since we have been running the script. 
        * The server fails and the script doesn't run for a week.
        * Exception B occurs 100 times the week that the script is not running. 
        * The script is re-deployed and is now running correctly. 
        * Exception B does not happen for another 2 weeks. 
        * We still have not uploaded the missing Exception B events to New Relic.
        * Exception B happens once again.
        * When we query the API, we see that Exception B has occurred 121 times.
        * We check the database, and we have uploaded 20 to New Relic before.
        * We upload 101 events of this type to New Relic.
            * These 101 events will have a timestamp in the query range, which will not correspond to the actual time they occurred. This is unavoidable because we do not have access to detailed records.

### Crashes
Crashes and Exceptions have similar schemas in Crittercism, and we treat them the same way. The methodology, bookkeeping, and implications are identical.
 
### Transactions
Transactions data can be queried as detailed (trace) data with a specific lookback. 
We take advantage of this and only upload that. We do not bookkeep. 
If the script is run on a regular interval supported by Crittercism, this should work well.
 
### App Loads
App Load data is only available as an aggregate. 
No matter which lookback we try to query, we always receive the last completed UTC day's worth of data. 
We bookkeep to make sure we don't upload it twice.

Implications:

    It's likely that all of the App Load data will be uploaded once per day to New Relic. Other runs of the script will not upload App Loads.
 
## Bookkeeping 
We use sqlite3 to do some local bookkeeping for data consistency.

Why sqlite3? 

* Because we don't want to require users of the script to have any database servers running. This script should work out of the box.

What do we store?

* Exceptions
    * Exceptions are only available split by app version as an all-time cumulative total. 
    * We store the running total uploaded so far in the error_history with the error_type='Exception'
* Crashes
    * Crashes are only available split by app version as an all-time cumulative total. 
    * We store the running total uploaded so far in the error_history with the error_type='Crash'
* App Loads
    * App Loads are only available as a daily total. 
    * In order to make sure we don't double upload, we store the number we've already uploaded for each date.
    * We store the running total uploaded so far in the app_load_history with the start_date and end_date.

What don't we store?

* Performance data

* Transactions data
    * The transactions API allows us to query for more flexible units of time. This makes it so that we don't need to keep track.
