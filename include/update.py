from pypeg2 import *
try:

	from include import  is_null_where as where
except:
	import  where
# Define the patterns for matching
identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_\.]*")  # Identifiers can include dots for schema.table
string_literal = re.compile(r"'[^']*'")  # String literals
function_call = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*\(\)")  # Function call, like getdate()

# Define the structure for a simple assignment (e.g., column = 'value')
class Assignment(str):
	grammar = identifier, "=", [string_literal, function_call]

# Define the structure for the SET clause with one or more assignments
class SetClause(List):
	grammar = 'SET', csl(Assignment)

# Define the structure for the UPDATE statement
class UpdateStatement(List):
	grammar = 'UPDATE', identifier, SetClause, where.WhereClause, optional(";")

# Your SQL update statement
update_statement = '''
	UPDATE stage_pkgs_outbound
	SET pkgs_search_processed = 'Y', dtu = getdate()
	WHERE pkgs_search_processed = 'N' AND ready_to_process = 'Y' AND payment_rec_arrived = 'Y' AND COALESCE(dup_unmanifested_or_postagedue, 'N') != 'Y';
'''
if __name__=="__main__":
	# Parse the SQL statement using the defined grammar
	parsed_update_statement = parse(update_statement, UpdateStatement)

	# Printing the parsed statement for clarity
	print(parsed_update_statement)
