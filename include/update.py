import sys
from pypeg2 import *
from pprint import pprint as pp
from include.base import  Base

try:

	from include import  is_null_where as where
except:
	import  where
import include.config.init_config as init_config  
apc = init_config.apc


e=sys.exit


# Define the patterns for matching
identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_\.]*")  # Identifiers can include dots for schema.table
string_literal = re.compile(r"'[^']*'")  # String literals
function_call = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*\(\)")  # Function call, like getdate()

class Base2(object):
	def get_type(self):
		return f'{__name__}.{self.__class__.__name__}'.replace('.','_')

		
# Define the structure for a simple assignment (e.g., column = 'value')
class Assignment(str):
	grammar = identifier, "=", [string_literal, function_call]

# Define the structure for the SET clause with one or more assignments
class SetClause(List):
	grammar = 'SET', csl(Assignment)

# Define the structure for the UPDATE statement
class UpdateStatement(List, Base):
	grammar = 'UPDATE', identifier, SetClause, where.WhereClause, optional(";")
	def get_dot(self):

		return f'{self.name} [shape="box", style=bold, color="lightpink", label="{self.tname} {apc.cntr.get(self)}" ];'
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
