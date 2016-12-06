import os
class DirOperator:
	def __init__(self,dir):
		self.dir = dir
		self.__createdir()
	def __createdir(self):
		if os.path.isdir(self.dir) == False:
			os.mkdir(self.dir)