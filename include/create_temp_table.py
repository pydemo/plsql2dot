from pypeg2 import *
import re

import include.config.init_config as init_config  
apc = init_config.apc
from include.base import  Base

e=sys.exit

class Local(object):
	def set_fname(self): self.fname=__name__
# Class to represent an identifier, such as table names
class Identifier(str):
	grammar = re.compile(r'[a-zA-Z_]\w*')


# LIKE clause for CREATE TABLE
class LikeClause(List):
	grammar = 'LIKE', attr('like_table', Identifier)

# CREATE TABLE statement
class CreateTableStatement(List, Base,  Local):
	fname=__name__
	grammar = 'CREATE', 'TEMP TABLE', attr('table', Identifier), \
			  '(', attr('like_clause', LikeClause), ')', ';'
	
	def get_dot(self):
		return f'{self.name} [shape="box",  color="orange", label="{self.tname} {apc.cntr.get(self)}" ];'
# Statement which can be either DROP TABLE or CREATE TABLE
class Statement(List):
	grammar = [ CreateTableStatement]

# Container for multiple statements
class SQLScript(List):
	grammar = maybe_some(Statement)

# Test string containing the SQL statements
test_string = '''
	
	CREATE TEMP TABLE package_search_temp (LIKE package_search_by_pic);
'''

# Parse the test string
parsed_sql = parse(test_string, SQLScript)

# Iterate over parsed statements and print information
for statement in parsed_sql:
	#print(statement, isinstance(statement[0], DropTableStatement))
	st=statement[0]
	if isinstance(st, CreateTableStatement):
		print(f"CREATE TABLE Statement, Table: {st.table}, LIKE: {st.like_clause.like_table}")
	else:
		raise Exception('Undefined statement type.')