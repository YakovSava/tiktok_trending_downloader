from toml import loads
from typing import Callable

try:
	from binder import reader, writer
	OPTIMIZED = True
except ImportError:
	reader = Callable
	writer = Callable
	OPTIMIZED = False


class OptimizedGetter:

	def __init__(self):
		self.read = reader
		self.write = writer


class NonOptimizedGetter:

	def __init__(self):
		pass

	def read(self, filename:str) -> str:
		with open(filename, 'r', encoding='utf-8') as file:
			return file.read()

	def write(self, filename:str, data:str) -> str:
		with open(filename, 'w', encoding='utf-8') as file:
			file.write(data)
			return filename

class TomlGetter:

	def __init__(self, getter:NonOptimizedGetter or OptimizedGetter=None):
		if getter is None:
			raise SystemError('Вы не передали геттер!')
		self._get = getter

	def load(self, filename:str) -> dict:
		return loads(self._get.read(filename))