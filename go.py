class Application(Tk):
	# 初始化棋盘,默认九路棋盘
	def __init__(self,my_mode_num=9):
		Tk.__init__(self)
		# 模式，九路棋：9，十三路棋：13，十九路棋：19
		self.mode_num=my_mode_num
		# 窗口尺寸设置，默认：1.8
		self.size=1.8
		# 棋盘每格的边长
		self.dd=360*self.size/(self.mode_num-1)
		# 相对九路棋盘的矫正比例
		self.p=1 if self.mode_num==9 else (2/3 if self.mode_num==13 else 4/9)
		# 定义棋盘阵列,超过边界：-1，无子：0，黑棋：1，白棋：2
		self.positions=[[0 for i in range(self.mode_num+2)] for i in range(self.mode_num+2)]
		# 初始化棋盘，所有超过边界的值置-1
		for m in range(self.mode_num+2):
			for n in range(self.mode_num+2):
				if (m*n==0 or m==self.mode_num+1 or n==self.mode_num+1):
					self.positions[m][n]=-1
		# 拷贝三份棋盘“快照”，悔棋和判断“打劫”时需要作参考
		self.last_3_positions=copy.deepcopy(self.positions)
		self.last_2_positions=copy.deepcopy(self.positions)
		self.last_1_positions=copy.deepcopy(self.positions)
		# 记录鼠标经过的地方，用于显示shadow时
		self.cross_last=None
		# 当前轮到的玩家，黑：0，白：1，执黑先行
		self.present=0 
		# 初始停止运行，点击“开始游戏”运行游戏
		self.stop=True
		# 悔棋次数，次数大于0才可悔棋，初始置0（初始不能悔棋），悔棋后置0，下棋或弃手时恢复为1，以禁止连续悔棋
		self.regretchance=0
		# 图片资源，存放在当前目录下的/Pictures/中
		self.photoW=PhotoImage(file = "./Pictures/W.png")
		self.photoB=PhotoImage(file = "./Pictures/B.png")
		self.photoBD=PhotoImage(file = "./Pictures/"+"BD"+"-"+str(self.mode_num)+".png")
		self.photoWD=PhotoImage(file = "./Pictures/"+"WD"+"-"+str(self.mode_num)+".png")
		self.photoBU=PhotoImage(file = "./Pictures/"+"BU"+"-"+str(self.mode_num)+".png")
		self.photoWU=PhotoImage(file = "./Pictures/"+"WU"+"-"+str(self.mode_num)+".png")
		# 用于黑白棋子图片切换的列表
		self.photoWBU_list=[self.photoBU,self.photoWU]
		self.photoWBD_list=[self.photoBD,self.photoWD]
		# 窗口大小
		self.geometry(str(int(600*self.size))+'x'+str(int(400*self.size)))
		# 画布控件，作为容器
		self.canvas_bottom=Canvas(self,bg='#369',bd=0,width=600*self.size,height=400*self.size)
		self.canvas_bottom.place(x=0,y=0)
		# 几个功能按钮
		self.startButton=Button(self,text='开始游戏',command=self.start)
		self.startButton.place(x=480*self.size,y=200*self.size)
		self.passmeButton=Button(self,text='弃一手',command=self.passme)
		self.passmeButton.place(x=480*self.size,y=225*self.size)	
		self.regretButton=Button(self,text='悔棋',command=self.regret)
		self.regretButton.place(x=480*self.size,y=250*self.size)
		# 初始悔棋按钮禁用
		self.regretButton['state']=DISABLED
		self.replayButton=Button(self,text='重新开始',command=self.reload)
		self.replayButton.place(x=480*self.size,y=275*self.size)
		self.newGameButton1=Button(self,text=('十三' if self.mode_num==9 else '九')+'路棋',command=self.newGame1)
		self.newGameButton1.place(x=480*self.size,y=300*self.size)
		self.newGameButton2=Button(self,text=('十三' if self.mode_num==19 else '十九')+'路棋',command=self.newGame2)
		self.newGameButton2.place(x=480*self.size,y=325*self.size)
		self.quitButton=Button(self,text='退出游戏',command=self.quit)
		self.quitButton.place(x=480*self.size,y=350*self.size)
		# 画棋盘，填充颜色
		self.canvas_bottom.create_rectangle(0*self.size,0*self.size,400*self.size,400*self.size,fill='#c51')
		# 刻画棋盘线及九个点
		# 先画外框粗线
		self.canvas_bottom.create_rectangle(20*self.size,20*self.size,380*self.size,380*self.size,width=3)
		# 棋盘上的九个定位点，以中点为模型，移动位置，以作出其余八个点
		for m in [-1,0,1]:
			for n in [-1,0,1]:
				self.oringinal=self.canvas_bottom.create_oval(200*self.size-self.size*2,200*self.size-self.size*2,
				200*self.size+self.size*2,200*self.size+self.size*2,fill='#000')
				self.canvas_bottom.move(self.oringinal,m*self.dd*(2 if self.mode_num==9 else (3 if self.mode_num==13 else 6)),
				n*self.dd*(2 if self.mode_num==9 else (3 if self.mode_num==13 else 6)))
		# 画中间的线条
		for i in range(1,self.mode_num-1):
			self.canvas_bottom.create_line(20*self.size,20*self.size+i*self.dd,380*self.size,20*self.size+i*self.dd,width=2)
			self.canvas_bottom.create_line(20*self.size+i*self.dd,20*self.size,20*self.size+i*self.dd,380*self.size,width=2)
		# 放置右侧初始图片
		self.pW=self.canvas_bottom.create_image(500*self.size+11, 65*self.size,image=self.photoW)
		self.pB=self.canvas_bottom.create_image(500*self.size-11, 65*self.size,image=self.photoB)
		# 每张图片都添加image标签，方便reload函数删除图片
		self.canvas_bottom.addtag_withtag('image',self.pW)
		self.canvas_bottom.addtag_withtag('image',self.pB)
		# 鼠标移动时，调用shadow函数，显示随鼠标移动的棋子
		self.canvas_bottom.bind('<Motion>',self.shadow)
		# 鼠标左键单击时，调用getdown函数，放下棋子
		self.canvas_bottom.bind('<Button-1>',self.getDown)
		# 设置退出快捷键<Ctrl>+<D>，快速退出游戏
		self.bind('<Control-KeyPress-d>',self.keyboardQuit)
