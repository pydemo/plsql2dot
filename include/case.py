from pypeg2 import *
try:
	from include import  func_func
except:
	import  func_func
# You would also need to define `rest_of_line` as before to capture the rest of the text on the line:
rest_of_line = re.compile(r'.*?(?=\n|$)')
identifier_pattern = re.compile(r'[a-zA-Z_]\w*')
class RestOfLine(str):
    grammar = re.compile(r'.*?(?=\n|$)')

class WhenCondition(str):
    # Match any characters (including newlines) in a non-greedy way until 'THEN' is encountered
    grammar = re.compile(r'.+?(?=THEN|\n)', re.DOTALL)

class ThenExpression(str):
	grammar =  [func_func.SQLFunction, rest_of_line]
ws = re.compile(r'\s*')
class WhenThen(List):
	grammar = "WHEN", WhenCondition,ws,"THEN", ThenExpression

class Case(List):
	grammar = "CASE", maybe_some(WhenThen), "END AS", identifier_pattern



# Now you can define your test string:
test_string = '''
			CASE
				WHEN fmp.date_time_of_mailing IS NOT NULL THEN to_date(to_char(fmp.date_time_of_mailing, 'YYYY-MM-DD'), 'YYYY-MM-DD')
				WHEN pr.dts_first IS NOT NULL
					THEN to_date(to_char(pr.dts_first, 'YYYY-MM-DD'), 'YYYY-MM-DD') END AS manifest_date
'''

# And then you can parse the test string:

if __name__=="__main__":
	parsed_case = parse(test_string, Case)
	print(parsed_case)

