from pypeg2 import *
from pprint import pprint as pp
rest_of_line= re.compile(r'.*?(?=\n|$)')
# Define a regex pattern to match identifiers (e.g., column names, table names)
identifier = re.compile(r'[a-zA-Z_]\w*')

# Define a class for a SQL identifier
class SqlIdentifier(str):
    grammar = identifier

# Define a class for a list of SQL identifiers (e.g., the columns in a SELECT)
class IdentifierList(List):
    grammar = csl(SqlIdentifier)

# Define classes for different types of JOINs
class JoinType(str):
    grammar = re.compile(r"LEFT OUTER JOIN|INNER JOIN")

class JoinCondition(str):
    grammar = "ON", rest_of_line

class JoinClause(List):
    grammar = attr("join_type", JoinType), attr("table", SqlIdentifier),identifier, attr("condition", JoinCondition)

# Define a class for the FROM clause
class FromClause(List):
    grammar = "FROM", SqlIdentifier,identifier, maybe_some(JoinClause)

# Define a class for the SELECT statement
class SelectStatement(List):
    grammar = "select", attr("columns", IdentifierList), attr("from_clause", FromClause)

# Define your test string
test_string = '''
select col1, col2 
FROM table1 pkgs
            LEFT OUTER JOIN table2 fmp ON pkgs.col1 = fmp.col2
            INNER JOIN tab3 pm ON pkgs.col4 = pm.col5
            INNER JOIN tab5 pr ON pkgs.col7 = pr.col8
'''

# Parse the test string
parsed_select = parse(test_string.strip(), SelectStatement)

# Access the parsed elements
print("Selected Columns:", [str(column) for column in parsed_select.columns])
print("From:", parsed_select.from_clause[0])
pp(parsed_select.from_clause[1:])
for join in parsed_select.from_clause[2:]:
    print(f"{join.join_type}: {join.table}")
    print(f"Condition: {join.condition}")
