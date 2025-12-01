# Makefile for LaTeX document compilation

# Document name (without .tex extension)
DOC = adaptive-cane-report

# LaTeX compiler
LATEX = pdflatex
BIBTEX = bibtex

# Default target
all: $(DOC).pdf

# Compile the PDF
$(DOC).pdf: $(DOC).tex template/bibliography.bib
	$(LATEX) $(DOC)
	$(BIBTEX) $(DOC)
	$(LATEX) $(DOC)
	$(LATEX) $(DOC)

# Clean auxiliary files
clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.fdb_latexmk *.fls *.synctex.gz

# Clean all generated files including PDF
cleanall: clean
	rm -f $(DOC).pdf

# Force rebuild
rebuild: cleanall all

# Help target
help:
	@echo "Available targets:"
	@echo "  all      - Compile the PDF (default)"
	@echo "  clean    - Remove auxiliary files"
	@echo "  cleanall - Remove all generated files including PDF"
	@echo "  rebuild  - Clean and rebuild everything"
	@echo "  help     - Show this help message"

.PHONY: all clean cleanall rebuild help