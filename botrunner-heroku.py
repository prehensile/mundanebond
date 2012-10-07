import logging
import time
import sys
import redisconnector
import random
import twitterconnector
import datetime

## log to stdout, get caught by heroku's log service
logging.basicConfig( 
    stream=sys.stdout, 
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)8s %(name)s - %(message)s', 
    datefmt='%H:%M:%S' 
) 

## set up redis
redis = redisconnector.get_redis()

# get the next due timestamp
nextrun_key = 'NextRun'
nextrun = None
lineptr_key = 'LinePtr'
line_ptr = None
try:
    nextrun = redis.get( nextrun_key )
    line_ptr = redis.get( lineptr_key )
except Exception as e:
    logging.info( e )
if line_ptr is None:
    line_ptr = 330
else:
    line_ptr = int( line_ptr )
    line_ptr += 1

POST_CHANCE = 1
SLEEP_START_HOUR = 22
SLEEP_END_HOUR = 8

override_nextrun = len(sys.argv) > 1 and sys.argv[1] == "override_nextrun"

now = time.time()
if override_nextrun or (not nextrun) or (now >= long(nextrun)):
    logging.info( "Running mundanebond..." )
    
    if random.random() > POST_CHANCE:
        # chance not met
        logging.info( "POST_CHANCE (%2.1f) not met." % POST_CHANCE )    
    else:

        # read all lines into a list, get the next one
        fh = open( 'lines_shuffled.txt' )
        lines = fh.read().splitlines()
        if line_ptr >= len(lines):
            line_ptr = 0
        line = lines[ line_ptr ]
        
        # tweet
        tc = twitterconnector.TwitterConnector( creds_path="twitter_creds" )
        tc.tweet( line )
        logging.info( "Tweet: %s" % line )

    ## set next tweet time
    hours = random.randrange( 2, 8 )
    delta = datetime.timedelta( hours=hours )
    delta -= datetime.timedelta( minutes=2 )  # make sure we will run on the actual hour, set time a couple of minutes before.
    dt_now = datetime.datetime.now()
    dt_nextrun = dt_now + delta

    # move next run times during sleep hours to the next day
    nexthour = dt_nextrun.hour
    sleep_length = (24 - SLEEP_START_HOUR) + SLEEP_END_HOUR
    if (nexthour > SLEEP_START_HOUR) or (nexthour < SLEEP_END_HOUR):
        # offset by sleep time, move to next morning
        dt_nextrun += datetime.timedelta( hours=sleep_length )

    # store next run time as timestamp
    nextrun = time.mktime( dt_nextrun.timetuple() )
    logging.info( "Next run at %s, will store %d" % (dt_nextrun,nextrun) )
    try:
        redis.set( nextrun_key, "%d" % nextrun )
        redis.set( lineptr_key, "%d" % line_ptr )
    except Exception as e:
        logging.info( e )
else:
    dt_nextrun = datetime.datetime.fromtimestamp( float(nextrun) )
    logging.info( "Not due yet, now=%s and nextrun=%s (%s)" % (now,nextrun,dt_nextrun) )
