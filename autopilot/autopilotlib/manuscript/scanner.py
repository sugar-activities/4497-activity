# -*- coding: cp1252 -*-
# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


"""
A scanner that converts an instruction into lexical tokens

"""


#-----------------------------------------------------------------------
#
# Lexicaltoken ID's
#
#-----------------------------------------------------------------------
LP              = 1    # (
RP              = 2    # )
EQ              = 3    # =
PLUS            = 4    # +
COMMA           = 5    # ,
ID              = 6    # Identifier
KEYWORD         = 7    # Reserved word
SPACE           = 8    # Space character ' '
COMMENT         = 9    # character '#'
STRING          = 10
NUM             = 11
TAB             = 58   # Tab character '\t'
UNKNOWN         = 98
NA              = 99

#-----------------------------------------------------------------------
#
# Lexical token sub-ID's for Instruction reserved words
#
#-----------------------------------------------------------------------
ID_INCLUDE        = 100
ID_START          = 101
ID_APP            = 102
ID_EXIT           = 103
ID_COMMENT        = 104
ID_SELECT         = 105
ID_MENU           = 106
ID_CLICK          = 107
ID_BUTTON         = 108
ID_CLOSE          = 109
ID_FRAME          = 110
ID_HIDE           = 111
ID_DIALOG         = 112
ID_ENTER          = 113
ID_TEXT           = 114
ID_CUSTOMTREECTRL = 115
ID_MOUSE          = 116
ID_COMBOBOX       = 117

#-----------------------------------------------------------------------
#
# reserved words
#
#-----------------------------------------------------------------------
INSTRUCTION_KEYWORDS = [
    "include",
    "start",
    "application",
    "exit",
    "comment",
    "select",
    "menu",
    "click",
    "button",
    "close",
    "frame",
    "hide",
    "dialog",
    "enter",
    "text",
    "customtreecontrol",
    "mouse",
    "combobox",
]

INSTRUCTION_ALIASES = {
    "app"   : "application",
    "mnu"   : "menu",
    "btn"   : "button",
    "txt"   : "text",
    "ctctrl": "customtreecontrol",
}

#-----------------------------------------------------------------------
#
# Used to give the lexical token IDs a user friendly representation in
# error messages
#
#-----------------------------------------------------------------------
TOKENID_MAP = {

    LP              : "(",
    RP              : ")",
    EQ              : "=",
    PLUS            : "+",
    COMMA           : ",",
    COMMENT         : "#",
    ID              : "Identifier",
    SPACE           : "Space",
    TAB             : "Tab",
    KEYWORD         : "Keyword",
    STRING          : "String",
    NUM             : "Number",
    UNKNOWN         : "Unknown",
    NA              : "",
    ID_INCLUDE      : INSTRUCTION_KEYWORDS[ID_INCLUDE - ID_INCLUDE],
    ID_START        : INSTRUCTION_KEYWORDS[ID_START   - ID_INCLUDE],
    ID_APP          : INSTRUCTION_KEYWORDS[ID_APP     - ID_INCLUDE],
    ID_EXIT         : INSTRUCTION_KEYWORDS[ID_EXIT    - ID_INCLUDE],
    ID_SELECT       : INSTRUCTION_KEYWORDS[ID_SELECT  - ID_INCLUDE],
    ID_CLICK        : INSTRUCTION_KEYWORDS[ID_CLICK   - ID_INCLUDE],
    ID_CLOSE        : INSTRUCTION_KEYWORDS[ID_CLOSE   - ID_INCLUDE],
}

#-----------------------------------------------------------------------
#
# Names for ID:s
#
#-----------------------------------------------------------------------
ID_NAMES = {
    LP              : "LP",
    RP              : "RP",
    EQ              : "EQ",
    PLUS            : "PLUS",
    COMMA           : "COMMA",
    COMMENT         : "COMMENT",
    ID              : "ID",
    SPACE           : "SPACE",
    TAB             : "TAB",
    KEYWORD         : "KEYWORD",
    STRING          : "STRING",
    NUM             : "NUM",
    UNKNOWN         : "UNKNOWN",
    NA              : "NA",
}

#-----------------------------------------------------------------------
#
# Names for SubID:s
#
#-----------------------------------------------------------------------
SUBID_NAMES = {
    ID_INCLUDE        : "INCLUDE",
    ID_START          : "START",
    ID_APP            : "APPLICATION",
    ID_EXIT           : "EXIT",
    ID_COMMENT        : "COMMENT",
    ID_SELECT         : "SELECT",
    ID_MENU           : "MENU",
    ID_CLICK          : "SELECT",
    ID_BUTTON         : "MENU",
    ID_CLOSE          : "CLOSE",
    ID_FRAME          : "FRAME",
    ID_HIDE           : "HIDE",
    ID_DIALOG         : "DIALOG",
    ID_ENTER          : "ENTER",
    ID_TEXT           : "TEXT",
    ID_CUSTOMTREECTRL : "CUTSOMTREECTRL",
    ID_MOUSE          : "MOUSE",
    ID_COMBOBOX       : "COMBOBOX",
}

#-----------------------------------------------------------------------
#
# Global variables
#
#-----------------------------------------------------------------------
ID_SPECIAL_CHARS = ('_', '-', '.','å','ä','ö','Å','Ä','Ö', '&')
_line = 1
_col  = 0
_tab_count = 0

_print_unknown_only = True
_include_whitespace_tokens = False
_include_comment_tokens = False

class Token(object):
    """An object of this class represents an instruction lexical token"""

    def __init__(self, token_id, lexeme, subid=None, col=0):
        self.id     = token_id
        self.lexeme = lexeme
        self.subid  = subid
        self.col    = col

    def tostr(self, exclude_filename=False):
        """Return a string representation of a Token object"""

        if self.subid == None:
            subid = NA
        else:
            subid = self.subid

        return "id= %-16.16s subid= %-12.12s lexeme='%s' " % (TOKENID_MAP[self.id], TOKENID_MAP[subid], self.lexeme)


def scan_instruction(text):

    global _tab_count
    global _print_unknown_only
    global _first_char_on_line
    global _col

    prevcol = 1
    _tab_count = 0
    _col = 0

    text = text.strip()
    nbr_of_chars = len(text)
    i = 0
    nbr_of_unkown = 0
    tokens = []
    _first_char_on_line = ' '

    while i < nbr_of_chars:
        lexeme = "unknown"
        typename = "Unknown"
        token = UNKNOWN
        subid = None

        # Space
        if i == 0 and (text[i] == '#' or text[i] == ' '):
            lexeme = text
            typename = "Comment"
            token = Token(KEYWORD, text, ID_COMMENT, col=0)
            tokens.append(token)
            return tokens
        
        # Space
        elif text[i] == ' ':
            lexeme = " "
            typename = "Space"
            token = SPACE

        # Tab
        elif text[i] == '\t':
            lexeme = " "
            typename = "Tab"
            token = TAB
            _tab_count = _tab_count + 1

        # Left Parenthesis
        elif text[i] == '(':
            lexeme = "("
            typename = "Left Parenthesis"
            token = LP

        # Right Parenthesis
        elif text[i] == ')':
            lexeme = ")"
            typename = "Right Parenthesis"
            token = RP

        elif text[i] == '=':
            lexeme = "="
            typename = "Equal sign"
            token = EQ

        elif text[i] == '+':
            lexeme = "+"
            typename = "Plus sign"
            token = PLUS

        elif text[i] == ',':
            lexeme = ","
            typename = "Comma"
            token = COMMA

        elif text[i] == '"':
            lexeme, token, subid, i = _parse_string(text, i)
            typename = "String"
            _col = i + 1

        elif text[i].isalnum() or text[i] in ID_SPECIAL_CHARS:
            lexeme, token, subid, i = _parse_identifier(text, i)
            typename = "Identifier"
            _col = i + 1

        # Unknown token
        else:
            if text[i].isspace():
                lexeme = " "
                typename = "Space"
                token = SPACE
            else:
                nbr_of_unkown = nbr_of_unkown + 1
                lexeme = "%c" % text[i]

        i += 1
        _col += 1

        #Print result
        if _print_unknown_only:
            if (token == UNKNOWN):
                msg = "%d %d %s %s" % (i, token, typename, lexeme)
                print msg

        if typename != "Space":
            token = Token(token, lexeme, subid, col=prevcol)
            tokens.append(token)
        prevcol = _col

    if nbr_of_unkown > 0:
        msg = "Nbr of unknown tokens encountered = %d" % nbr_of_unkown
        print msg

    return tokens

#-----------------------------------------------------------------------
#
# _parse_identifier
#
#-----------------------------------------------------------------------
def _parse_identifier(text, i):

    # Collection of all characters that belongs to the identifier
    collector = []
    maxlength = len(text)
    # Parse
    while i < maxlength and (text[i].isalnum() or text[i] in ID_SPECIAL_CHARS):
        collector.append((text[i]))
        i += 1

    # Create a string from the collector
    identifier = "".join(collector)

    # Reserved word ?
    if identifier.lower() in INSTRUCTION_ALIASES.keys():
        identifier = INSTRUCTION_ALIASES[identifier.lower()] 
    if identifier.lower() in INSTRUCTION_KEYWORDS:
        identifier = identifier.lower() 
        token = KEYWORD
        subid = ID_INCLUDE + INSTRUCTION_KEYWORDS.index(identifier)
    else:
        if is_number(identifier):
            token = NUM
        else:
            token = ID
        subid = None

    # Return string and index of last character in identifier
    return identifier, token, subid, i - 1

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def _parse_string(text, i):
    inx = text.find('"', i + 1)
    if inx < 0:
        return text, STRING, None, len(text) - 1
    else:    
        return text[i:inx+1], STRING, None, inx


def print_tokens(tokens):
    print "Nbr of tokens = %d:\n" % len(tokens)

    for token in tokens:
        print token.tostr()
