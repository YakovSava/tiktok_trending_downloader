install: compile
	pip install -r requirments.txt
	python -m playwright install

run:
	python main.py

compile:
	cd binder_r
	maturin build --release
	cd ..

download: install
	python downloader.py