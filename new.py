import ui, wndMgr, uiCommon, pack, os, time, dbg

class pack_darealfreak(object):

	def __init__(self, filename, mode = 'rb'):
		assert mode in ('r', 'rb')
		if not pack.Exist(filename):
			raise IOError, 'No file or directory'
		self.data = pack.Get(filename)
		if mode == 'r':
			self.data=_chr(10).join(self.data.split(_chr(13)+_chr(10)))

	def __iter__(self):
		return pack_file_iterator(self)

	def read(self, len = None):
		if not self.data:
			return ''
		if len:
			tmp = self.data[:len]
			self.data = self.data[len:]
			return tmp
		else:
			tmp = self.data
			self.data = ''
			return tmp

	def readline(self):
		return self.read(self.data.find(_chr(10))+1)

	def readlines(self):
		return [x for x in self]

class FileExtractor(ui.ScriptWindow):
	Gui = []
	Errortype = "none"
	
	def __init__(self):
		self.Gui = []
		ui.ScriptWindow.__init__(self)
		self.AddGui()

	def __del__(self):
		self.Gui[0].Hide()
		ui.ScriptWindow.__del__(self)
				
	def AddGui(self):
		Gui = [
			[[ui.ThinBoard, ""], [255, 40], [50, wndMgr.GetScreenHeight()-100], [], ["float"]],			
			[[ui.Button, 0], [0, 0], [230, 13], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ['SetToolTipText', ["Close", 0, - 23]], ['SetEvent', [lambda : self.__del__()]]], []],	
			[[ui.Button, 0], [0, 0], [120, 10], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Cikart"]], ['SetEvent', [lambda : self.ExtractFiles()]]], []],			
			[[ui.SlotBar, 0], [87, 18], [15, 10], [], []],			
			[[ui.EditLine, 3], [87, 17], [6, 2], [["SetMax", [15]], ["SetFocus", [""]]], []],			
			]
		GuiParser(Gui, self.Gui)

	def Extract(self, script):
		add = ""
		if str(script).find("d:/") != -1:
			script = str(script).replace("d:/", "")
			add = "d:/"

		if pack.Exist(add + script):
			if not os.path.exists("Source/" + script):
				os.makedirs("Source/" + script)

			if os.path.exists("Source/" + script):
				if os.path.isfile("Source/" + script):
					os.remove("Source/" + script)
				else:
					os.rmdir("Source/" + script)

			if self.IsBinary(script) == 0:
				lines = pack_darealfreak(add + script, "r").readlines()
				f = open("Source/" + script, "a+")

				for line in lines:
					tokens = line
					f.write(str(tokens))		
				f.close()
			else:
				Binary = pack_darealfreak(add + script, 'rb')
				Bytes = Binary.read()
				if len(Bytes) == 0:
					if self.Errortype != "ending":
						self.Errortype = "read"
						self.ErrorScreen(str(add + script)+" couldn't read.")
					return
				else:
					f = open("Source/" + script, "wb")		
					f.write(str(Bytes))		
					f.close()
		else:
			self.Errortype = "exist"
			self.ErrorScreen(str(add + script)+" doesn't exist.")
			return
			
		self.ErrorScreen("Extraction successfully completed.")

	def ExtractFiles(self):
		extensionList = [
			".mde",
			".efx",
			".dds",
			".gr2",
			".tga",
			".anim",
			".mdl",
			".fly",
			".jpg",
			".png",
			".slc",
			".spt",
			".txt",
			".json",
			".msa",
			".sub",
			".csv",
			".mse",
			".mdatr",
			".fnt",
			".bmp",
			".odsc",
			".msk",
			".msm",
			".msf",
			".prb",
			".prd",
			".pre",
			".prt",
			".pra",
			".dprt",
			".sprt",
			".bprt",
			".eprt",
			".wav",
			".mp3",
			".mss",
			".snd",
			".raw",
			".atr",
			".wtr"
		]

		handle = app.OpenTextFile("liste.txt")
		count = app.GetTextFileLineCount(handle)
		for ext in extensionList:
			os.system("start ExtPatch.exe %d %s" % (os.getpid(), ext))
			taskList = str(os.popen("tasklist").read())
			if "ExtPatch" in taskList:
				dbg.TraceError("ExtPatch running")
				time.sleep(1)

			for i in xrange(count):
				try:
					line = app.GetTextFileLine(handle, i)
				except IndexError:
					pass
				line = line.lower()
				if ext in line:
					self.Extract(line)

	def IsBinary(self, script):
		if str(script).count(".") == 0:
			self.Errortype = "ending"
			self.ErrorScreen(str(script)+" has no file extension.")
			script = script + ".binary"
		Split = script.split(".")
		end = str(Split[1])
		end = end.lower()
		
		if end == "": 
			return 0 
		else:
			return 1
			
	def ErrorScreen(self, error=""):
		ErrorDialog = uiCommon.PopupDialog()
		ErrorDialog.SetText(error)
		ErrorDialog.SetAcceptEvent(self.__OnCloseErrorDialog)
		ErrorDialog.Open()
		self.ErrorDialog = ErrorDialog
		
	def __OnCloseErrorDialog(self):
		self.pop = None

def GuiParser(guiobjects, list):
	#[Type, Parentindex],[Sizex, Sizey], [Posx, Posy], [commands], [flags]
	for object in guiobjects:
		Object = object[0][0]()
		if object[0][1] != "":
			Object.SetParent(list[object[0][1]])
		if object[1][0] + object[1][1] != 0:
			Object.SetSize(object[1][0], object[1][1])
		if object[2][0] + object[2][1] != 0:
			Object.SetPosition(object[2][0], object[2][1])
				
		for command in object[3]:
			cmd = command[0]	
			attr = getattr(Object,cmd)			
			if callable(attr):
				argument = command[1]
				lenght = len(argument)
				if lenght == 1:
					if argument[0] == "":
						attr()
					else:
						attr(argument[0])
				elif lenght == 2:
					attr(argument[0], argument[1])
				elif lenght == 3:
					attr(argument[0], argument[1], argument[2])
				elif lenght == 4:
					attr(argument[0], argument[1], argument[2], argument[3])
		for flag in object[4]:
			Object.AddFlag(str(flag))
		Object.Show()
	
		list.append(Object)
		
FileExtractor().Show()