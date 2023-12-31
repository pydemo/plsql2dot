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

# Define patterns for table names, column names, etc.
identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
quoted_string = re.compile(r"'[^']*'")
number = re.compile(r"\d+")
expression = re.compile(r".+?(?= AND|$)")
function_call_pattern = re.compile(r'\w+\(\)')
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

	# Define a grammar for the full expression (assuming it's just a condition)
	class FuncExpression(str):
		grammar = FuncCondition
if 1:



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

class Condition(str):
	grammar = [Comparison,FuncCondition, IsNullCondition]

class WhereClause(List):
	grammar = WHERE, csl(Condition, separator=AND)

# Define your clauses
class SelectClause(List):
	grammar = SELECT,  csl(name())

class FromClause(List):
	grammar = FROM, identifier, name()

# Define a full SQL statement
class SQLStatement(List):
	grammar = attr("select_clause", SelectClause), \
			  attr("from_clause", FromClause), \
			  attr("where_clause", WhereClause)
test_string = '''
 pkgs.pkgs_search_processed = 'N' AND pkgs.info_fcn_or_crid_of_mail_owner = fcn.crid
AND pkgs.current_month_flag = 'Y' AND payment_rec_arrived = 'Y' AND pkgs.dtc > p_cutoff_date
'''
# Your SQL string
test_string = '''
select col1, col2 
FROM table1 pkgs
	WHERE   pkgs.pkgs_search_processed = 'N' AND pkgs.info_fcn_or_crid_of_mail_owner = fcn.crid
			AND pkgs.current_month_flag = 'Y' AND payment_rec_arrived = 'Y' AND pkgs.dtc > p_cutoff_date
			AND COALESCE(pkgs.dum_unmanifested_or_postagedue, 'N') = 'Y'

'''
test_string = '''
select col1, col2 
FROM table1 pkgs
	WHERE  pkgs.pkgs_search_processed = 'N' AND pkgs.info_fcn_or_crid_of_mail_owner = fcn.crid
			AND pkgs.current_month_flag = 'Y' AND payment_rec_arrived = 'Y' AND pkgs.dtc > p_cutoff_date
			AND COALESCE(pkgs.dum_unmanifested_or_postagedue, 'N') = 'Y'
			AND pkgs.pkgs_search_processed = 'N' 
			AND pkgs.dtc > p_cutoff_date
			 AND COALESCE(pkgs.dup_unmanifested_or_postage_due, 'N') = 'Y'
			  AND ps.pkg_grp_id IS NULL
			  
'''
#pkgs.pkgs_search_processed = 'N' AND pkgs.dtc > p_cutoff_date AND COALESCE(pkgs.dup_unmanifested_or_postage_due, 'N') = 'Y' AND ps.pkg_grp_id IS NULL;
if __name__ == '__main__':
	# Parse the string using the defined grammar
	parsed_select = parse(test_string, SQLStatement)

	print("Selected Columns:", [str(column) for column in parsed_select.select_clause])
	print("From:", parsed_select.from_clause[0])
	pp(parsed_select.from_clause[1:])
	for join in parsed_select.where_clause:
		print(f"{join}")
		#print(f"Condition: {join.condition}")
