from pypeg2 import *
import re
import pypeg2
pypeg2.print_trace = True
from pypeg2 import *
try:
	from include import  one_func
except:
	import  one_func

# A regex pattern that matches a word which may contain dots
class WordWithDot(str):
    grammar = re.compile(r'[\w\.]+')

# A class for the function name which is a simple word
class FunctionName(WordWithDot):
    pass

# A class for a string enclosed in single quotes
class QuotedString(str):
    grammar = "'", re.compile(r"[^']+"), "'"  # modified to match any character except the single quote

# A class for function arguments, you can add more variations if needed
class FunctionArg(List):
    grammar = attr('value',[QuotedString, one_func.SQLFunction] ) # Use WordWithDot to allow dots in arguments

# Now we can define the overall SQL function grammar
class SQLFunction(List):
    grammar = attr('name', FunctionName), "(", attr('arguments',csl(FunctionArg)), ")"

# Parsing the provided test string
test_string = "to_date(to_char(fmp.date_time_of_mailing, 'YYYY-MM-DD'), 'YYYY-MM-DD')"

if __name__ == '__main__':
	parsed_expression = parse(test_string, SQLFunction)
	# Output the parsed components
	print(f"Function: {parsed_expression.name}")
	print("Arguments:", [arg.value for arg in parsed_expression.arguments])

