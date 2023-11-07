from pypeg2 import *

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
    grammar = [QuotedString, WordWithDot]  # Use WordWithDot to allow dots in arguments

# Now we can define the overall SQL function grammar
class SQLFunction(List):
    grammar = FunctionName, "(", csl(FunctionArg), ")"


sql_function_string = """
to_char(fmp.date_time_of_mailing, 'YYYY-MM-DD')
"""

if 0:
	parsed_function = parse(sql_function_string, SQLFunction)

	print(parsed_function)
