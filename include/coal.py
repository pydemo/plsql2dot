from pypeg2 import *
import re

# Keyword definition helper for case-insensitive matching
def ci_keyword(kword):
    return re.compile(r'\b' + kword + r'\b', re.IGNORECASE)

# Regular expression patterns for different parts of the statement
identifier_pattern = re.compile(r'[a-zA-Z_]\w*')
string_literal_pattern = re.compile(r"'(?:[^'\\]|\\.)*'")  # Handles escaped quotes within strings
function_call_pattern = re.compile(r'\w+\(\)')

# Class for table name, column names, and function calls (like getdate())
class Identifier(str):
    grammar = identifier_pattern

class FunctionCall(str):
    grammar = function_call_pattern

# Class for string literals within the values clause
class StringLiteral(str):
    grammar = string_literal_pattern

# Class for a single value, which can be a string literal or a function call
class Value(str):
    grammar = [FunctionCall, StringLiteral, Identifier]

# Class for the list of values to be inserted
class ValueList(List):
    grammar = '(', csl(Value), ')'

# Class for the list of columns in the insert statement
class ColumnList(List):
    grammar = '(', csl(Identifier), ')'

# Class to handle case-insensitive keywords for insert and select
class InsertKword(str):
    grammar = ci_keyword("insert"), ci_keyword("into")

class SelectKword(str):
    grammar = ci_keyword("select")

class FromKword(str):
    grammar = ci_keyword("from")

# Class for aliases in the select statement
class Alias(str):
    grammar = optional(ci_keyword("as")), identifier_pattern

# Class for a select expression, which could be a function call, an identifier, or an alias
class SelectExpression(str):
    grammar = re.compile(r".+?(?=,|FROM)", re.IGNORECASE | re.DOTALL)

class SelectExpressionList(List):
    grammar = csl(SelectExpression)

# Class for the select statement within an insert statement
class SelectStatement(List):
    grammar = SelectKword, attr('expressions', SelectExpressionList), FromKword, attr('table', name())

# Class for the full insert-select statement
class InsertSelectStatement(List):
    grammar = InsertKword, attr('table', Identifier), attr('columns', ColumnList), \
              attr('select', SelectStatement), ';'

# The SQL insert-select string to parse
test_string = '''
    INSERT INTO package_search_temp (mid, manifest_date, file_name)
    SELECT
        COALESCE(fmp.mailowner_mailer_id, pr.mid) AS mid,
        pr.pkg_grp_id AS pkg_grp_id,
        p.processing_time AS dtc,
        p.processing_time AS dtu,
        fmp.rate_ind AS rate_ind
    FROM ssometable_name;
'''

if __name__ == '__main__':
    # Parse the test string
    parsed_insert_select = parse(test_string, InsertSelectStatement)

    # Pretty-print the parsed insert-select statement
    print(f"Table: {parsed_insert_select.table}")
    print("Columns:", [str(column) for column in parsed_insert_select.columns])
    print("Select Expressions:", [str(expression) for expression in parsed_insert_select.select.expressions])
    print(f"From Table: {parsed_insert_select.select.table}")
