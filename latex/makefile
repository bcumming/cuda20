LATEX=pdflatex

PDF=introduction.pdf porting.pdf memory.pdf kernels.pdf shared.pdf cuda_mpi.pdf async.pdf miniapp.pdf cuda2d.pdf miniapp_intro.pdf

all: images ${PDF}

porting.pdf: beamerthemeCSCS.sty images porting.tex
	$(LATEX) porting.tex

introduction.pdf: beamerthemeCSCS.sty images introduction.tex
	$(LATEX) introduction.tex

memory.pdf: beamerthemeCSCS.sty images memory.tex
	$(LATEX) memory.tex

kernels.pdf: beamerthemeCSCS.sty images kernels.tex
	$(LATEX) kernels.tex

shared.pdf: beamerthemeCSCS.sty images shared.tex
	$(LATEX) shared.tex

cuda_mpi.pdf: beamerthemeCSCS.sty images cuda_mpi.tex
	$(LATEX) cuda_mpi.tex

cuda2d.pdf: beamerthemeCSCS.sty images cuda2d.tex
	$(LATEX) cuda2d.tex

async.pdf: beamerthemeCSCS.sty images async.tex
	$(LATEX) async.tex

miniapp.pdf: beamerthemeCSCS.sty images miniapp.tex
	$(LATEX) miniapp.tex

miniapp_intro.pdf: beamerthemeCSCS.sty images miniapp_intro.tex
	$(LATEX) miniapp_intro.tex

force : ${PDF}
	$(LATEX) introduction.tex
	$(LATEX) porting.tex

images : images/*.tex
	cd images; make;

clean:
	rm -f ${PDF}
	rm -f *.aux *.dvi *.log *.nav *.out *.snm *.toc *.vrb
