from pypeg2 import *
import re
INSERT = K("insert")
# Regular expression patterns for different parts of the statement
identifier_pattern = re.compile(r'[a-zA-Z_]\w*')
string_literal_pattern = re.compile(r"'(?:[^'\\]|\\.)*'")  # Handles escaped quotes within strings
function_call_pattern = re.compile(r'\w+\(\)')

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

class InsertKword(Keyword):
	grammar = Enum(K("insert"), K("INSERT"), K("into"), K("INTO"), K("values"), K("VALUES"))

def IK(k):
	return re.compile(r'\b' + k + r'\b', re.IGNORECASE)

def IK2(kword):
	return ignore_case(kword)

# Class for the list of columns in the insert statement
class ColumnList(List):
	grammar = '(', csl(Identifier), ')'


	
class SelectStatement(List):
	# Defines the structure of an if statement
	grammar = 'SELECT', ColumnList, \
			  'FROM', name()

# Class for the insert statement itself
class InsertStatement(List):
	grammar = IK("insert into"), attr('table', Identifier), attr('columns', ColumnList),SelectStatement,';'


			  
# Example SQL insert statement
test_string = '''
	INSERT INTO package_search_temp (mid, manifest_date, file_name)
	SELECT
			COALESCE(fmp.mailowner_mailer_id, pr.mid) AS mid,
			pr.pkg_grp_id AS pkg_grp_id,
			p.processing_time AS dtc,
			p.processing_time AS dtu,
			fmp.rate_ind AS rate_ind
		FROM stage_pkgs_outbound pkgs;

'''
if __name__=='__main__':
	# Parse the test string
	parsed_insert = parse(test_string, InsertStatement)

	# Pretty-print the parsed insert statement
	print(f"Table: {parsed_insert.table}")
	print("Columns:", [str(column) for column in parsed_insert.columns])
	#print("Values:", [str(value) for value in parsed_insert.values])
