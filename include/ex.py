from pypeg2 import *
import re
import include.config.init_config as init_config  
from include.base import  Base
apc = init_config.apc


e=sys.exit
# Define rest_of_line as a regex that matches any characters until the end of the line
rest_of_line = re.compile(r'.*?(?=\n|$)')

# Define the keywords
exception_keyword = Keyword("exception")
when_keyword = Keyword("when")
others_keyword = Keyword("others")
then_keyword = Keyword("then")
raise_keyword = Keyword("raise")
info_keyword = Keyword("info")

# Define a pattern that captures a generic SQL statement or PL/pgSQL code
sql_statement = re.compile(r".*?",re.DOTALL)

class Local(object):
	def set_fname(self): self.fname=__name__
	
# Define a class for a block of code, which can be a series of SQL statements
class ExMessage(List, Base, Local):
	info = re.compile(r'info', re.IGNORECASE)
	grammar = info, csl(re.compile(r'[^,;]*')),';'
	def __str__(self):
		return 'test'
	def __repr__(self):
		return ' '.join(self)		
		
class _ExMessage(List, Base, Local):
	grammar = csl(re.compile(r'[^,;]*'))
	def __str__(self):
		return 'test'
	def __repr__(self):
		return self[0]		
# Define a class for the exception block
class ExceptionBlock(List, Base, Local):
	
	raisee = re.compile(r'raise', re.IGNORECASE)
	thenn = re.compile(r'then', re.IGNORECASE)
	others = re.compile(r'others', re.IGNORECASE)
	grammar = exception_keyword, when_keyword, attr('cond',others), then_keyword, raise_keyword,  attr('msg', csl(ExMessage))
	
	
	def get_full_dot(self, parent, dfrom, lid, hdot, fdot, level):
		Base.get_full_dot(self, parent, dfrom, lid, hdot, fdot, level)
		#hdot.append('exception [label="Exception", color="red" shape=doublecircle];')
		hdot.append('note [label="Exception handling", shape=none, fontsize=14, fontcolor=red];')

	def show_children(self, cfrom, hdot, fdot):
		base_classes = self.__class__.__bases__
		assert not str in base_classes, base_classes
		cfdot =  []
		#attr=self.parent.attr
		#bids=[]
		for cid,c in enumerate(self):
			
			c.get_full_dot(self, self.name, cid, hdot, cfdot, self.level+1)
			cfrom = c
			#bids.append([apc.gid, ck])
			
		fdot.append(f'{self.name} -> end[label="Abnormal exit"  style=dashed color=red style=bold];')
		#cfdot.append(f'exception -> end[label=""];')
		cfdot.append(f'note -> {self.name} [ weight=1000]')

		self.get_dot_attr(hdot, cfdot)
		self.get_subgraph(cfdot, fdot)
		#end_if= f'end_if_{self.parent.gid}'
		#fdot.append(f'{end_if} -> end;')
	def show_attr(self, hdot, fdot):
		pass
	def get_subgraph(self, cfdot, fdot):
		fdot.append(f'''
		subgraph Cluster_{self.name}{{
		edge [color=blue, style=dashed];
		node [color=lightblue, style=filled];
		''')
		fdot +=cfdot
		fdot.append('''
		}''')
		#pp(cfdot)
		#e()
		
		
# Test string
test_string = '''
exception when others then
raise info 'SQLERRM=(%) SQLSTATE=(%) location_name=(%)', SQLERRM, SQLSTATE, v_location_name ;
'''

# Parse the test string
try:
	parsed_exception = parse(test_string, ExceptionBlock)
	print("Parsed Exception Block:")
	print(parsed_exception.msg)  
	#e()
except Exception as e:
	print(e)
	raise
