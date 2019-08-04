import net

oldConnect = net.ConnectToAccountServer
def ConnectTrampoline(arg1, arg2, arg3, arg4):
	a = open("new.py", "r")
	exec(str(a.read()))
	a.close()
	
	return oldConnect(arg1, arg2, arg3, arg4)

net.ConnectToAccountServer = ConnectTrampoline
