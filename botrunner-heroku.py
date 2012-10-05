import logging
import time
import sys
import redisconnector
import random
import twitterconnector


## log to stdout, get caught by heroku's log service
logging.basicConfig( 
    stream=sys.stdout, 
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)8s %(name)s - %(message)s', 
    datefmt='%H:%M:%S' 
) 

## set up redis
redis = redisconnector.get_redis()

# run bot every run_interval seconds
nextrun_key = 'NextRun'
nextrun = None
try:
    nextrun = redis.get( nextrun_key )
    logging.info( "nextrun=%d" % nextrun )
except Exception as e:
    logging.info( e )

now = time.time()
if (not nextrun) or (now >= long(nextrun)):
    logging.info( "Running mundanebond..." )
    
    fh = open( 'lines.txt' )
    lines = fh.read().splitlines()
    line = random.choice( lines )

    tc = twitterconnector.TwitterConnector( creds_path="twitter_creds" )
    tc.tweet( line )

    hours = random.randrange( 1, 4 )
    nextrun = (60 * 60 * hours) - 10  # make sure we will run on the hour, set deadline a few seconds before.
    try:
        redis.set( nextrun_key, "%d" % nextrun )
    except Exception as e:
        logging.info( e )
else:
    logging.info( "Not due yet, now=%s and nextrun=%s" % (now,nextrun) )
