import re, os, sys, math
from pypeg2 import *
from pprint import pprint as pp
import include.config.init_config as init_config  

init_config.init(**{})
apc = init_config.apc


from include import select
from include import statement
from include import insert_as_select as ias
from include import update 
from include import ex 

from include import insert 
from include import drop 
from include import create_temp_table as ctt 
from include.base import  clean_for_html_display, split_equally_by_words, Base, BaseBase
from include.base import  Comment, String, StringVal, StringTable
e=  sys.exit
class Start(object):
	name='start'
class Local(object):
	def set_fname(self): self.fname=__name__
class BooleanLiteral(Keyword):
	# Adjusting the regex to handle boolean literals
	K.regex = re.compile(r'"*\w+"*')
	grammar = Enum(K('true'), K('false'), K(r'"true"'), K(r'"false"'))

class CommitLiteral(str, String, Local):
	# Handles the 'commit' keyword
	grammar = re.compile(r'commit', re.IGNORECASE), ';'

	def get_dot(self):
		print('CommitLiteral', apc.cntr.get(self))
		return f'{self.name} [shape="septagon", style=bold, color="blue", label="Commit {apc.cntr.get(self)}" ];'
	
class LineFilter(Namespace):
	grammar = flag('inverted', "-"), name(), ":", attr('value', word)

class StringLiteral(str):
	# Matches a quoted string
	quoted_string = re.compile(r'"[^"]*"')
	grammar = quoted_string


		
class Assignment(str, Base, Local):
	# Matches an assignment operation
	identifier_pattern = re.compile(r'\b[a-zA-Z_]\w*\b')
	rest_of_line = re.compile(r'.*?(?=\n|$)')
	grammar = attr('identifier', identifier_pattern), ':=', attr('value',rest_of_line)
	def _get_dot(self):
		return f'{self.name} [shape="box",  color="gray", label="AAAAAAAAAAAAAAAAAAAAAAAAAA {self.tname} {apc.cntr.get(self)}\n>{str(self)}<" ];'

class Assignment2(str, Base, Local):
	# Matches an assignment operation
	identifier_pattern = re.compile(r'\b[a-zA-Z_]\w*\b')
	rest_of_line = re.compile(r'.*?(?=\n|$)')
	grammar = identifier_pattern, ':=', rest_of_line

class LineExpression(List, Base, Local):
	# Defines the different expressions that can be on a single line
	grammar = maybe_some([LineFilter, BooleanLiteral, StringLiteral, Comment, Assignment, CommitLiteral, insert.InsertStatement, drop.DropTableStatement,\
	ctt.CreateTableStatement,  statement.Assignment,ias.InsertSelectStatement, update.UpdateStatement])
	def get_dot(self):
		return f'{self.name} [shape="box",  color="black", label="{self.label} {apc.cntr.get(self)}" ];'

	def init(self, parent, lid):
		Base.init(self,parent, lid)
		#assert type(parent) in [Condition]

	def show_children(self, parent, hdot, fdot):
		
		
		cfdot =  []
		#attr=self.parent.attr
		bids=[]
		#cfrom = self
		cfrom=parent
		if 1:
			for cid,c in enumerate(self):

				if 1:
					comm=None
					if type(cfrom) in [Comment]:
						comm=cfrom
						#print(111, cid, comm.lid, type(c), parent)
						
						#e()
						if comm.lid == 0:
							cfrom=parent
						else:
							cfrom=parent[comm.lid-1]
							
					c.get_full_dot(self, cfrom.name, cid, hdot, cfdot, self.level+cid+1)
					if comm:
						cfdot.append(f'{comm.name} -> {c.name}[label="comm ({self.level}) " style=dashed color="lightblue"];')
						comm=None
				cfrom = c
		
			bids.append([apc.gid, c])
		
		#self.get_end_if_dot(bids,hdot, cfdot )
		self.get_subgraph(cfdot, fdot)
		#end_if= f'end_if_{self.parent.gid}'
		#fdot.append(f'{end_if} -> end;')

	def get_subgraph(self, cfdot, fdot):
		fdot.append(f'''
		subgraph Cluster_{self.name}{{
		edge [color=blue, style=dashed];
		node [color=lightblue, style=filled];
		''')
		fdot +=cfdot
		fdot.append('''
		}''')
		
	def get_end_if_dot(self,bids,hdot, fdot ):
		end_if= f'end_if_{self.parent.gid}'
		hdot.append(f'{end_if} [shape="ellipse",  color="black", label="End If" ];')
		fdot.append(f'{apc.all[bids[0][0]].name} -> {end_if}[label="{bids[0][1]}" ];')
		#fdot.append(f'{apc.all[bids[1][0]].name} -> {end_if}[label="{bids[1][1]}" ];')
		

class Condition(str, Base, Local):
	# Matches a condition such as 'a > b'
	identifier_pattern = re.compile(r'\b[a-zA-Z_]\w*\b')
	cond=re.compile(r'\s*[><=!]=?\s*')
	grammar = attr('left', identifier_pattern),attr('cond',cond), attr('right',word)
	def init(self, parent, lid):
		Base.init(self,parent, lid)
		assert type(parent) in [IfStatement]
		
	def get_dot(self):

		return f'{self.name} [shape="box",  color="black", label="{self.label} {apc.cntr.get(self)}\n{self.attr["left"]}{self.attr["cond"]}{self.attr["right"]}" ];'
	def show_attr(self, hdot, fdot):
		pass
	def show_children(self, cfrom, hdot, fdot):
		base_classes = self.__class__.__bases__
		assert str in base_classes, base_classes
		cfdot =  []
		attr=self.parent.attr
		bids=[]
		for cid,ck in enumerate(attr):
			c=attr[ck]
			#print (self.name, type(c), f'>{c}<')

			#print (self.name, type(c))
			if not type(c) in [LineExpression]:
				print(type(c))
				pp(attr.keys())
				pp(self.attr)
				e()
			c.get_full_dot(self, self.name, cid, hdot, cfdot, self.level+1, label=ck) #True/False
			cfrom = c.name
			bids.append([apc.gid, ck])

		self.get_end_if_dot(bids,hdot, cfdot )
		self.get_subgraph(cfdot, fdot)
		end_if= f'end_if_{self.parent.gid}'
		fdot.append(f'{end_if} -> end;')

	def get_subgraph(self, cfdot, fdot):
		fdot.append('''
		subgraph Cluster_O{
		edge [color=blue, style=dashed];
		node [color=lightblue, style=filled];
		''')
		fdot +=cfdot
		fdot.append('''
		}''')
		
	def get_end_if_dot(self,bids,hdot, fdot ):
		end_if= f'end_if_{self.parent.gid}'
		hdot.append(f'{end_if} [shape="ellipse",  color="black", label="End If" ];')
		fdot.append(f'{apc.all[bids[0][0]].name} -> {end_if}[label="{bids[0][1]}" ];')
		fdot.append(f'{apc.all[bids[1][0]].name} -> {end_if}[label="{bids[1][1]}" ];')
		
		

		
class IfStatement(List, Base, Local):
	# Defines the structure of an if statement
	grammar = 'if',  Condition, 'then', \
			  attr('True',LineExpression), optional('else'),  attr('False',LineExpression),\
			  'end if', ';'
	def get_dot(self):
		
		return f'{self.name} [shape="diamond", style=bold, color="black", label="{self.label} {apc.cntr.get(self)}" ];'
	def show_attr(self, hdot, fdot):
		pass



class StatementExpression(List, Base, Local):
	# Defines the different expressions that can be on a single line
	grammar = maybe_some([IfStatement, select.Select, statement.Assignment,  statement.Comment ])
	
class Block(List, Base, Local):
	# Defines the structure of an if statement
	grammar = 'begin', StatementExpression, \
			  ex.ExceptionBlock,'end', ';',Literal('$$')
	def get_dot(self):
		
		return f'{self.name} [shape="box", style=bold, color="black", label="{self.label} {apc.cntr.get(self)}" ];'
		

	def init(self, parent, lid):
		Base.init(self,parent, lid)
		#assert type(parent) in [apc.parsed]
		
	def show_attr(self, hdot, fdot):
		pass
	def show_children(self, cfrom, hdot, fdot):
		base_classes = self.__class__.__bases__
		assert not str in base_classes, base_classes
		cfdot =  []
		#attr=self.parent.attr
		#bids=[]
		for cid,c in enumerate(self):
			
			c.get_full_dot(self, self.name, cid, hdot, cfdot, self.level+1)
			cfrom = c
			#bids.append([apc.gid, ck])

		
		self.get_subgraph(cfdot, fdot)
		#end_if= f'end_if_{self.parent.gid}'
		#fdot.append(f'{end_if} -> end;')

	def get_subgraph(self, cfdot, fdot):
		fdot.append(f'''
		subgraph Cluster_{self.name}{{
		edge [color=blue, style=dashed];
		node [color=lightblue, style=filled];
		''')
		fdot +=cfdot
		fdot.append('''
		}''')
		#pp(cfdot)
		#e()
		

		
		
		
class Identifier(str):
	grammar = re.compile(r'[a-zA-Z_]\w*')

# Define the grammar for a datatype
class Datatype(str):
	grammar = re.compile(r'integer|varchar\(\d+\)')

# Define the grammar for an optional default value assignment
class DefaultValue(str):
	grammar = ':=', re.compile(r"'.*?'|\w+")

# Define the grammar for a single variable declaration
class VariableDeclaration(List, Base, Local):
	grammar = attr('name', Identifier), attr('datatype', Datatype), optional(attr('default', DefaultValue)), ';'
	def get_dot(self):
		
		return f'<TR><TD >{self.attr["name"]}</TD><TD >{self.attr["datatype"]}</TD><TD >{self.attr.get("default","")}</TD></TR>'


class DeclarationExpression(List,Base, Local):
	# Defines the different expressions that can be on a single line
	grammar = maybe_some([VariableDeclaration])

	def show_children(self, cfrom, hdot, fdot):
		out=[]
		for cid,c in enumerate(self):
			c.init(self, cid)
			#pp(c.attr)
			#e()
			out.append(c.get_dot())
		hdot.append( f'''
		{self.name} [shape=none, margin=0, label=<
			<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
				<TR><TD >Variable</TD><TD >Datatype</TD><TD >Default</TD></TR>
				{os.linesep.join(out)}
			</TABLE>
		>];''')
		if 0:
			fdot.append(f'{self.dfrom} -> {self.name}[label="{self.tname} ({self.level})" ];')



class Declarations(List, Base, Local):
	grammar = 'as', Literal('$$'),"declare", DeclarationExpression
	def get_dot(self):
		
		return f'{self.name} [shape="box", color="gray", label="DECLARE {apc.cntr.get(self)}" ];'
	
identifier = re.compile(r"[a-zA-Z_][a-zA-Z0-9_$]*")
# Parameter definition within the procedure
class Type(Keyword):
	grammar = Enum(K("timestamp"), K("INTEGER"),("integer"), K("VARCHAR2"), K("DATE"))
	
class Parameter(List, Base, Local):
	grammar = attr("direction", optional("in")), attr("name", identifier), attr("data_type", Type)
	def get_dot(self):
		
		return f'<TR><TD >{self.attr["direction"]}</TD><TD >{self.attr.get("name")}</TD><TD >{self.attr.get("data_type")}</TD></TR>'

	
language_keyword = Keyword("language")

class Language(str, Base, Local):
	grammar = language_keyword, name()
class Security(str, String, Local):
	grammar = Keyword("security"), Keyword("definer")
# A list of parameters separated by commas
class Parameters(List, Base, Local):
	grammar = optional(csl(Parameter))
	
	def show_children(self, cfrom, hdot, fdot):
		out=[]
		for cid,c in enumerate(self):
			c.init(self, cid)
			c.level=self.level+1
			#pp(c.attr)
			#e()
			out.append(c.get_dot())
		hdot.append( f'''
		{self.name} [shape=none, margin=0, label=<
			<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
				<TR><TD >Direction</TD><TD >Name</TD><TD >DataType</TD></TR>
				{os.linesep.join(out)}
			</TABLE>
		>];''')
		if 0:
			fdot.append(f'{self.dfrom} -> {self.name}[label="{self.tname} ({self.level})" ];')

	
class ProcOrFuncName(str):
	grammar = word
class FunctionOrProcedure(List, Base, Local):
	grammar = "create or replace",["function", "procedure"],attr("name", ProcOrFuncName)  , "(", attr("params", Parameters), ")",Language, Security
	def get_dot(self):
		return f'{self.name} [shape="septagon", style=bold, color="black", label="Procedure" ];'
	def get_full_dot(self, parent, dfrom, lid, hdot, fdot, level, label=''):

		self.init(parent, lid)
		self.dfrom=dfrom
		
		self.level=level
		#hdot.append(f'{self.get_dot()}')
		cfrom=self.name
		if 0:
			dto, _ = self.get_name()
			fdot.append(f'{self.dfrom} -> {dto}[label="{label} ({self.level}) " ];')


		#self.show_children(cfrom, hdot, fdot)
		self.get_dot_attr(hdot, fdot)
	def get_dot_attr(self, hdot, fdot):
		
		self.attr['params'].get_full_dot(self, 'start', 3, hdot, fdot, 1, label='')
		if 0:
			if self.attr:
			
				print(self.gid)
				out=[]
				for k, v in self.attr.items():
					out.append(f'<TR><TD>{k}</TD><TD>{repr(v)[:30]}</TD></TR>')
					print(k,v, type(v))
					#if type(v) in [str]:
					#	e()
				hdot.append(f'''
			TableNode_{self.gid} [shape=none, margin=0, label=<
				<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
					
					{os.linesep.join(out)}
				</TABLE>
			>];''')			
				cfrom, clabel = self.get_name()
				fdot.append(f'start -> TableNode_{self.gid}[label="attr2" ];')
class Code(List, Base, Local):
	grammar = attr('proc',FunctionOrProcedure), Declarations, Block

	def get_full_dot(self, parent, dfrom, lid, hdot, fdot, level, label=''):

		self.init(parent, lid)
		self.dfrom=dfrom
		
		self.level=level
		hdot.append(f'start [label="Start {self.attr["proc"].name}", shape=tripleoctagon];')
		cfrom=self.name
		#pp(self.attr['proc'].name)
		#e()
		#
		if 0:
			dto, _ = self.get_name()
			fdot.append(f'start -> {dto}[label="{label} ({self.level}) " ];')


		self.show_children(Start(), hdot, fdot)
		self.get_dot_attr(hdot, fdot)

	def get_dot_attr(self, hdot, fdot):
		
		self.attr['proc'].get_full_dot(self, 'start', 3, hdot, fdot, 0, label='')
		if 0:
			if self.attr:
			
				print(self.gid)
				out=[]
				for k, v in self.attr.items():
					out.append(f'<TR><TD>{k}</TD><TD>{repr(v)[:30]}</TD></TR>')
					print(k,v, type(v))
					#if type(v) in [str]:
					#	e()
				hdot.append(f'''
			TableNode_{self.gid} [shape=none, margin=0, label=<
				<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
					
					{os.linesep.join(out)}
				</TABLE>
			>];''')			
				cfrom, clabel = self.get_name()
				fdot.append(f'start -> TableNode_{self.gid}[label="attr2" ];')
			
		
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
#apc.cntr=cntr=counter()
parsed = parse(test_string, Code)

print('Input:')
print(test_string)
print('Parsed output:')
print('==============')

for c in parsed:
	
	#print( str(type(c)))
	if isinstance(c,FunctionOrProcedure):
		print('NAME:',c.name)
		#e()
	elif isinstance(c,Declarations):
		
		print('DECLARATIONS:')
		assert len(c)==1, len()
		for d in c[0]:
		
			if str(type(d)).endswith(".VariableDeclaration'>"):
				print('\tDVAR:',d.name)
			else:
				pass
				#print(111, d, type(d))
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
				
				for le in b:
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
						pp(dir(le))
						pp(le.__dict__)
						#e()
						print(f"\t\tDROP TABLE: {le.table}")
					elif isinstance(le, ctt.CreateTableStatement):
						print(f"\t\tCREATE TEMP TABLE: {le.table}, LIKE: {le.like_clause.like_table}")
					elif isinstance(le, ias.InsertSelectStatement):
						print(f"\t\tINSERT AS SELECT: {le.table}, LIKE: {le.columns}")
					
					elif isinstance(le, update.UpdateStatement):
						print(f"\t\tUPDATE: {le}")
					else:
						print(le, type(le))
			elif isinstance(b, ex.ExceptionBlock):
				print('\tEXCEPTION:', b)
			else:
				print(b, type(b))
			
	
		#if isinstance(c.ex, ex.ExceptionBlock):
		#	print('EXCEPTION:', c.ex)
	else:
		print(c, str(type(c)))


#pp(out)
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


'''

footer=f'''

}}
'''

import re

# Input string
input_string = "Hello, World! It's a beautiful day :) #123"

# Regular expression pattern for non-alphanumeric characters
pattern = '[^\w\s]'  # \w matches any alphanumeric character and underscore. \s matches any whitespace character.

# Replace non-alphanumeric characters with an empty string
cleaned_string = re.sub(pattern, '', input_string)



class Parsed(Local):

	def _get_full_dot(self, parent, dfrom, hdot, fdot):
		pp(parent)
		
		#e()
		for cid,c in enumerate(parent):
			c.get_full_dot(parent,'start', cid, hdot, fdot, level=1)
		
	
		
hdot=[]
fdot=[]
apc.parsed=parsed
if 1:
	ped=Parsed()
	
	apc.parsed.get_full_dot(ped, 'start',  1, hdot, fdot, 0, label='')


pp(apc.cntr.cnt)


#e(0)
dot=f'''
{header}
end [label="End", shape=circle];
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