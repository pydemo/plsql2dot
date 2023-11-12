from pypeg2 import *
import re
from pprint import pprint as pp
from include.base import String,  Base
import include.config.init_config as init_config  
apc = init_config.apc


e=sys.exit
# This pattern will match any amount of whitespace including newlines
ws = re.compile(r'\s*')

rest_of_line = re.compile(r'.*$', re.MULTILINE)


from include.base import  String



string_literal = re.compile(r"'(?:[^'\\]|\\.)*'")

class Local(object):
	def set_fname(self): self.fname=__name__
	
	
class Assignment(List, Base, Local):
	grammar = attr('identifier',name()),['=', ':='], attr('value',string_literal), ';'	
	def _get_dot(self):
		return f'{self.name} [shape="box",  color="gray", label="Stmt {self.tname} {apc.cntr.get(self)}" ];'	
class Comment(str):
	grammar = '--', rest_of_line
	
	
class Statement(List):
	# This class could be extended with more statement types as needed
	grammar =  [attr("assignment",Assignment), attr("comment", Comment)]
			  



class Code(List):
	grammar = maybe_some(Statement)

test_string = '''
	--v_location_name = 'Get count of unprocessed search pkgs';
	v_location_name2 = 'Get count of gwsbw5sg search pkgs';

'''
if 0:
	parsed_code = parse(test_string, Code)

	print(parsed_code)
