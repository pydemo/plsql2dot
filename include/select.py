from pypeg2 import *
import re

# This pattern will match any amount of whitespace including newlines
ws = re.compile(r'\s*')
rest_of_line = re.compile(r'.*$', re.DOTALL)
rest_of_select_body = re.compile(r'(?:(?!;\s*$).)*', re.DOTALL)
condition = re.compile(r'[^;]+')


class Base(object):
	def get_type(self):
		return f'{__name__}.{self.__class__.__name__}'.replace('.','_')
		
		
class Condition(str):
	grammar = name(), '=',  word

# Using csl() to parse comma-separated lists that may span multiple lines
class ConditionList(List):
	grammar = csl(Condition)

class Select(List, Base):
	grammar = ['SELECT', 'select'],condition,';'

class SQLExpression(List):
	grammar = maybe_some(Select)

test_string = '''
SELECT count(*) INTO v_cnt_search_pkgs
from stage_pkgs_outbound
WHERE pkgs_search_processed = 'N' AND
ready_to_process = 'Y' AND
payment_rec_arrived = 'Y' AND
dtc > p_cutoff_date;


'''
if 0:
	parsed_sql = parse(test_string, SQLExpression)

	print(parsed_sql)
