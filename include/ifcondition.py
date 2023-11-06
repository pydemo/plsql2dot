from pypeg2 import *
import re

# This pattern will match any amount of whitespace including newlines
ws = re.compile(r'\s*')

# Patterns for identifiers and string literals
identifier = re.compile(r'[a-zA-Z_]\w*')
string_literal = re.compile(r"'(?:[^'\\]|\\.)*'")

# Patterns for matching
ws = re.compile(r'\s*')
rest_of_line = re.compile(r'.*?(?=\n|$)')
identifier = re.compile(r'[a-zA-Z_]\w*')
string_literal = re.compile(r"'(?:[^'\\]|\\.)*'")
eol = re.compile(r'.*?$', re.MULTILINE) 
# Comment pattern
rest_of_line = re.compile(r'.*?(?=\n|$)')
comm = re.compile(r'(commit;)')
class Comment(str):
	grammar = '--', rest_of_line

class Commit(str):
	grammar = comm
# A comparison in an 'if' statement
class Comparison(str):
	grammar = name(), ">", re.compile(r'\d+')

# The body of an 'if' statement that includes a commit
class IfBody(List):
	grammar = attr('comment',maybe_some(Comment)), attr('commit',maybe_some(Commit))

# 'if' condition block
class IfBlock(str):
    grammar = 'if', Comparison, 'then', attr('ifbody',IfBody), 'end if;'

# A Statement can be several things, for now, it is just an IfBlock
class Statement(List):
	grammar = attr('if_block', IfBlock)

# Code contains many Statements
class Code(List):
	grammar =  attr('code',maybe_some(Statement))

test_string = '''if v_cnt_search_pkgs > 0 then
	-- This includes census, duplicates and unmanifested adjustments
	commit;
end if;'''
if __name__ == "__main__":
	parsed_code = parse(test_string, Code)
	for statement in parsed_code:
		print(statement)  # Printing each 'if' block
		for body in statement.ifblock:
			print(statement.ifblock.ifbody.comment)
			print(statement.ifblock.ifbody.commit)
