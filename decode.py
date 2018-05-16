import zlib
from doc import Doc
fp=open('Melvin-Lim.pdf')
doc=Doc(fp)
doc.display()
raw_input()
fp=open('N5.pdf')
doc=Doc(fp)
doc.display()
