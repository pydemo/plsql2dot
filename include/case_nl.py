from pypeg2 import *

class RestOfLine(str):
    grammar = re.compile(r'.*?(?=\n|$)')

class WhenCondition(str):
    # Match any characters (including newlines) in a non-greedy way until 'THEN' is encountered
    grammar = re.compile(r'.+?(?=THEN|\n)', re.DOTALL)

class ThenExpression(str):
    grammar = "THEN", RestOfLine

class WhenThen(List):
    grammar = "WHEN", WhenCondition, ThenExpression

class CaseEnd(str):
    grammar = "END AS", word

class CaseStatement(List):
    grammar = "CASE", maybe_some(WhenThen), CaseEnd

# Define your test string:
test_string = '''
CASE    
    WHEN pr.dts_first IS NOT NULL 
    THEN 'test'
END AS manifest_date
'''

# Parse the test string:
parsed_case = parse(test_string.strip(), CaseStatement)
print(parsed_case)
