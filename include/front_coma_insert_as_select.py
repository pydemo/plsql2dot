from pypeg2 import *
import re
try:
	from include import  case
except:
	import  case
try:

	from include import  where
except:
	import  where
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
	grammar = [FunctionCall,  case.Case, StringLiteral, Identifier]


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
	grammar = re.compile(r".+?(?=,|FROM\s)", re.IGNORECASE | re.DOTALL)

class SelectExpressionList(List):
	grammar = csl(SelectExpression)
class SqlIdentifier(str):
	identifier = re.compile(r'[a-zA-Z_]\w*')
	grammar = identifier

# Define classes for different types of JOINs
class JoinType(str):
	grammar = re.compile(r"LEFT OUTER JOIN|INNER JOIN")

class JoinCondition(str):
	rest_of_line= re.compile(r'.*?(?=\n|$)')
	grammar = "ON", optional(rest_of_line)

class JoinClause(List):
	alias = re.compile(r'[a-zA-Z_]\w*')
	rest_of_line= re.compile(r'.*?(?=\n|$)')
	rest_of_line = re.compile(r'.*?(?=\n|$)')
	grammar = attr("join_type", JoinType), attr("table", name()),optional(name()), "ON", optional(rest_of_line)
	
	
# Class for the select statement within an insert statement
class SelectStatement(List):
	grammar = SelectKword, attr('expressions', SelectExpressionList), FromKword, attr('table', name()), optional(attr('alias', name())),\
	optional(attr('join',maybe_some(JoinClause))), optional(attr('where',maybe_some(where.WhereClause)))

# Class for the full insert-select statement
class InsertSelectStatement(List):
	grammar = InsertKword, attr('table', Identifier), attr('columns', ColumnList), \
			  attr('select', SelectStatement),';'

# The SQL insert-select string to parse
test_string = '''
		INSERT INTO package_search_temp(mid, crid, manifest_date, file_name, pic, efn, entry_zip, destination_zip, zone, mail_class, manifest_weight, permit_number, eps_account_number, usps_recalculated_postage, eps_transaction_id, month, year, source_reports, search_type, manifest_package_id, pkg_grp_id, dtc, dtu, rate_ind)
		SELECT pr.mid
			  ,pr.crid
			  ,CASE
				  WHEN pr.dts_first IS NOT NULL
				  THEN to_date(to_char(pr.dts_first, 'YYYY-MON-DD'), 'YYYY-MON-DD') 
				  ELSE to_date(to_char(pr.dts_first, 'YYYY-MON-DD'), 'YYYY-MON-DD')
			   END AS manifest_date
			  ,pr.file_name
			  ,pr.pic
			  ,pr.electronic_file_num AS efn
			  ,COALESCE(pr.assd_zc_origin, pr.zc_origin) AS entry_zip
			  ,COALESCE(pr.assd_zc_dest, pr.zc_dest) AS destination_zip
			  ,pr.assd_zone AS zone
			  ,pr.assd_mc_code AS mail_class
			  ,pr.weight AS manifest_weight
			  ,pr.permit_no AS permit_number
			  ,cast(pr.eps_acc_num as varchar) AS eps_account_number
			  ,pr.postage_delta AS usps_recalculated_postage
			  ,NULL AS eps_transaction_id
			  ,date_part('month', manifest_date) AS month
			  ,date_part('year', manifest_date) AS year
			  ,CASE 
				  WHEN UPPER(nvl(pr.rootcauses, 'X')) LIKE '%UNMANIFESTED%' THEN 'Unmanifested'
				  WHEN UPPER(nvl(pr.rootcauses, 'X')) LIKE '%DUPLICATE%' THEN 'Duplicate'
				  ELSE 'NA' 
			   END AS source_reports
			  ,CASE 
				  WHEN source_reports != 'NA' THEN 'UNIVERSAL' 
				  ELSE 'NA' 
			   END AS search_type
			  ,pr.manifest_package_id
			  ,pr.pkg_grp_id
			  ,p.processing_time AS dtc
			  ,p.processing_time AS dtu
			  ,pr.rate_ind
		FROM stage_pkgs_outbound pkgs
		INNER JOIN facts_pricing pr ON pkgs.quote_id = pr.quote_id
		LEFT OUTER JOIN package_search_by_pic ps ON pr.pkg_grp_id = ps.pkg_grp_id AND ps.search_type = 'UNIVERSAL'
		WHERE pkgs.pkgs_search_processed = 'N' AND pkgs.dtc > p_cutoff_date AND COALESCE(pkgs.dup_unmanifested_or_postage_due, 'N') = 'Y' 
		AND ps.pkg_grp_id IS NULL;
	
'''

test_string = '''
	INSERT INTO package_search_temp(mid, crid, manifest_date, file_name, pic, efn, entry_zip, destination_zip, zone, mail_class, manifest_weight, permit_number, eps_account_number, usps_recalculated_postage, eps_transaction_id, month, year, source_reports, search_type, manifest_package_id, pkg_grp_id, dtc, dtu, rate_ind)
	SELECT pr.mid
		  ,pr.crid
		  ,CASE
			  WHEN pr.dts_first IS NOT NULL
			  THEN to_date(to_char(pr.dts_first, 'YYYY-MON-DD'), 'YYYY-MON-DD') 
			  ELSE to_date(to_char(pr.dts_first, 'YYYY-MON-DD'), 'YYYY-MON-DD')
		   END AS manifest_date
		  ,pr.file_name
		  ,pr.pic
		  ,pr.electronic_file_num AS efn
		  ,COALESCE(pr.assd_zc_origin, pr.zc_origin) AS entry_zip
		  ,COALESCE(pr.assd_zc_dest, pr.zc_dest) AS destination_zip
		  ,pr.assd_zone AS zone
		  ,pr.assd_mc_code AS mail_class
		  ,pr.weight AS manifest_weight
		  ,pr.permit_no AS permit_number
		  ,cast(pr.eps_acc_num as varchar) AS eps_account_number
		  ,pr.postage_delta AS usps_recalculated_postage
		  ,NULL AS eps_transaction_id
		  ,date_part('month', manifest_date) AS month
		  ,date_part('year', manifest_date) AS year
		  ,CASE 
			  WHEN UPPER(nvl(pr.rootcauses, 'X')) LIKE '%UNMANIFESTED%' THEN 'Unmanifested'
			  WHEN UPPER(nvl(pr.rootcauses, 'X')) LIKE '%DUPLICATE%' THEN 'Duplicate'
			  ELSE 'NA' 
		   END AS source_reports
		  ,CASE 
			  WHEN source_reports != 'NA' THEN 'UNIVERSAL' 
			  ELSE 'NA' 
		   END AS search_type
		  ,pr.manifest_package_id
		  ,pr.pkg_grp_id
		  ,p.processing_time AS dtc
		  ,p.processing_time AS dtu
		  ,pr.rate_ind
	FROM stage_pkgs_outbound pkgs
	INNER JOIN facts_pricing pr ON pkgs.quote_id = pr.quote_id
	LEFT OUTER JOIN package_search_by_pic ps ON pr.pkg_grp_id = ps.pkg_grp_id AND ps.search_type = 'UNIVERSAL'
	WHERE pkgs.pkgs_search_processed = 'N' AND pkgs.dtc > p_cutoff_date AND COALESCE(pkgs.dup_unmanifested_or_postage_due, 'N') = 'Y' 
	AND ps.pkg_grp_id IS NULL;
	
'''

if __name__ == '__main__':
	# Parse the test string
	parsed_insert_select = parse(test_string, InsertSelectStatement)

	# Pretty-print the parsed insert-select statement
	print(f"TABLE: {parsed_insert_select.table}")
	print("COLUMNS:", [str(column) for column in parsed_insert_select.columns])
	print("SELECT EXP:", [str(expression) for expression in parsed_insert_select.select.expressions])
	print(f"JOIN: {parsed_insert_select.select.join}")
	print(f"FROM TABLE: {parsed_insert_select.select.table}")
	print(f"WHERE: {parsed_insert_select.select.where}")
