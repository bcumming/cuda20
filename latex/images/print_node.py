#!/usr/bin/env python2
#coding: utf-8

import argparse

def parse_clargs():
    P = argparse.ArgumentParser(description='generate tex for node diagram')
    P.add_argument('-m', '--managed', action='store_true',
                   help='print managed memory')

    return P.parse_args()

scale = 11
cpu_core_width=2*scale
gpu_core_width=0.25*scale
shared_height=gpu_core_width
l2_height=0.4*scale
gpu_cache_height=cpu_core_width
shared_height=gpu_core_width*2
cpu_space=0.2*scale
gpu_space=0.2*scale

smx_height=8*(gpu_core_width) + shared_height
smx_width=8*(gpu_core_width)

dram_space=2*scale
dram_height=5*scale

gpu_width  = (gpu_core_width+gpu_space)*15
gpu_height = smx_height*4 + gpu_space*4 + gpu_cache_height + cpu_space*2

# width and height of combined items inside cpu socket (minus padding at edge)
cpu_cores_width  = 4*cpu_core_width + 3*cpu_space
cpu_cores_height = 3*(cpu_core_width+l2_height) + cpu_core_width + 4*cpu_space

gpu_cores_width  = 15*8*gpu_core_width + 14*gpu_space
gpu_width  = gpu_cores_width + 2*cpu_space

cpu_width  = cpu_cores_width + 2*cpu_space
cpu_height = cpu_cores_height + 2*cpu_space

image_height = cpu_height + dram_space + dram_height
image_width = cpu_width + 3*dram_space + gpu_width

hbm_height = image_height - gpu_height - dram_space

def print_measurement(name, value):
    return '\\newcommand{\\' + name + '}{' + str(value) + 'mm}\n'

def print_header():
    text = ''

    text += print_measurement('gpucorewidth', gpu_core_width)
    text += print_measurement('gpucoreheight', gpu_core_width)
    text += print_measurement('cpuspace', cpu_space)
    text += print_measurement('memwidth', 16)
    text += print_measurement('memheight', 4)
    text += print_measurement('corewidth', cpu_core_width)
    text += print_measurement('sharedheight', shared_height)
    text += print_measurement('lthreewidth', cpu_cores_width)
    text += print_measurement('smxwidth', smx_width)
    text += print_measurement('ltwoheight', l2_height)
    text += print_measurement('gpucacheheight', gpu_cache_height)
    text += print_measurement('gpucachewidth', gpu_cores_width)
    text += print_measurement('dramheight', dram_height)
    text += print_measurement('hbmheight', hbm_height)
    text += print_measurement('cpuwidth', cpu_width)
    text += print_measurement('cpuheight', cpu_height)
    text += print_measurement('gpuwidth', gpu_width)
    text += print_measurement('gpuheight', gpu_height)
    text += print_measurement('imageheight', image_height)
    text += print_measurement('imagewidth', image_width)

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
\tikzstyle{cpu_core}=[
    draw,
    rectangle,
    minimum height=\corewidth,
    minimum width=\corewidth,
    fill=green!50,
    anchor=north west]
\tikzstyle{cache_lthree}=[
    draw,
    rectangle,
    minimum height=\corewidth,
    minimum width=\lthreewidth,
    fill=blue!20,
    anchor=north west]
\tikzstyle{cache_ltwo}=[
    draw,
    rectangle,
    minimum height=\ltwoheight,
    minimum width=\corewidth,
    fill=yellow!50,
    anchor=north west]
\tikzstyle{dram}=[
    draw,
    rectangle,
    minimum width=\cpuwidth,
    minimum height=\dramheight,
    fill=red!20,
    anchor=north west]
\tikzstyle{hbm}=[
    draw,
    rectangle,
    minimum width=\gpuwidth,
    minimum height=\hbmheight,
    fill=red!20,
    anchor=north west]
\tikzstyle{managed}=[
    draw,
    rectangle,
    minimum width=\imagewidth,
    minimum height=\hbmheight,
    fill=red!20,
    anchor=north west]
\tikzstyle{cpusocket}=[
    draw,
    rectangle,
    minimum width=\cpuwidth,
    minimum height=\cpuheight,
    fill=green!20,
    anchor=north west]
\tikzstyle{gpusocket}=[
    draw,
    rectangle,
    minimum width=\gpuwidth,
    minimum height=\gpuheight,
    fill=green!20,
    anchor=north west]
    '''

    text += node_description
    return text

def print_footer():

    return r'''
\end{tikzpicture}

\end{document}
'''

def print_node(i, j, pos):
    return '\\node[core] (core' + str(i) + ') [' + pos + ' = of core' + str(j) + '] {};\n'

def print_smx(smx_id, x, y):
    first_node = smx_id*64
    text = '\\node[core] (core' + str(first_node) + ') at(' + str(x) + 'mm,' + str(y) + 'mm) {};\n'
    for i in range(first_node+1,first_node+8):
        text += print_node(i, i-1, 'right')

    for i in range(1,8):
        text += '\n'
        text += str() + '\n'
        start = first_node + i*8
        text += print_node(start, start-8, 'below')
        for i in range(start+1,start+8):
            text += print_node(i, i-1, 'right')

    text += '\\node[shared] (memory) at(' + str(x) + 'mm,' + str(y-smx_height+shared_height) + 'mm) {\\bfseries \\tiny shared memory};\n\n'
    return text

def print_gpu(x, y):
    text = ''

    start_x = x + cpu_space
    start_y = y - cpu_space
    text =  '\\node[gpusocket] (gpu) at(' + str(x) + 'mm,' + str(y) + 'mm) {};'

    for col in range(15):
        for row in range(2):
            smx_id = col + row*8
            text += '\n% smx ' + str(smx_id) + ' @ ' + str(row) + ',' + str(col)  + '\n\n'
            text += print_smx(smx_id, start_x+col*(smx_width+gpu_space), start_y-row*(smx_height+gpu_space))

    two_smx_rows = 2*(smx_height + gpu_space)
    text += '\n\n\\node[gpucache] at (' + str(start_x) + 'mm,' + str(start_y-two_smx_rows) + 'mm) {\\bfseries \\Huge L2 Cache};'

    start_y = start_y - (two_smx_rows + gpu_cache_height + gpu_space)
    for col in range(15):
        for row in range(2,4):
            text += '\n% smx ' + str(smx_id) + ' @ ' + str(row) + ',' + str(col)  + '\n\n'
            text += print_smx(smx_id, start_x+col*(smx_width+gpu_space), start_y-(row-2)*(smx_height+gpu_space))

    return text

def print_hbm(x, y):
    text =  '\\node[hbm] (hbm) at(' + str(x) + 'mm,' + str(y) + 'mm) {\\bfseries \\Huge 16 GB HBM2};'
    return text

def print_ddr(x, y):
    start_x = x
    start_y = y
    text =  '\\node[dram] (dram) at(' + str(start_x) + 'mm,' + str(start_y) + 'mm) {\\bfseries \\Huge 64 GB DDR4};\n'

    return text

def print_managed(x, y):
    start_x = x
    start_y = y
    text =  '\\node[managed] (managed) at(' + str(start_x) + 'mm,' + str(start_y) + 'mm) {\\bfseries \\Huge Unified Memory};\n'

    return text

def print_cpu(x, y):
    text = ''

    # draw outline of cpu
    start_x = x + cpu_space
    start_y = y - cpu_space

    text =  '\\node[cpusocket] (cpu) at(' + str(x) + 'mm,' + str(y) + 'mm) {};'

    # draw 3 rows of 4 cores

    text +=  '\\node[cpu_core] (cpu_core0) at('+str(start_x)+'mm,'+str(start_y)+'mm) {\\bfseries Core 0};\n'
    text +=  '\\node[cpu_core] (cpu_core1) [right = \cpuspace of cpu_core0] {\\bfseries Core 1};\n'
    text +=  '\\node[cpu_core] (cpu_core2) [right = \cpuspace of cpu_core1] {\\bfseries Core 2};\n'
    text +=  '\\node[cpu_core] (cpu_core3) [right = \cpuspace of cpu_core2] {\\bfseries Core 3};\n'

    text +=  '\\node[cache_ltwo] (cache_c0) [below = of cpu_core0] {\\bfseries \\tiny L2 Cache};\n'
    text +=  '\\node[cache_ltwo] (cache_c1) [below = of cpu_core1] {\\bfseries \\tiny L2 Cache};\n'
    text +=  '\\node[cache_ltwo] (cache_c2) [below = of cpu_core2] {\\bfseries \\tiny L2 Cache};\n'
    text +=  '\\node[cache_ltwo] (cache_c3) [below = of cpu_core3] {\\bfseries \\tiny L2 Cache};\n'

    text +=  '\\node[cpu_core] (cpu_core4) [below = \cpuspace of cache_c0] {\\bfseries Core 4};\n'
    text +=  '\\node[cpu_core] (cpu_core5) [right = \cpuspace of cpu_core4] {\\bfseries Core 5};\n'
    text +=  '\\node[cpu_core] (cpu_core6) [right = \cpuspace of cpu_core5] {\\bfseries Core 6};\n'
    text +=  '\\node[cpu_core] (cpu_core7) [right = \cpuspace of cpu_core6] {\\bfseries Core 7};\n'

    text +=  '\\node[cache_ltwo] (cache_c4) [below = of cpu_core4] {\\bfseries \\tiny L2 Cache};\n'
    text +=  '\\node[cache_ltwo] (cache_c5) [below = of cpu_core5] {\\bfseries \\tiny L2 Cache};\n'
    text +=  '\\node[cache_ltwo] (cache_c6) [below = of cpu_core6] {\\bfseries \\tiny L2 Cache};\n'
    text +=  '\\node[cache_ltwo] (cache_c7) [below = of cpu_core7] {\\bfseries \\tiny L2 Cache};\n'

    text +=  '\\node[cpu_core] (cpu_core8) [below = \cpuspace of cache_c4] {\\bfseries Core 8};\n'
    text +=  '\\node[cpu_core] (cpu_core9) [right = \cpuspace of cpu_core8] {\\bfseries Core 9};\n'
    text +=  '\\node[cpu_core] (cpu_core10) [right = \cpuspace of cpu_core9] {\\bfseries Core 10};\n'
    text +=  '\\node[cpu_core] (cpu_core11) [right = \cpuspace of cpu_core10] {\\bfseries Core 11};\n'
    text +=  '\\node[cache_ltwo] (cache_c8) [below = of cpu_core8] {\\bfseries \\tiny L2 Cache};\n'
    text +=  '\\node[cache_ltwo] (cache_c9) [below = of cpu_core9] {\\bfseries \\tiny L2 Cache};\n'
    text +=  '\\node[cache_ltwo] (cache_c10) [below = of cpu_core10] {\\bfseries \\tiny L2 Cache};\n'
    text +=  '\\node[cache_ltwo] (cache_c11) [below = of cpu_core11] {\\bfseries \\tiny L2 Cache};\n'

    cache_y_offset=start_y-(cpu_core_width+cpu_space+l2_height)*3 - cpu_space
    text +=  '\\node[cache_lthree] (l3) at('+str(start_x)+'mm, '+str(cache_y_offset)+'mm) {\\bfseries \\Huge L3 Cache};\n'

    # draw L2 cache

    return text

#
#   main
#

args = parse_clargs()

txt =  print_header()
txt += print_cpu(0, 0)

gpu_start_x = cpu_width + 3*dram_space
cpu_start_x = 0
managed_start = -gpu_height - dram_space
txt += print_gpu(gpu_start_x, 0)

if args.managed :
    txt += print_managed(0, -(gpu_height+dram_space))
    txt += '\n'
    txt += '\\path[pil,<->,black,line width=2.5mm] (' + str(cpu_width/2) + 'mm,' + str(-cpu_height) + 'mm) edge (' + str(cpu_width/2) + 'mm,' + str(managed_start) + 'mm);\n'
    txt += '\\path[pil,<->,black,line width=2.5mm] (' + str(gpu_start_x+gpu_width/2) + 'mm,' + str(-gpu_height) + 'mm) edge (' + str(gpu_start_x+gpu_width/2) + 'mm,' + str(managed_start) + 'mm);\n'
else :
    txt += print_ddr(0, -(cpu_height+dram_space))
    txt += print_hbm(gpu_start_x, -(gpu_height+dram_space))
    txt += '\n'
    txt += '\\path[pil,<->,black,line width=2mm] (hbm.north west)  edge (dram.east);\n'
    txt += '\\path[pil,<->,black,line width=2mm] (gpu.south)  edge (hbm.north);\n'
    txt += '\\path[pil,<->,black,line width=2mm] (cpu.south)  edge (dram.north);\n'

txt += print_footer()

print txt
