from pypeg2 import *
from include import select
from include import statement
class BooleanLiteral(Keyword):
	# Adjusting the regex to handle boolean literals
	K.regex = re.compile(r'"*\w+"*')
	grammar = Enum(K('true'), K('false'), K(r'"true"'), K(r'"false"'))

class CommitLiteral(str):
	# Handles the 'commit' keyword
	grammar = re.compile(r'commit', re.IGNORECASE), ';'

class LineFilter(Namespace):
	grammar = flag('inverted', "-"), name(), ":", attr('value', word)

class StringLiteral(str):
	# Matches a quoted string
	quoted_string = re.compile(r'"[^"]*"')
	grammar = quoted_string

class Comment(str):
	# Matches the rest of the line after a comment
	rest_of_line = re.compile(r'.*?(?=\n|$)')
	grammar = '--', rest_of_line

class Assignment(str):
	# Matches an assignment operation
	identifier_pattern = re.compile(r'\b[a-zA-Z_]\w*\b')
	rest_of_line = re.compile(r'.*?(?=\n|$)')
	grammar = identifier_pattern, ':=', rest_of_line

class Condition(str):
	# Matches a condition such as 'a > b'
	grammar = name(), re.compile(r'\s*[><=!]=?\s*'), word

from include import insert 
from include import drop 
from include import create_temp_table as ctt 
class LineExpression(List):
	# Defines the different expressions that can be on a single line
	grammar = maybe_some([LineFilter, BooleanLiteral, StringLiteral, Comment, Assignment, CommitLiteral, insert.InsertStatement, drop.DropTableStatement,\
	ctt.CreateTableStatement,  statement.Assignment])
	
class IfStatement(List):
	# Defines the structure of an if statement
	grammar = 'if',  Condition, 'then', \
			  LineExpression, \
			  'end if', ';'

class StatementExpression(List):
	# Defines the different expressions that can be on a single line
	grammar = maybe_some([IfStatement, select.Select, statement.Assignment,  statement.Comment,])
	
class Block(List):
	# Defines the structure of an if statement
	grammar = 'begin', StatementExpression, \
			  'end', ';'
class Identifier(str):
    grammar = re.compile(r'[a-zA-Z_]\w*')

# Define the grammar for a datatype
class Datatype(str):
    grammar = re.compile(r'integer|varchar\(\d+\)')

# Define the grammar for an optional default value assignment
class DefaultValue(str):
    grammar = ':=', re.compile(r"'.*?'|\w+")

# Define the grammar for a single variable declaration
class VariableDeclaration(List):
    grammar = attr('name', Identifier), attr('datatype', Datatype), optional(attr('default', DefaultValue)), ';'


#class VariableDeclaration_nodefault(List):
#	grammar = word,  data_type_pattern, ";"
class DeclarationExpression(List):
	# Defines the different expressions that can be on a single line
	grammar = maybe_some([VariableDeclaration])
class Declarations(List):
	grammar = 'as', Literal('$$'),"declare", DeclarationExpression
identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_$]*")
# Parameter definition within the procedure
class Type(Keyword):
	grammar = Enum(K("timestamp"), K("INTEGER"),("integer"), K("VARCHAR2"), K("DATE"))
	
class Parameter(List):
	grammar = attr("direction", optional("in")), attr("name", identifier), attr("data_type", Type)
class Language(str):
	grammar = 'language', name()
class Security(str):
	grammar = 'security', 'definer'
# A list of parameters separated by commas
class Parameters(List):
	grammar = optional(csl(Parameter))
class ProcOrFuncName(str):
	grammar = word
class FunctionOrProcedure(List):
	grammar = "create or replace",["function", "procedure"],attr("name", ProcOrFuncName)  , "(", attr("params", Parameters), ")",Language, Security
	
	
	
class Code(List):
	grammar = FunctionOrProcedure, Declarations, Block

test_string = '''
create or replace procedure sp_rs_refresh_pkgs_search (in p_processing_time timestamp, in p_cutoff_date timestamp)
language plpgsql security definer

as $$
declare
	v_cnt_search_pkgs integer;
	v_status varchar(50);
	v_location_name varchar(100) := 'sp_rs_refresh_pkgs_search';
begin
	--v_location_name = 'Get count of unprocessed search pkgs';
	v_location_name2 = 'Get count of gwsbw5sg search pkgs';

	SELECT count(*) INTO v_cnt_search_pkgs from stage_pkgs_outbound WHERE pkgs_search_processed = 'N' AND ready_to_process = 'Y' AND payment_rec_arrived = 'Y' AND dtc > p_cutoff_date;
	if test > 0 then
		--test
		v_status:='BEGIN pkgs search summary';
		insert into ppc_qlik_reports_log (log_date, report_name, module_name, status)
		values (getdate(), 'MANIFEST_SEARCH_REPORT', 'Summarizing Manifest Search', v_status);
						
		DROP TABLE IF EXISTS package_search_temp;
		CREATE TEMP TABLE package_search_temp (LIKE package_search_by_pic);
		v_location_name2 = 'Get count of gwsbw5sg search pkgs';
		commit;
	end if;
end;
'''

parsed = parse(test_string, Code)

print('Input:')
print(test_string)
print('Parsed output:')
print('==============')
for c in parsed:
	
	#print( str(type(c)))
	if str(type(c)).endswith(".FunctionOrProcedure'>"):
		print('NAME:',c.name)
	elif  str(type(c)).endswith(".Declarations'>"):
		
		print('DECLARATIONS:')
		assert len(c)==1, len()
		for d in c[0]:
		
			if str(type(d)).endswith(".VariableDeclaration'>"):
				print('\tDVAR:',d.name)
			else:
				print(111, d, type(d))
	elif str(type(c)).endswith(".Block'>"):
		print('BLOCK:')
		for b in c[0]:
			
			if str(type(b)).endswith(".Comment'>"):
				print('\tCOMMENT: --', b)
			elif str(type(b)).endswith(".Assignment'>"):
				print('\tASSIGN:', b)
			elif str(type(b)).endswith(".Select'>"):
				print('\tSELECT:', b)
			elif str(type(b)).endswith(".IfStatement'>"):
				print('\tIF_COND:', b)
				
				for le in b[1]:
					if str(type(le)).endswith(".Comment'>"):
						print('\t\tCOMMENT: --', le)
					elif str(type(le)).endswith(".Assignment'>"):
						print('\t\tASSIGN:', le)
					elif str(type(le)).endswith(".CommitLiteral'>"):
						print('\t\tCOMMIT:', le)
					elif str(type(le)).endswith(".InsertStatement'>"):
						print('\t\tINSERT:', le)
						print(f"\t\t\tTAB: {le.table}")
						print("\t\t\tCOLS:", [str(column) for column in le.columns])
						print("\t\t\tVALS:", [str(value) for value in le.values])
					elif isinstance(le, drop.DropTableStatement):
						print(f"\t\tDROP TABLE: {le.table}")
					elif isinstance(le, ctt.CreateTableStatement):
						print(f"\t\tCREATE TEMP TABLE: {le.table}, LIKE: {le.like_clause.like_table}")
					else:
						print(le, type(le))
			else:
				print(b, type(b))
			
	else:
		print(c, str(type(c)))
