#!/usr/bin/python
# coding=utf-8

# Convert OGG file to MP2 (renamed to .mp3).

import copy
import glob
import optparse
import os
import sys

import DataManipulation as DM
import FileManipulation as FM
import System as S

dmf = DM.mk_proper_fn
dma = DM.mk_proper_ascii
cdc = copy.deepcopy

#------------------------------------------------------------------------------------------#

# Read arguments:
parser = optparse.OptionParser()

parser.add_option("-d", "--dir",
                  dest="dir",
                  help="Output directory. Default: ~/Downloads.",
                  default="/home/isilanes/Downloads")

parser.add_option("-f", "--flat",
                  dest="flat",
                  help="Output flat, that is, do not create $author/$album/ dirs inside output dir. Default: do create.",
		  action="store_true",
                  default=False)

parser.add_option("-v", "--verbose",
                  dest="verbose",
                  help="Whether to be verbose. Default: don\'t be.",
		  action="store_true",
                  default=False)

parser.add_option("-r", "--reverse",
                  help="Do the reverse: from MP3 to OGG. Default: convert OGG to MP3.",
		  action="store_true",
                  default=False)

parser.add_option("-y", "--dryrun",
                  help="Dry run: do nothing, just tell what would be done. Default: real run.",
		  action="store_true",
                  default=False)

(o,args) = parser.parse_args()

#------------------------------------------------------------------------------------------#

# Check destination dir:
if not os.path.isdir(o.dir):
  sys.exit('Directory "%s" does not exist!' % (o.dir))

# If dry run, be verbose:
if o.dryrun:
  o.verbose = True

if o.reverse:
  iext = 'mp3'
  oext = 'ogg'
else:
  iext = 'ogg'
  oext = 'mp3'

#------------------------------------------------------------------------------------------#

# Get file list from argument list:
listin  = []
listout = args

there_are_dirs = True
while there_are_dirs:
  there_are_dirs = False
  listin         = cdc(listout)
  listout        = []

  for li in listin:
    if os.path.isdir(li):
      there_are_dirs = True
      cont = glob.glob('%s/*' % (li))
      listout.extend(cont)

    elif os.path.isfile(li):
      if '.%s' % (iext) in li:
        listout.append(li)

        if o.verbose:
          print 'Including %s' % (li)
      else:
        if o.verbose:
          print 'Neglecting %s' % (li)

#------------------------------------------------------------------------------------------#

# Process files in list one by one:
for f in listout:

  # Get ID3 tags from input file
  tags = FM.ID3read(f)

  # Generate output filename/dir from input:
  af   = f.split('/')

  if o.reverse:
    baseout = af[-1].replace('.mp3','')

  else:
    baseout = af[-1].replace('.ogg','')

  baseout = dma(baseout)
  baseout = dmf(baseout)

  if o.flat:
    baseout = '%s/%s' % (o.dir,baseout)

  else:
    try:
      artist = dma(tags['artist'])
      artist = dmf(artist)
    except:
      artist = 'unknown_artist'

    try:
      album = dma(tags['album'])
      album = dmf(album)
    except:
      album = 'unknown_album'

    try:
      year = int(tags['date'])
    except:
      year = 1000

    outdir = '%s/%s/%04i-%s' % (o.dir,artist,year,album)

    if not o.dryrun and not os.path.isdir(outdir):
      os.makedirs(outdir)

    baseout = '%s/%s' % (outdir,baseout)

  if o.verbose:
    print 'IN:  %s' % (f)
    print 'WAV: %s.wav' % (baseout)
    print 'OUT: %s.%s' % (baseout,oext)
    print ''

  # Produce WAV:
  if o.reverse:
    # MP3 --> WAV
    cmnd = 'mp3-decoder "%s" -w "%s.wav"' % (f,baseout)

  else:
    # OGG --> WAV
    cmnd = 'oggdec "%s" -o "%s.wav"' % (f,baseout)

  if o.verbose:
    print cmnd

  if not o.dryrun:
    S.cli(cmnd)
  
  # Encode WAV to OGG or MP3:
  if o.reverse:
    # WAV --> OGG (and delete WAV)
    cmnd = 'oggenc -q 7 "%s.wav" -o "%s.%s" && rm -f "%s.wav"' % (baseout,baseout,oext,baseout)

  else:
    # WAV --> MP2 (and delete WAV)
    cmnd = 'lame --vbr-new -V 0 "%s.wav" "%s.%s" && rm -f "%s.wav"' % (baseout,baseout,oext,baseout)

  if o.verbose:
    print cmnd

  if not o.dryrun:
    S.cli(cmnd)

  # Insert correct ID3 tags into output MP3:
  for t in tags:
    t  = t.lower()
    if not o.dryrun:
      FM.ID3write('%s.%s' % (baseout,oext),t,tags[t])

    if o.verbose:
      print "Tagging %16s : %s" % (t,tags[t])
