install: compile
	pip install -r requirments.txt

run:
	python main.py

compile:
	cd binder_r
	maturin build --release
	cd ..
	pip install ./binder_r/target/wheels/*

download: install
	python downloader.py