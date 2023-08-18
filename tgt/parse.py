#!/usr/bin/env python3

import ply.lex as lex
import ply.yacc as yacc
import tgt


# Tokenizer

tokens = [
    'NUMERIC',
    'FILETYPE',
    'EQ',
    'QUOTED_STRING',
    'VAR',
    'SIZE',
    'ITEM_TAG',
    'ANNOTATION_TAG'
]

t_FILETYPE = r'File\stype\s=\s"ooTextFile"\nObject\sclass\s=\s"TextGrid"'
t_EQ = '='
t_NUMERIC = r'\d+(\.\d+)?'
t_VAR = r'\w+'
t_ignore  = '\n\t '
t_ignore_EXISTS = r'(tiers\?\s+)?<exists>'
t_ITEM_TAG = r'item\s+\[\d*\]:'
t_ANNOTATION_TAG = r'(intervals|points)\s+\[\d*\]:'


def t_SIZE(t):
    r'((intervals|points):\s+)?size'
    t.value = 'size'
    return t
    

def t_QUOTED_STRING(t):
    r'("[^"]*")|(\'[^[\']*\')'
    t.value = t.value.strip('\n\"\'')
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Grammar

def p_textgrid(p):
    'tier : textgrid_header tiers_list'

    p[0] = tgt.TextGrid()
    p[0].add_tiers(p[2])

def p_textgrid_header(p):
    '''textgrid_header : FILETYPE assignments_list ITEM_TAG
                       | FILETYPE NUMERIC NUMERIC NUMERIC'''
    if isinstance(p[2], dict):
        p[0] = {'start_time': tgt.Time(p[2]['xmin']), 'end_time': tgt.Time(p[2]['xmax']),
                'n_tiers': int(p[2]['size'])}
    else:
        p[0] = {'start_time': tgt.Time(p[2]), 'end_time': tgt.Time(p[3]), 'n_tiers': int(p[4])}

def p_tiers_list(p):
    '''tiers_list : tiers_list tier_long
                  | tiers_list tier_short
                  | tier_long
                  | tier_short'''

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])

# Long tiers
    
def p_tier_long(p):
    '''tier_long : tier_header_long annotations_list_long'''
    tier_type = p[1]['class']
    if tier_type == 'IntervalTier':
        p[0] = tgt.IntervalTier(name=p[1]['name'])
        for annot in p[2]:
            p[0].add_interval(tgt.Interval(tgt.Time(annot['xmin']), tgt.Time(annot['xmax']), annot['text']))
    elif tier_type == 'TextTier':
        p[0] = tgt.PointTier(name=p[1]['name'])
        for annot in p[2]:
            p[0].add_point(tgt.Point(tgt.Time(annot['number']), annot['mark']))
    else:
        ValueError('Unknown tier type: {}'.format(tier_type))

def p_tier_header_long(p):
    '''tier_header_long : ITEM_TAG assignments_list'''
    p[0] = p[2]

def p_annotations_list_long(p):
    '''annotations_list_long : annotations_list_long annotation_long
                             | annotation_long'''

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])

def p_annotation_long(p):
    '''annotation_long : ANNOTATION_TAG assignments_list'''
    p[0] = p[2]

def p_assignments_list(p):
    '''assignments_list : assignments_list assignment
                        | assignment'''

    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1]
        p[0].update(p[2])
    

def p_assigment(p):
    '''assignment : VAR EQ NUMERIC
                  | VAR EQ QUOTED_STRING
                  | SIZE EQ NUMERIC'''
    p[0] = {p[1]: p[3]}

# Short tiers

def p_tier_short(p):
    'tier_short : tier_header_short annotations_list_short'

    if p[1]['tier_type'] == 'IntervalTier':
        p[0] = tgt.IntervalTier(name = p[1]['tier_name'], objects = p[2])
    elif p[1]['tier_type'] == 'TextTier':
        p[0] = tgt.PointTier(name = p[1]['tier_name'], objects = p[2])
    else:
        raise ValueError('Unknown tier type: {}'.format(p[0][tier_type]))

def p_tier_header_short(p):
    'tier_header_short : QUOTED_STRING QUOTED_STRING NUMERIC NUMERIC NUMERIC'
    p[0] = {'tier_type': p[1], 'tier_name': p[2], 'start_time': tgt.Time(p[3]), 'end_time': tgt.Time(p[4]), 'n_annotations': int(p[5])}

def p_annotations_list_short(p):
    '''annotations_list_short : annotation_short annotations_list_short
                              | annotation_short'''
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = p[2]
    p[0].append(p[1])

def p_annotation_short(p):
    '''annotation_short : NUMERIC NUMERIC QUOTED_STRING
                        | NUMERIC QUOTED_STRING'''

    if len(p) == 4:
        p[0] = tgt.Interval(tgt.Time(p[1]), tgt.Time(p[2]), p[3])
    else:
        p[0] = p[0] = tgt.Point(tgt.Time(p[1]), p[2])


def p_error(p):
    print("Syntax error in input!")

# Test

def parse(path):
    

    with open(path) as f:
        tg = f.read()
    lexer = lex.lex()
    lexer.input(tg)

    parser = yacc.yacc()
    res = parser.parse(tg)

    for t in res:
        print(t)
        print()

parse('test_long.TextGrid')
parse('test_short.TextGrid')
