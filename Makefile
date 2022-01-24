run:
	python3 main.py
config:
	python3 main.py -c
clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf