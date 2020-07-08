PDFS=smx.pdf reduction.pdf blur_point_gather.pdf blur_point_scatter.pdf blur_point_shared.pdf core.pdf async_null.pdf async_simple.pdf async_two_streams.pdf  overlap.pdf node.pdf node_managed.pdf fp-perf.pdf transistors.pdf frequency.pdf

all: ${PDFS}

fp-perf.pdf: fp-perf.tex
	pdflatex fp-perf.tex

frequency.pdf: frequency.tex
	pdflatex frequency.tex

transistors.pdf: transistors.tex
	pdflatex transistors.tex

node.pdf: node.tex print_node.py
	python2 print_node.py > node_raw.tex
	pdflatex -jobname=node node.tex

node_managed.pdf: node.tex print_node.py
	python2 print_node.py --managed > node_raw.tex
	pdflatex -jobname=node_managed node.tex

smx.pdf: smx.tex print_smx.py
	./print_smx.py -i block > smx_raw.tex
	pdflatex -jobname=smx smx.tex

core.pdf: core.tex print_smx.py
	./print_smx.py -i thread > smx_raw.tex
	pdflatex -jobname=core smx.tex

reduction.pdf: reduction.tex
	pdflatex reduction.tex

blur_point_gather.pdf: blur_point_gather.tex
	pdflatex blur_point_gather.tex

blur_point_scatter.pdf: blur_point_scatter.tex
	pdflatex blur_point_scatter.tex

blur_point_shared.pdf: blur_point_shared.tex
	pdflatex blur_point_shared.tex

async_null.pdf: async_null.tex
	pdflatex async_null.tex

async_simple.pdf: async_simple.tex
	pdflatex async_simple.tex

async_two_streams.pdf: async_two_streams.tex
	pdflatex async_two_streams.tex

overlap.pdf: overlap.tex
	pdflatex overlap.tex

clean:
	rm -f ${PDFS}
	rm -f *.dvi
	rm -f *.aux
	rm -f *.log
	rm -f node_raw.tex
