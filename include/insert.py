from pypeg2 import *
import re

# Regular expression patterns for different parts of the statement
identifier_pattern = re.compile(r'[a-zA-Z_]\w*')
string_literal_pattern = re.compile(r"'(?:[^'\\]|\\.)*'")  # Handles escaped quotes within strings
function_call_pattern = re.compile(r'\w+\(\)')

from include.base import  Base

import include.config.init_config as init_config  
apc = init_config.apc


e=sys.exit


class Local(object):
	def set_fname(self): self.fname=__name__
	
	
# Class for table name, column names, and function calls (like getdate())
class Identifier(str):
	grammar = identifier_pattern

class FunctionCall(str):
	grammar = function_call_pattern

# Class for string literals within the values clause
class StringLiteral(str):
	grammar = string_literal_pattern

# Class for a single value, which can be a string literal or a function call
class Value(str):
	grammar = [FunctionCall, StringLiteral, Identifier]

# Class for the list of values to be inserted
class ValueList(List):
	grammar = '(', csl(Value), ')'

# Class for the list of columns in the insert statement
class ColumnList(List):
	grammar = '(', csl(Identifier), ')'

# Class for the insert statement itself
class InsertStatement(List, Base, Local):
	grammar = 'insert into', attr('table', Identifier), attr('columns', ColumnList), \
			  'values', attr('values', ValueList), ';'
	def get_dot(self):
		return f'{self.name} [shape="box", style=bold, color="yellow", label="{self.tname} {apc.cntr.get(self)}" ];'
# Example SQL insert statement
test_string = '''
	insert into ppc_qlik_reports_log (log_date, report_name, module_name, status)
	values (getdate(), 'MANIFEST_SEARCH_REPORT', 'Summarizing Manifest Search', v_status);
'''
if __name__=='__main__':
	# Parse the test string
	parsed_insert = parse(test_string, InsertStatement)

	# Pretty-print the parsed insert statement
	print(f"Table: {parsed_insert.table}")
	print("Columns:", [str(column) for column in parsed_insert.columns])
	print("Values:", [str(value) for value in parsed_insert.values])
