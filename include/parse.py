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