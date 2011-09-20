# coding=utf-8
'''
Perform various operations related to music files, like ID3 tagging and reading.
'''

import re
import sys
import eyeD3
import subprocess as sp
import o2m.core as Core

#------------------------------------------------------------------------------------------#

def ID3read(fname,ftype=None):
  '''
  Read ID3 tags from file, and return dictionary with data.
    fname = name of file to read
  '''

  dic = {}

  if not ftype:
      ftype = Core.get_ftype(fname)

  if ftype == 'mp3':
    tag = eyeD3.Tag()
    test = tag.link(fname) # link to file, and btw test if has ID3 tags
    if test:
      try:
          dic['artist'] = tag.getArtist()
      except:
          pass

      try:
          dic['album'] = tag.getAlbum()
      except:
          pass

      try:
          dic['title'] = tag.getTitle()
      except:
          pass
        
      try:
          dy = tag.getYear()
          dy = int(dy)
          dic['date'] = dy
      except:
          pass

      try:
          dg = tag.getGenre()
          dg = str(dg)
          dg = re.sub('[0-9()]','',dg)
          dic['genre'] = dg
      except:
          pass

      try:
          dt = tag.getTrackNum()
          if type(dt) is tuple:
              dt = dt[0]
              dic['tracknumber'] = dt
      except:
          pass

    else:
        print('Warning, file "{0}" has no ID3 tags!'.format(fname))

  elif ftype == 'ogg':
    cmnd = 'vorbiscomment "%s"' % (fname)
    s = sp.Popen(cmnd, stdout=sp.PIPE, shell=True)
    data = s.communicate()[0].split('\n')
    for line in data:
      line   = line.replace('\n','')
      aline  = line.split('=')

      try:
          key = aline[0].lower()
      except:
          fmt  = 'ID3read: something wrong with some tag in file "{0}".'
          fmt += ' Run "vorbiscomment" or "tagtool" on it to diagnose.'
          string = fmt.format(fname)
          sys.exit(string)

      try:
          val = aline[1]
      except:
          val = 'unknown'

      dic[key] = val

  else:
      sys.exit('ID3read: don\'t know how to process a file of type "%s"' % (ftype))

  return dic

#------------------------------------------------------------------------------------------#

def ID3write(fname,tname,tval,version=eyeD3.ID3_V2_3):
  '''
  Give some value to some ID3 tag in a MP3/OGG file.
    fname = file to edit
    tname = tag name
    tval  = tag value to asign to tname
  '''

  ftype = Core.get_ftype(fname)

  if ftype == 'mp3':
    # Check that file DOES have ID3 tags. If not, create ID3v2.3 header
    # (eyeD3 procedures below fail if there is no ID3 tag beforehand)
    tag  = eyeD3.Tag()
    test = tag.link(fname)

    if not test:
       tag.header.setVersion(eyeD3.ID3_V2_3)

    # Try to modify it:
    try:
      tval = tval.decode('utf8')
  
      try:
        if tname == 'artist':
          tag.setArtist(tval)
  
        elif tname == 'album':
          tag.setAlbum(tval)
  
        elif tname == 'title':
          tag.setTitle(tval)
        
        elif tname in "date year":
          tag.setDate(int(tval))
        
        elif tname == 'genre':
          tag.setGenre(tval.encode('latin-1'))
        
        elif tname == 'tracknumber':
            tag.setTrackNum((int(tval),None))
        
        elif tname in 'comment description':
          tag.addComment(tval)
      
        elif tname == 'aartist':
          tag.addComment('AARTIST=%s' % (tval))
      
        tag.update(version)

      except:
        sys.exit('Could not modify ID3 tags, sorry (maybe you don\'t have package "eyeD3" installed?).')
 
    except:
        print('Don\'t know how to handle tag named "{0}"! (ignoring)'.format(tname))

  elif ftype == 'ogg':
    mydic = ID3read(fname)
    mydic[tname] = tval

    tagstr = ''
    for tag in mydic:
      mt = mydic[tag]
      if type(mt) is unicode:
        mt = mt.encode('utf-8')

      tagstr += ' -t "%s=%s" ' % (tag,mt)

    cmnd = 'vorbiscomment -w %s %s' % (tagstr,fname)
    s = sp.subprocess(cmnd, shell=True)
    s.communicate()

#------------------------------------------------------------------------------------------#

