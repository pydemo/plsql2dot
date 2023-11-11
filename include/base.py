import re, os, sys

import include.config.init_config as init_config  
apc = init_config.apc

def get_name(p,c, id=0):
	if type(c) is str:
		title=c[:20]
		pattern = '[^\w\d]'
		clean= re.sub(pattern, '_', title)
		return f's_{clean}_{p.index(c)}_{id}',title 
	else:
		return f'{c.get_type()}_{p.index(c)}_{id}', c.get_type()

class BaseBase(object):
	

	def get_type(self):
		return self.__class__.__name__
	def init(self, parent, lid):
		self.parent=parent
		self.lid = lid
		self.gid = gid = apc.get_gid()
		#print(1111,gid)
		self.set_name()
		self.tname=self.__class__.__name__
		apc.cntr.inc(self)
		#self.dfrom=None
	


	def get_name(self):
		return self.name,  self.label
	def get_dot(self):
		return f'{self.name} [shape="box",label="{self.tname} {apc.cntr.get(self)}" ];'
	def set_name(self):
		p,c=self.parent, self
		if type(c) in [String]:
			obj=self.val
		else:
			obj=self
		print('parent:',type(p))
		self.name, self.label = f'{c.get_type()}_{p.index(obj)}	_{apc.get_gid()}', c.get_type()
		
class String(BaseBase):
	def __init__(self, val):
		self.val=val
	def get_str_dot(self, parent, dfrom, lid, hdot, fdot):
		self.dfrom=dfrom
		gid =apc.get_gid()
		self.init(parent, lid)

		hdot.append(f'{self.get_dot()}')
		
		if 1:
			dto, label = self.get_name()
			fdot.append(f'{self.dfrom} -> {dto}[label="" ];')
			
class Base(BaseBase):
	def get_str_dot(self,  dfrom,  hdot, fdot):
		parent =self.parent
		lid=self.lid
		self.dfrom=dfrom
		gid =apc.get_gid()
		self.init(parent, lid)

		hdot.append(f'{self.get_dot()}')
		
		if 1:
			dto, label = self.get_name()
			fdot.append(f'{self.dfrom} -> {dto}[label="" ];')
	def get_full_dot(self, parent, dfrom, lid, hdot, fdot):
		self.dfrom=dfrom
		gid =apc.get_gid()
		self.init(parent, lid)

		hdot.append(f'{self.get_dot()}')
		
		if 1:
			dto, label = self.get_name()
			fdot.append(f'{self.dfrom} -> {dto}[label="" ];')
		#if  type(self) not in [str]:
		print('before loop:', type(self), len(self))
		#print('before loop:', self[0])
		# Assume `obj` is your object
		base_classes = self.__class__.__bases__
		print('Base: ',base_classes, str in base_classes)
		if str in base_classes:
			print('STR in BASE', type(self), self)
			self.get_str_dot(self.name, hdot, fdot)
		else:
			for cid,c in enumerate(self):
				print (self.name, type(c), f'>{c}<')
				#assert c, self.name
				print (self.name, type(c))
				if type(c) in [str]:
					print('Base 2 : ',c.__class__.__bases__, str in base_classes)
					c = String(c)
					c.get_str_dot(self, self.name, cid, hdot, fdot)
				else:
					c.get_full_dot(self, self.name, cid, hdot, fdot)
			
		