import random
# read all lines into a list, pick one
fh = open( 'lines.txt' )
lines = fh.read().splitlines()
random.shuffle( lines )

lines_out = "\n".join( lines )
fo = open( "lines_shuffled.txt", "w" )
fo.write( lines_out )
fo.close()