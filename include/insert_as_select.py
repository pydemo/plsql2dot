from pypeg2 import *
import re
try:
	from include import  case
except:
	import  case
try:

	from include import  where as where
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
	INSERT INTO package_search_temp (mid, manifest_date, file_name)
	SELECT
		COALESCE(fmp.mailowner_mailer_id, pr.mid) AS mid,
		COALESCE(fmp.crid_of_mail_owner, pr.crid) AS crid,
		CASE
			WHEN fmp.date_time_of_mailing IS NOT NULL THEN to_date(to_char(fmp.date_time_of_mailing, 'YYYY-MM-DD'), 'YYYY-MM-DD')
			WHEN pr.dts_first IS NOT NULL
				THEN to_date(to_char(pr.dts_first, 'YYYY-MM-DD'), 'YYYY-MM-DD') END AS manifest_date,
			fmp.file_name AS file_name,
			COALESCE(fmp.pic, pr.pic) AS pic,
			COALESCE(fmp.electronic_file_num, fmp.child_efn) AS efn,
			fmp.entry_facility_zipcode AS entry_zip,
			fmp.dest_zip_code AS destination_zip,
			coalesce(fmp.domestic_zone, pr.assd_zone) AS zone,
			coalesce(fmp.class_of_mail, pr.mail_mc_code) AS mail_class,
			fmp.weight AS manifest_weight,
			fmp.permit_no AS permit_number,
			coalesce(cast(fmp.eps_acc_num as varchar), fmp.permit_eps_acc_num) AS eps_account_number,
			pm.eps_tran_amt AS usps_recalculated_postage,
			pm.eps_tran_id AS eps_transaction_id,
			date_part('month', pm.eps_tran_dt) AS month,
			date_part('year', pm.eps_tran_dt) AS year,
			CASE
				WHEN pm.eps_tran_type = 'REFUND' OR pm.eps_tran_type = 'ADJUSTMENT' THEN
					CASE
						WHEN UPPER(nvl(pr.rootcauses, 'X')) LIKE '%WEIGHT%' OR
							 UPPER(nvl(pr.rootcauses, 'X')) LIKE '%DIMENSIONS%' OR
							 UPPER(nvl(pr.rootcauses, 'X')) LIKE '%D&CTS%' OR
							 UPPER(nvl(pr.rootcauses, 'X')) LIKE '%SPACING%' OR
							 UPPER(nvl(pr.rootcauses, 'X')) LIKE '%MISSTIPPED%' THEN 'Census'
						WHEN UPPER(nvl(pr.rootcauses, 'X')) LIKE '%USED REFUNDED%' THEN 'Used Refund Label'
						ELSE 'NA'
					END
				WHEN pm.eps_tran_type = 'PURCHASE' AND (UPPER(nvl(pr.rootcauses, 'X')) LIKE '%UNMANIFEST%' OR UPPER(nvl(pr.rootcauses, 'X')) LIKE '%DUPLICATES%') THEN
					CASE
						WHEN UPPER(nvl(pr.rootcauses, 'X')) LIKE '%UNMANIFEST%' THEN 'Unmanifested'
						WHEN UPPER(nvl(pr.rootcauses, 'X')) LIKE '%DUPLICATES%' THEN 'Duplicate'
						ELSE 'NA' END
					ELSE 'Manifest' END AS source_reports,
				CASE
					WHEN source_reports = 'Manifest' THEN 'MANIFEST'
					ELSE 'UNIVERSAL' END AS search_type,
			fmp.manifest_package_id AS manifest_package_id,
			pr.pkg_grp_id AS pkg_grp_id,
			p.processing_time AS dtc,
			p.processing_time AS dtu,
			fmp.rate_ind AS rate_ind
		FROM stage_pkgs_outbound pkgs
			LEFT OUTER JOIN facts_manifest_package fmp ON pkgs.manifest_package_id = fmp.manifest_package_id
			INNER JOIN facts_payment pm ON pkgs.quote_id = pm.submission_id
			INNER JOIN facts_pricing pr ON pkgs.quote_id = pr.quote_id
		WHERE pkgs.pkgs_search_processed = 'N' AND pkgs.info_fcn_or_crid_of_mail_owner = fcn.crid
			AND pkgs.current_month_flag = 'Y' AND payment_rec_arrived = 'Y' AND pkgs.dtc > p_cutoff_date
			AND COALESCE(pkgs.dum_unmanifested_or_postagedue, 'N') = 'Y'
			;
	
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
