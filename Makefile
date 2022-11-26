run:
	python3 .
config:
	python3 . -c
clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf