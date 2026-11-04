.PHONY: all generate build poc01 poc02 test clean
all:
	python -m src.main --all
generate:
	python -m src.main --generate
build:
	python -m src.main --build
poc01:
	python -m src.main --poc01
poc02:
	python -m src.main --poc02
test:
	python -m unittest discover -s tests -v
clean:
	python -m src.main --clean-generated
