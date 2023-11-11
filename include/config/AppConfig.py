import os, re, sys, copy, string, logging 
from os.path import isfile, isdir, join, basename, dirname
import json
from datetime import datetime 
from copy import deepcopy
from pprint import pprint as pp
from include.config.Config import Config
import shutil
import logging

log=logging.getLogger()

e=sys.exit
from collections import defaultdict


class Counter(object):
	def __init__(self):
		self.cnt=defaultdict(lambda: 1)
	def inc(self, obj):
		tname=obj.__class__.__name__
		self.cnt[tname] +=1
	def get(self, obj):
		tname=obj.__class__.__name__
		return self.cnt[tname]
		

class AppConfig(Config): 
	def __init__(self, **kwargs):
		Config.__init__(self,**kwargs)
		self.gid=0
		self.cntr = Counter()
		if 0:
			self.kwargs=kwargs
			self.ui_layout=kwargs['ui_layout']
			self.params=params=kwargs['params']
	def get_gid(self):
		self.gid += 1
		return self.gid
	def load_ui_cfg(self, quiet=False):


		self.ucfg = self.LoadConfig(config_path=self.apc_path, quiet=quiet)
		assert self.ucfg is not None, self.ucfg
		return self
 
	def load_pipeline_module(self, mod_name, step=''):
		
		
		assert isdir(PIPELINE_DIR), PIPELINE_DIR
		dn = dirname(mod_name)
		fn = basename(mod_name)
		#if not  uic.ui_layout:
		#    uic.ui_layout ='default'
		mod_loc= join(step,PIPELINE_DIR,self.pipeline,self.ui_layout, dn, f'{fn}.py').replace('/','\\')
		print(mod_loc)
		assert isfile(mod_loc), mod_loc
		return getattr(import_module(mod_loc),  fn)
		
	def getErrDlgSize(self):
		cfg=self.cfg
		assert 'ErrDlg' in cfg
		assert 'size' in cfg['ErrDlg']
		return cfg['ErrDlg']['size']
	def getErrDlgSPos(self):
		cfg=self.cfg
		assert 'ErrDlg' in cfg
		assert 'pos' in cfg['ErrDlg']
		return cfg['ErrDlg']['pos']
	def setErrDlgSize(self, size):
		cfg=self.cfg
		assert 'ErrDlg' in cfg
		assert 'size' in cfg['ErrDlg']
		cfg['ErrDlg']['size'] = tuple(size)
		self.saveConfig()
	def setErrDlgPos(self, pos):
		cfg=self.cfg
		assert 'ErrDlg' in cfg
		assert 'pos' in cfg['ErrDlg']
		cfg['ErrDlg']['pos']= tuple(pos)
		self.saveConfig()		
		
		
		
		
		
	def getConn(self):
		env=self.env
		cfg=self.cfg
		assert env in cfg.env
		ckey = cfg.env[env][self.conn_name]
		conn = cfg.stores[ckey]
		assert 'conn_string' in conn
		assert conn.conn_string
		assert 'env_refs' in conn
		assert conn.env_refs
		for k in list(conn.env_refs.keys()):
			v=conn.env_refs[k]
			if type(v) == list: # it's env var
				var=v[0]
				conn.env_refs[k] = os.environ[var]
		
		conn.conn_string=conn.conn_string.format(**conn.env_refs)

		return conn
	def setConnName(self, cname):  
		self.conn_name=cname		