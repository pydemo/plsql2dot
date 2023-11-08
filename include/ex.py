from pypeg2 import *
import re

# Define rest_of_line as a regex that matches any characters until the end of the line
rest_of_line = re.compile(r'.*?(?=\n|$)')

# Define the keywords
exception_keyword = Keyword("exception")
when_keyword = Keyword("when")
others_keyword = Keyword("others")
then_keyword = Keyword("then")
raise_keyword = Keyword("raise")
info_keyword = Keyword("info")

# Define a pattern that captures a generic SQL statement or PL/pgSQL code
sql_statement = re.compile(r".*?",re.DOTALL)

# Define a class for a block of code, which can be a series of SQL statements
class CodeBlock(List):
	grammar = csl(re.compile(r'[^,;]*'))

# Define a class for the exception block
class ExceptionBlock(List):
	
	grammar = exception_keyword, when_keyword, others_keyword, then_keyword, raise_keyword, info_keyword,attr("code", CodeBlock),';'

# Test string
test_string = '''
exception when others then
raise info 'SQLERRM=(%) SQLSTATE=(%) location_name=(%)', SQLERRM, SQLSTATE, v_location_name ;
'''

# Parse the test string
try:
	parsed_exception = parse(test_string, ExceptionBlock)
	print("Parsed Exception Block:")
	print(parsed_exception.code)  # The code captured between 'exception when others then' and 'raise info'
except Exception as e:
	print(e)
	raise
