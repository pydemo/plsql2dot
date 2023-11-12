from pypeg2 import *
from include.base import String,  Base
import include.config.init_config as init_config  
apc = init_config.apc


e=sys.exit

# Define the patterns for matching
identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_\.]*")  # Identifiers can contain dots for table.column
string_literal = re.compile(r"'[^']*'")  # String literals
comparison_operator = re.compile(r"=|!=|>|<|>=|<=")  # Comparison operators
boolean_operator = re.compile(r"AND", re.IGNORECASE)  # Boolean operator AND
null_condition = re.compile(r"IS NULL", re.IGNORECASE)  # NULL condition
function_call = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*\(.+\)")  # Function call, like COALESCE(...)

from pypeg2 import *
from pprint import pprint as pp
def KW(kword):
	return re.compile(r'\b' + kword + r'\b', re.IGNORECASE)
# Define keywords as needed
SELECT = KW("SELECT")
FROM = KW("FROM")
WHERE = KW("WHERE")
AND = KW("AND")
COALESCE = KW("COALESCE")
IS_NULL = KW("IS NULL")

# Define patterns for table names, column names, etc.
identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
quoted_string = re.compile(r"'[^']*'")
number = re.compile(r"\d+")
expression = re.compile(r".+?(?= AND|$)")
function_call_pattern = re.compile(r'\w+\(\)')

class Local(object):
	def set_fname(self): self.fname=__name__
	
	
class Column(str):
	grammar = [(name(),'.',name()), quoted_string , identifier , number, name()]

if 1:
	func_identifier = re.compile(r"[a-zA-Z_][^,]*")
	func_string_literal = re.compile(r"'[^']*'")
	func_condition_operator = re.compile(r"=|!=|>|<|>=|<=")

	# Function name
	function_name = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")

	# Define the structure of a function call
	class FunctionCall(str):
		grammar = function_name, "(", csl([func_identifier, func_string_literal]), ")"

	# Define a simple condition which may include a function call
	class FuncCondition(str):
		grammar = FunctionCall, func_condition_operator, func_string_literal
		

# Define the structure for a comparison (e.g., column = value)
class Comparison(str):
	identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_\.]*")  # Identifiers can contain dots for table.column
	string_literal = re.compile(r"'[^']*'")  # String literals
	comparison_operator = re.compile(r"=|!=|>|<|>=|<=")  # Comparison operators
	boolean_operator = re.compile(r"AND", re.IGNORECASE)  # Boolean operator AND	
	grammar = identifier, comparison_operator, [identifier, string_literal]



class IsNullCondition(str):
	identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_\.]*")
	null_condition = re.compile(r"IS NULL", re.IGNORECASE)  # NULL condition
	grammar = identifier, null_condition
	
class Condition(str, String, Local):
	grammar = [Comparison,FuncCondition, IsNullCondition]

class WhereClause(List, Base, Local):
	grammar = WHERE, csl(Condition, separator=AND) , optional(';')

# Your test string
test_string = '''
WHERE pkgs.pkgs_search_processed = 'N' 
	AND pkgs.dtc > p_cutoff_date 
	AND COALESCE(pkgs.dup_unmanifested_or_postage_due, 'N') = 'Y' 
	AND ps.pkg_grp_id IS NULL
'''



test_string = '''
WHERE pkgs.pkgs_search_processed = 'N' 
	AND pkgs.dtc > p_cutoff_date 
	AND COALESCE(pkgs.dup_unmanifested_or_postage_due, 'N') = 'Y' 
	AND ps.pkg_grp_id IS NULL
	AND pkgs_search_processed = 'N'
	AND ready_to_process = 'Y' 
	AND payment_rec_arrived = 'Y' 
	AND COALESCE(dup_unmanifested_or_postagedue, 'N') != 'Y';
'''
test_string = '''
	WHERE pkgs.pkgs_search_processed = 'N' AND pkgs.info_fcn_or_crid_of_mail_owner = fcn.crid
		AND pkgs.current_month_flag = 'Y' AND payment_rec_arrived = 'Y' AND pkgs.dtc > p_cutoff_date
		AND COALESCE(pkgs.dum_unmanifested_or_postagedue, 'N') = 'Y'
		AND pkgs.pkgs_search_processed = 'N' AND pkgs.dtc > p_cutoff_date AND COALESCE(pkgs.dup_unmanifested_or_postage_due, 'N') = 'Y' AND ps.pkg_grp_id IS NULL;
'''


if __name__ == '__main__':
	# Parse the string using the defined grammar
	parsed_where_clause = parse(test_string, WhereClause)

	# Printing each parsed condition for clarity
	for condition in parsed_where_clause:
		print(condition)
