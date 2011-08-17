#!/usr/bin/python2
# coding=utf-8

'''
ogg2mp3
(c) 2008-2011, Iñaki Silanes

LICENSE

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License (version 2), as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details (http://www.gnu.org/licenses/gpl.txt).

DESCRIPTION

Converts OGG filse to MP3, and the other way around. Transfers tags if present.

USAGE

% ogg2mp3 [options] file-or-dir

for options:

% ogg2mp3 -h 
'''

import os
import sys
import copy
import glob
import optparse
import System as S
import DataManipulation as DM
import MusicManipulation as MM

#------------------------------------------------------------------------------------------#

dmf = DM.mk_proper_fn
dmu = DM.mk_proper_utf
cdc = copy.deepcopy

#------------------------------------------------------------------------------------------#

# Read arguments:
parser = optparse.OptionParser()

parser.add_option("-d", "--dir",
                  dest="dir",
                  help="Output directory. Default: present directory.",
                  default=".")

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
                  help="Dry run: do nothing, just tell what would be done. Implies --verbose. Default: real run.",
		  action="store_true",
                  default=False)

parser.add_option("-n", "--name",
                  help="Build output file name from input filename. Default: build it from tracknum and title.",
		  action="store_true",
                  default=False)

parser.add_option("-q", "--quality",
                  help="Output quality. Default: 7.",
                  default=7)

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

def afu(ins_str=None):
    out_str = dmf(ins_str)
    out_str = dmu(out_str)
    
    return out_str

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
          print('Including {0}'.format(li))
      else:
          if o.verbose:
              fmt = 'Neglecting {0} because extension does not match required one ({1})'
              print(fmt.format(li,iext))

#------------------------------------------------------------------------------------------#

# Process files in list one by one:
for f in listout:

  # Get ID3 tags from input file
  tags = MM.ID3read(f)

  # Generate output filename/dir from input:
  af = f.split('/')

  if o.name:
    baseout = af[-1].replace('.'+iext,'')

  else:
    try:
      tn = int(tags['tracknumber'])
    except:
      tn = 1

    try:
      st = afu(tags['title'])
    except:
      st = 'unknown'

    baseout = '%02i-%s' % (tn,st)

  baseout = dmf(baseout)

  if o.flat:
    baseout = '%s/%s' % (o.dir,baseout)

  else:

    try:
      artist = afu(tags['artist'])
    except:
      artist = 'unknown_artist'

    try:
      album = afu(tags['album'])
    except:
      album = 'unknown_album'

    try:
      year = int(tags['date'])
    except:
      year = 1000

    outdir = '%s/%s/%04i-%s' % (o.dir,artist,year,album)
    if type(outdir) is unicode:
      outdir = outdir.encode('utf-8')

    if not o.dryrun and not os.path.isdir(outdir):
      os.makedirs(outdir)

    baseout = '%s/%s' % (outdir,baseout)

  if o.verbose:
      print('IN:  {0}'.format(f))
      print('WAV: {0}.wav'.format(baseout))
      print('OUT: {0}.{1}'.format(baseout,oext))
      print('')

  # Produce WAV:
  if o.reverse:
    # MP3 --> WAV
    cmnd = 'mpg123 -w "%s.wav" "%s"' % (baseout,f)

  else:
    # OGG --> WAV
    cmnd = 'oggdec "%s" -o "%s.wav"' % (f,baseout)

  if o.verbose:
      print(cmnd)

  if not o.dryrun:
    S.cli(cmnd)
  
  # Encode WAV to OGG or MP3:
  if o.reverse:
      # WAV --> OGG (and delete WAV)
      fmt = 'oggenc -q {0} "{1}.wav" -o "{1}.{2}" && rm -f "{1}.wav"'
      cmnd = fmt.format(o.quality, baseout, oext)

  else:
    # WAV --> MP2 (and delete WAV)
    cmnd = 'lame --vbr-new -V 0 "%s.wav" "%s.%s" && rm -f "%s.wav"' % (baseout,baseout,oext,baseout)

  if o.verbose:
      print(cmnd)

  if not o.dryrun:
    S.cli(cmnd)

  # Insert correct ID3 tags into output MP3:
  for t in tags:
      t  = t.lower()
      if not o.dryrun:
          MM.ID3write('%s.%s' % (baseout,oext),t,tags[t])

      if o.verbose:
          val = tags[t]
          if type(val) == type(u''):
              val = val.encode('utf-8')
          print("Tagging {0:16s} : {1}".format(t, val))
