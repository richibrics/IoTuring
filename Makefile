run:
	python3 IoTuring
config:
	python3 IoTuring -c
clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf