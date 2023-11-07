from pypeg2 import *
import re

# Class to represent an identifier, such as table names
class Identifier(str):
	grammar = re.compile(r'[a-zA-Z_]\w*')

# DROP TABLE statement
class DropTableStatement(List):
	grammar = 'DROP TABLE', 'IF EXISTS', attr('table', Identifier), ';'



# Statement which can be either DROP TABLE or CREATE TABLE
class Statement(List):
	grammar = [DropTableStatement]

# Container for multiple statements
class SQLScript(List):
	grammar = maybe_some(Statement)

# Test string containing the SQL statements
test_string = '''
	DROP TABLE IF EXISTS package_search_temp;

'''
if __name__=='__main__':
	# Parse the test string
	parsed_sql = parse(test_string, SQLScript)

	# Iterate over parsed statements and print information
	for statement in parsed_sql:
		#print(statement, isinstance(statement[0], DropTableStatement))
		st=statement[0]
		if isinstance(st, DropTableStatement):
			print(f"DROP TABLE Statement, Table: {st.table}")
		else:
			raise Exception('Undefined statement type.')