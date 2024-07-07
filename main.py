from asyncio import run
from plugins.ttd import TikTokDownloader
from plugins.getter import OPTIMIZED

if OPTIMIZED:
	from plugins.getter import TomlGetter, OptimizedGetter as Getter 
else:
	from plugins.getter import TomlGetter, NonOptimizedGetter as Getter 

toml = TomlGetter(getter=Getter())

data = toml.load("config.ini")
ttd = TikTokDownloader(
	tt_token=data['tt_token'],
	output_folder=data['output_folder'],
	speed_ratio=data['speed_ratio'],
	resize_ratio=data['resize_ratio'],
	audio_filename=data['audio'],
	report=data['report_filename']
)

if __name__ == '__main__':
	run(ttd.run(5))