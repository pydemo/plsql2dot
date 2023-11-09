from pypeg2 import *
import re

# This pattern will match any amount of whitespace including newlines
ws = re.compile(r'\s*')
string_literal = re.compile(r"'(?:[^'\\]|\\.)*'")

rest_of_line = re.compile(r'.*$', re.MULTILINE)

class Base2(object):
	def get_type(self):
		return f'{__name__}.{self.__class__.__name__}'.replace('.','_')
from include.base import  Base

class Assignment(List, Base):
	grammar = name(), '=', string_literal, ';'	
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
