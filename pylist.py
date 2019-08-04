import sys
import pack

a = open("Module.txt", "w")
a.write("\n".join(sys.modules.keys()))
a.close()

a = open("Module.txt", "r")
b = a.readlines()
a.close()
string = ""
for x in b:
	try:
		x.__file__
	except:
		if pack.Exist(x.replace("\n",".py")): 
			string += x.replace("\n", ".py\n")

a = open("liste.txt", "w")
a.write(string)
a.close()