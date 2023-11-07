from pypeg2 import *

# You would also need to define `rest_of_line` as before to capture the rest of the text on the line:
rest_of_line = re.compile(r'.*?(?=\n|$)')
identifier_pattern = re.compile(r'[a-zA-Z_]\w*')
class WhenCondition(str):
	grammar = re.compile(r'.+?(?=THEN)')

class ThenExpression(str):
	grammar = "THEN", rest_of_line

class WhenThen(List):
	grammar = "WHEN", WhenCondition, ThenExpression

class Case(List):
	grammar = "CASE", maybe_some(WhenThen), "END AS", identifier_pattern



# Now you can define your test string:
test_string = '''
	CASE
		WHEN fmp.date_time_of_mailing IS NOT NULL THEN 'test'
		WHEN pr.dts_first IS NOT NULL THEN 'test2'
	END AS manifest_date
'''

# And then you can parse the test string:
try:
	parsed_case = parse(test_string, Case)
	print(parsed_case)
except ParsingError as pe:
	print("Parsing Error:", pe)
