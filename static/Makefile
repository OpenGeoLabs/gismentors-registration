PDFFILES = $(patsubst %.tex, %.pdf, $(wildcard *.tex))

all: $(PDFFILES)

$(PDFFILES): %.pdf: %.tex
	pdflatex $<