all:
	python ebook.py
	rm -f joj.epub
	~/.cabal/bin/pandoc --toc ebook.txt -o joj.epub --from=markdown-auto_identifiers --toc-depth=2 --data-dir=$(shell pwd) --include-in-header titlesec.tex
