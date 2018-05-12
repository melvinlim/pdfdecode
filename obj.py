class Obj():
	def __init__(self,objN,genN,raw):
		self.objN=objN
		self.genN=genN
		data=raw.strip('<<')
		data=data.strip('\n')
		data=data.split('>>')
		params=data[0].split('\n')
		params=filter(None,params)
		self.params=dict()
		for words in params:
			tmp=words.split(' ')
			tmp=filter(None,tmp)
			self.params[tmp[0]]=tmp[1:]
		self.data=[]
		if len(data)==2 and data[1]!='' and data[1]!='\n':
			tmp=data[1]
			if tmp.find('endstream')>=0:
				tmp=tmp.strip('\n')
				tmp=tmp.strip('endstream')
				tmp=tmp.strip('stream')
				tmp=tmp.strip('\n')
			if '/Filter' in self.params and '/FlateDecode' in self.params['/Filter']:
				import zlib
				try:
					self.data=zlib.decompress(tmp)
				except:
					print 'zlib failed header check'
					self.data=tmp
			else:
				self.data=tmp
		else:
			self.data=raw
