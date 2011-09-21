# coding=utf-8

import re

#--------------------------------------------------------------------------------#

def mk_proper_fn(instr=None):
  '''
  Converts input string into a proper file/dir name (no blanks, parentheses or single quotes).
    instr = input string
  '''

  pdir = { ' ':'_', # blanks to underscores
           '/':'',  # remove slashes
           '(':'',  # remove parentheses
           ')':'',  # remove parentheses
           "'":'',  # remove single quotes
           '"':'',  # remove double quotes
           "¿":'',  # remove opening question marks
           "?":'',  # remove closing question marks
           "¡":'',  # remove opening exclamation marks
           "!":'',  # remove closing exclamation marks
           "&":'N', # substitute ampersands for N 
           ",":'',  # remove commas
	   }

  fn = ''
  for c in instr:
      if c in pdir:
          fn += pdir[c]
      else:
          fn += c

  return fn

#--------------------------------------------------------------------------------#

def mk_proper_utf(instr=None):
  '''
  Converts input string into a proper UTF string. Strings can be "Str" or "Unicode", and if
  Str, they can have different encodings. Some apps return a string containing accents or 
  other non-ASCII chars, but are labeled by Python as a plain ASCII Str. You can not transform 
  them to Unicode, because being ASCII they contain non-ASCII chars. OTOH, you can not use them
  as directly as Unicode because they are Str.

  This function tries to fix it, generating a proper UTF-8-encoded Str.
    instr = input string
  '''

  trdir = { 
            161:"¡",
            180:"'",
	    186:'º',
            191:'¿',
            193:'Á',
            196:'Ä',
            201:'É',
            203:'Ë',
            205:'Í',
            207:'Ï',
            209:'Ñ',
            211:'Ó',
            214:'Ö',
            218:'Ú',
            220:'Ü',
            224:'à',
            225:'á',
	    227:'ã',
            228:'ä',
	    231:'ç',
	    232:'è',
            233:'é',
	    234:'â',
            235:'ë',
            237:'í',
            239:'ï',
            241:'ñ',
            243:'ó',
            246:'ö',
            250:'ú',
	    251:'û',
            252:'ü',
            }

  ord2char = { 
               56545:'á',
               56553:'é',
               56557:'í',
               56561:'ñ',
               56563:'ó',
             }

  utfout = ''

  try:
      utfout = instr.encode('utf-8')
      utfout = utfout.decode("utf-8")

  except:
    try:
        utfout = instr.decode('ascii')

    except:
        try:
           utfout = instr.decode('utf-8')

        except:
          for c in instr:
            oc = ord(c)
            if oc in trdir:
                utfout += trdir[oc]
            else:
                if oc < 128:
                    utfout += c
                elif oc in ord2char:
                    utfout += ord2char[oc]
                else:
                    utfout += '#'
                    string = "\n\033[31m%\n% DataManipulation.mk_proper_utf:"
                    string += " char with ord "
                    string += str(oc)+" was found (substituted for an #):\n%\033[0m "
                    string += utfout+"\n\033[31m%\033[0m\n"

  return utfout.encode('utf-8')

#------------------------------------------------------------------------------------------#

def get_ftype(fname):
  '''
  Given a file, it determines the type (Gaussian input, Siesta output...).
    fname = file name to check
  '''

  # Audio:
  if re.search('\.mp3$',fname):
    ftype = 'mp3'

  elif re.search('\.ogg$',fname):
    ftype = 'ogg'

  # Video:

  elif re.search('\.mpe?g$',fname):
    ftype = 'mpg'

  # Other:
  else:
    f = myopen(fname)

    ftype = 'xyz' # default type

    for line in f:
      if re.search('fdfstring',line):
        ftype = 'fdf'
        break
    
      elif re.search('\*  WELCOME TO SIESTA  \*',line):
        ftype = 'siestalog'
        break
    f.close()

  return ftype

#--------------------------------------------------------------------------------#
