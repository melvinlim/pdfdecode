class Obj():
	def __init__(self,objN,genN,raw):
		self.objN=objN
		self.genN=genN
		data=raw.strip('<<')
		data=data.split('>>')
		params=data[0].split('\n')
		params=filter(None,params)
		self.params=dict()
		for words in params:
			tmp=words.split(' ')
			tmp=filter(None,tmp)
			self.params[tmp[0]]=tmp[1:]
		self.data=[]
		if len(data)>1:
			for words in data[1:]:
				tmp=words.strip('\n')
				if tmp!='':
					self.data.append(tmp)
