import os, sys
from pypeg2 import *
from include import select
from include import statement
from include import insert_as_select as ias
from include import update 
from include import ex 

e=  sys.exit

class Base(object):
	def get_type(self):
		return self.__class__.__name__
	
	
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

class Assignment(str, Base):
	# Matches an assignment operation
	identifier_pattern = re.compile(r'\b[a-zA-Z_]\w*\b')
	rest_of_line = re.compile(r'.*?(?=\n|$)')
	grammar = identifier_pattern, ':=', rest_of_line


class Assignment2(str, Base):
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
	ctt.CreateTableStatement,  statement.Assignment,ias.InsertSelectStatement, update.UpdateStatement])
	
class IfStatement(List, Base):
	# Defines the structure of an if statement
	grammar = 'if',  Condition, 'then', \
			  LineExpression, optional('else'),  optional(LineExpression),\
			  'end if', ';'

class StatementExpression(List, Base):
	# Defines the different expressions that can be on a single line
	grammar = maybe_some([IfStatement, select.Select, statement.Assignment,  statement.Comment ])
	
class Block(List, Base):
	# Defines the structure of an if statement
	grammar = 'begin', StatementExpression, \
			  attr('ex',ex.ExceptionBlock),'end', ';',Literal('$$')
class Identifier(str):
    grammar = re.compile(r'[a-zA-Z_]\w*')

# Define the grammar for a datatype
class Datatype(str):
    grammar = re.compile(r'integer|varchar\(\d+\)')

# Define the grammar for an optional default value assignment
class DefaultValue(str):
    grammar = ':=', re.compile(r"'.*?'|\w+")

# Define the grammar for a single variable declaration
class VariableDeclaration(List, Base):
    grammar = attr('name', Identifier), attr('datatype', Datatype), optional(attr('default', DefaultValue)), ';'


#class VariableDeclaration_nodefault(List):
#	grammar = word,  data_type_pattern, ";"
class DeclarationExpression(List,Base):
	# Defines the different expressions that can be on a single line
	grammar = maybe_some([VariableDeclaration])
class Declarations(List, Base):
	grammar = 'as', Literal('$$'),"declare", DeclarationExpression
identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_$]*")
# Parameter definition within the procedure
class Type(Keyword):
	grammar = Enum(K("timestamp"), K("INTEGER"),("integer"), K("VARCHAR2"), K("DATE"))
	
class Parameter(List):
	grammar = attr("direction", optional("in")), attr("name", identifier), attr("data_type", Type)
class Language(str, Base):
	grammar = 'language', name()
class Security(str, Base):
	grammar = 'security', 'definer'
# A list of parameters separated by commas
class Parameters(List):
	grammar = optional(csl(Parameter))
class ProcOrFuncName(str):
	grammar = word
class FunctionOrProcedure(List, Base):
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
	v_location_name = 'Get count of unprocessed search pkgs';
	SELECT count(*) INTO v_cnt_search_pkgs from stage_pkgs_outbound WHERE pkgs_search_processed = 'N' AND ready_to_process = 'Y' AND payment_rec_arrived = 'Y' 
	AND dtc > p_cutoff_date;
	if v_cnt_search_pkgs > 0
	then
		-- This includes census, duplicates and unmanifested adjustments
		v_status := 'BEGIN pkgs search summary';
		insert into ppc_qlik_reports_log (log_date, report_name, module_name, status)
		values (getdate(), 'MANIFEST_SEARCH_REPORT', 'Summarizing Manifest Search', v_status);
				
		DROP TABLE IF EXISTS package_search_temp;
		CREATE TEMP TABLE package_search_temp (LIKE package_search_by_pic);
		
		v_location_name = 'Insert into package_search_temp';
		INSERT INTO package_search_temp (mid, manifest_date, file_name, pic, efn, entry_zip, destination_zip, zone, mail_class, manifest_weight, permit_number, pkgs_account_number, usps_recalculated_postage, eps_transaction_id, month, year, source_reports, search_type, manifest_package_id, epg_grp_id, dtc, dtu, rate_ind)
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
			AND COALESCE(pkgs.dum_unmanifested_or_postagedue, 'N') = 'Y';
		COMMIT;
		

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
		WHERE pkgs.pkgs_search_processed = 'N' AND pkgs.dtc > p_cutoff_date AND COALESCE(pkgs.dup_unmanifested_or_postage_due, 'N') = 'Y' AND ps.pkg_grp_id IS NULL;
		commit;
	
		-- Updating search processed status for packages
		v_location_name := 'Update stage_pkgs_outbound for pkgs_search_processed';
		UPDATE stage_pkgs_outbound
		SET pkgs_search_processed = 'Y', dtu = getdate()
		WHERE pkgs_search_processed = 'N' AND ready_to_process = 'Y' AND payment_rec_arrived = 'Y' AND COALESCE(dup_unmanifested_or_postagedue, 'N') != 'Y';
		commit;

		-- Updating search processed status for packages with certain conditions
		UPDATE stage_pkgs_outbound
		SET pkgs_search_processed = 'Y', dtu = getdate()
		WHERE pkgs_search_processed = 'N' AND COALESCE(dup_unmanifested_or_postagedue, 'N') = 'Y';
		commit;

		-- Inserting data into package_search_by_pic after processing
		v_location_name := 'Loading pkgs into package_search_by_pic';
		INSERT INTO package_search_by_pic(mid, crid, manifest_date, file_name, pic, efn, entry_zip, destination_zip, zone, mail_class, manifest_weight, permit_number, eps_account_number, usps_recalculated_postage, eps_transaction_id, month, year, source_reports, search_type, manifest_package_id, pkg_grp_id, dtc, dtu, rate_ind)
		SELECT mid, crid, manifest_date, file_name, pic, efn, entry_zip, destination_zip, zone, mail_class, manifest_weight, permit_number, eps_account_number, usps_recalculated_postage, eps_transaction_id, month, year, source_reports, search_type, manifest_package_id, pkg_grp_id, dtc, dtu, rate_ind 
		FROM package_search_temp;
		commit;
	
		v_location_name := 'Loading pkgs into package_search_by_efn';
		INSERT INTO package_search_by_efn(mid, crid, manifest_date, file_name, pic, efn, entry_zip, destination_zip, zone, mail_class, manifest_weight, permit_number, eps_account_number, usps_recalculated_postage, eps_transaction_id, month, year, source_reports, search_type, manifest_package_id, pkg_grp_id, dtc, dtu, rate_ind)
		SELECT mid, crid, manifest_date, file_name, pic, efn, entry_zip, destination_zip, zone, mail_class, manifest_weight, permit_number, eps_account_number, usps_recalculated_postage, eps_transaction_id, month, year, source_reports, search_type, manifest_package_id, pkg_grp_id, dtc, dtu, rate_ind 
		FROM package_search_temp;
		commit;

		v_status := 'Loaded pic, efn tables with pkgs';
		insert into ppc_qlik_reports_log (log_date, report_name, module_name, status)
		values (getdate(), 'MANIFEST_SEARCH_REPORT', 'pic, efn tables loaded', v_status);
		commit;

	else
		v_status := 'Manifested search pkgs not found';
		insert into ppc_qlik_reports_log (log_date, report_name, module_name, status)
		values (getdate(), 'MANIFEST_SEARCH_REPORT', 'Exiting Summarization', v_status);
		commit;

	end if;

exception when others then
raise info 'SQLERRM=(%) SQLSTATE=(%) location_name=(%)', SQLERRM, SQLSTATE, v_location_name;
end; 
$$

'''

parsed = parse(test_string, Code)

print('Input:')
print(test_string)
print('Parsed output:')
print('==============')

for c in parsed:
	
	#print( str(type(c)))
	if isinstance(c,FunctionOrProcedure):
		print('NAME:',c.name, c.get_type())
		#e()
	elif isinstance(c,Declarations):
		
		print('DECLARATIONS:')
		assert len(c)==1, len()
		for d in c[0]:
		
			if str(type(d)).endswith(".VariableDeclaration'>"):
				print('\tDVAR:',d.name)
			else:
				print(111, d, type(d))
	elif isinstance(c, Block):
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
					elif isinstance(le, ias.InsertSelectStatement):
						print(f"\t\tINSERT AS SELECT: {le.table}, LIKE: {le.columns}")
					
					elif isinstance(le, update.UpdateStatement):
						print(f"\t\tUPDATE: {le}")
					else:
						print(le, type(le))
			elif str(type(b)).endswith(".IfStatement'>"):
				print('\tIF_COND:', b)
			else:
				print(b, type(b))
			
	
		if isinstance(c.ex, ex.ExceptionBlock):
			print('EXCEPTION:', c.ex)
	else:
		print(c, str(type(c)))

from pprint import pprint as pp
from collections import OrderedDict
out={}
level=0
cnt=0
for aid,a in enumerate(parsed):
	#pp(a.__dict__)
	cnt +=1
	aname=str(a.__class__.__name__)
	akey=f'{aname}_{aid}'
	aobj={}
	out[aid]=dict(name=aname, attr=a.__dict__, obj=aobj, level=level, id=cnt, type=a.get_type())
	
	for bid,b in enumerate(a[0]):
		level =1
		cnt +=1
		bname=str(b.__class__.__name__)
		bkey=f'{bname}_{bid}'
		bobj={}
		attr =  b.__dict__
		attr.pop('position_in_text', None)
		aobj[bid]=dict( name=bname,attr=b.__dict__, obj=bobj, level=level, id=cnt)
		for cid,c in enumerate(b):
			level =2
			cnt +=1
			cname=str(c.__class__.__name__)
			ckey=f'{cname}_{cid}'
			cobj={}
			print(type(c)==str)
			if type(c) is str:
				attr=dict(type=type(c), value=str(c))
			else:
				attr =  c.__dict__
				attr.pop('position_in_text', None)
			for k,v in attr.items():
				attr[k]=str(v)
						
			bobj[cid]=dict( name=cname,attr=attr, obj=cobj, level=level, id=cnt, type= str(type(c)))
			for did,d in enumerate(c):
				level =3
				cnt +=1
				dname=str(d.__class__.__name__)
				dkey=f'{dname}_{did}'
				dobj={}
				
				if type(d) is str:
					attr=dict(type=type(d), value=str(d))
				else:
					attr =  d.__dict__
					attr.pop('position_in_text', None)
				for k,v in attr.items():
					attr[k]=str(v)
				if not (type(c) is str):
					cobj[did]=dict( name=dname,attr=attr, obj=dobj, level=level, id=cnt, type= str(type(d)))
print()
pp(out)
if 0:
	import json
	jfn='dump.json'
	with open(jfn, 'w') as f:
		# Serialize dict to a JSON formatted string and write it to a file
		json.dump(out, f, indent=4) 


header='''
digraph G {
    rankdir=TB;
    //node [shape=box, style=rounded];
	node [color=black];
start [label="Start", shape=tripleoctagon];

'''

footer=f'''

}}
'''
def get_name(p,c, id=0):
	name=f'{c.get_type()}_{p.index(c)}_{id}'
	print(name)
	return name
hdot=[]

if 0:
	for cid,c in enumerate(parsed):
		print(cid,parsed.index(c))
	e()
		
if 0:
	
	for k,v in out.items():
		hdot.append(f'{v["name"]} [label="{v["name"]}", shape=diamond ];')
else:

	hdot.append('//level 1')
	for cid,c in enumerate(parsed):
		name = get_name(parsed,c, cid)
		hdot.append(f'{name} [label="{name}", shape=box ];')
		
		for ccid,cc in enumerate(c):
			name = get_name(c,cc, ccid)
			hdot.append(f'\t{name} [label="{name}", shape=box ];')
			for cccid, ccc in enumerate(cc):
				try:
					name = get_name(cc,ccc,cccid)
					hdot.append(f'\t{name} [label="{name}", shape=box ];')
				except Exception as ex:
					print(c.get_type())
					print(cc.get_type())
					print(ccc)
					e(str(ex))
if 0:
	hdot.append('//level 2')
	for c in parsed:
		for cc in c:
			hdot.append(f'{cc.get_type()} [label="{cc.get_type()}", shape=box ];')
		
pp(hdot)

fdot=[]
if 0:
	
	for k,v in out.items():
		fdot.append(f'{v["name"]} [label="{v["name"]}", shape=diamond ];')
else:

	
	for cid, c in enumerate(parsed):
		if not cid:
			dfrom = 'start'
		else:
			dfrom = get_name(parsed,parsed[cid-1], cid-1) 
			

		dto = get_name(parsed,c, cid)
		fdot.append(f'{dfrom} -> {dto}[label="" ];')
		
		for ccid, cc in enumerate(c):
			ddto=get_name(c,cc, ccid) 
			
			fdot.append(f'{dto} -> {ddto}[label="" ];')
			for cccid,ccc in enumerate(cc):
				#dddto= ccc.get_type()
				dddto=get_name(cc,ccc, cccid)
				fdot.append(f'{ddto} -> {dddto}[label="" ];')
		
pp(fdot)
parsed[0]

#e(0)
dot=f'''
{header}
{os.linesep.join(hdot)}

// LINKS

{os.linesep.join(fdot)}
{footer}
'''
#//..\graphviz_diagram\gw\bin\dot -Tpng dotout.dot -o plsql.png; .\plsql.png
if 1:
	dotfn = 'dotout.dot'
	with open(dotfn, 'w') as fh:
		# Serialize dict to a JSON formatted string and write it to a file
		fh.write(dot) 