#!/usr/bin/env python3
#coding: utf-8

import argparse

def parse_clargs():
    P = argparse.ArgumentParser(description='generate tex for smx diagrams')
    P.add_argument('-i', '--image', help='one of {thread, block}', default='thread')

    return P.parse_args()

scale = 11
gpu_core_width=0.25*scale
shared_height=gpu_core_width
shared_height=gpu_core_width*2
gpu_space=0.2*scale

smx_height=8*(gpu_core_width) + shared_height
smx_width=8*(gpu_core_width)

def print_measurement(name, value):
    return '\\newcommand{\\' + name + '}{' + str(value) + 'mm}\n'

def print_header():
    text = ''

    text += print_measurement('gpucorewidth', gpu_core_width)
    text += print_measurement('gpucoreheight', gpu_core_width)
    text += print_measurement('sharedheight', shared_height)
    text += print_measurement('smxwidth', smx_width)

    node_description = r'''
\begin{document}
\begin{tikzpicture}[x=0mm, y=0mm, node distance=0 mm,outer sep = 0pt]
\tikzstyle{core}=[
    draw,
    rectangle,
    minimum height=\gpucoreheight,
    minimum width=\gpucorewidth,
    fill=green!50,
    anchor=north west]
\tikzstyle{coreidle}=[
    draw,
    rectangle,
    minimum height=\gpucoreheight,
    minimum width=\gpucorewidth,
    fill=white,
    anchor=north west]
\tikzstyle{shared}=[
    draw,
    rectangle,
    minimum height=\sharedheight,
    minimum width=\smxwidth,
    fill=yellow!60,
    anchor=north west]
\tikzstyle{gpucache}=[
    draw,
    rectangle,
    minimum height=\gpucacheheight,
    minimum width=\gpucachewidth,
    fill=blue!20,
    anchor=north west]
    '''

    text += node_description
    return text

def print_footer():

    return r'''
\end{tikzpicture}

\end{document}
'''

def print_node(i, j, pos, fill):
    if fill:
        return '\\node[core] (core' + str(i) + ') [' + pos + ' = of core' + str(j) + '] {};\n'
    else:
        return '\\node[coreidle] (core' + str(i) + ') [' + pos + ' = of core' + str(j) + '] {};\n'

def print_smx(smx_id, x, y, full_block):
    first_node = smx_id*64
    text = '\\node[core] (core' + str(first_node) + ') at(' + str(x) + 'mm,' + str(y) + 'mm) {};\n'
    for i in range(first_node+1,first_node+8):
        text += print_node(i, i-1, 'right', full_block)

    for i in range(1,8):
        text += '\n'
        text += str() + '\n'
        start = first_node + i*8
        text += print_node(start, start-8, 'below', full_block)
        for i in range(start+1,start+8):
            text += print_node(i, i-1, 'right', full_block)

    text += '\\node[shared] (memory) at(' + str(x) + 'mm,' + str(y-smx_height+shared_height) + 'mm) {\\bfseries \\tiny shared memory};\n\n'
    return text


#
#   main
#

args = parse_clargs()

txt =  print_header()

if args.image == 'thread':
    txt += print_smx(0,0,0,False)

elif args.image == 'block':
    txt += print_smx(0,0,0,True)

txt += print_footer()

print(txt)
