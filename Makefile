install:
	pip install -r requirments.txt
	python -m playwright install

run:
	python main.py

compile:
	script.sh

repair:
	playwright uninstall --all
	pip install --force-reinstall -v "playwright==1.40.0"