import re, os, sys
def get_name(p,c, id=0):
	if type(c) is str:
		title=c[:20]
		pattern = '[^\w\d]'
		clean= re.sub(pattern, '_', title)
		return f's_{clean}_{p.index(c)}_{id}',title 
	else:
		return f'{c.get_type()}_{p.index(c)}_{id}', c.get_type()
		
		
class Base(object):
	

	def get_type(self):
		return self.__class__.__name__
	def init(self, parent, lid, gid):
		self.parent=parent
		self.lid, self.gid=lid, gid
		self.name,  self.label=get_name(parent, lid, gid)
		self.tname=self.__class__.__name__

	def get_dot(self):
		return f'{self.name} [shape="box",label="{self.tname}" ];'