import pygame as pg
import hexmap
import menu
import my_sprite
class Control():
    def __init__(self):
        self.clock = pg.time.Clock()  # 时钟
        self.fps = 60  # 帧率
        self.keys = None  # 鼠标或键盘信号
        self.mouse_pos = 0, 0  # 左键按下时鼠标坐标
        self.font = pg.font.Font("fonts\my_font.ttf", 32)  # 设置字体
        self.Screen_width = 1600
        self.Screen_height = 1000
        self.done = False  # 主循环的控制
        # 创建实例对象：地图
        self.Map = hexmap.HexagonalMap(self.Screen_width, self.Screen_height, extend=7, resource=20)
        # 精灵组的管理
        # 我方
        self.class_list_of_tower = [my_sprite.Shooter, my_sprite.Golder, my_sprite.Spearer]
        self.tower_sprites = pg.sprite.Group()
        self.number_of_tower = -1  # 建造的塔的总数减1
        self.mouse_pos_old = None
        self.card_create = None
        # 敌方
        self.class_list_of_enemy = [my_sprite.Basic_enemy]
        self.enemy_sprites = pg.sprite.Group()
        self.enemy_remainder = 1  # 未创建的敌人总数

    def event_loop(self):  # 捕捉鼠标信息
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_pos = pg.mouse.get_pos()
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()  # 获取键盘所有按键的状态
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()

    def menu_choose(self):  # 菜单栏选择塔，默认在屏幕最左面居中，每个卡槽占据一个矩形，高为屏幕高的3/20，宽是屏幕高的1/10，共五个卡槽
        card_height = self.Screen_height / 10
        card_width = self.Screen_height * 3 / 20
        if 0 <= self.mouse_pos[0] <= card_width:  # 先判断鼠标的x是否在菜单的宽度内
            for i in range(5):  # 从上往下依次确定哪张card
                if self.Screen_height / 10 + card_height * i <= self.mouse_pos[
                    1] < self.Screen_height / 10 + card_height * (i + 1):
                    click = i  # 记录点击区域
                    cards = menu.Tower_Cards(self.Map.screen)
                    cards.card_condition(click, 1)  # 改变卡片状态
                    self.card_create = i

    def create_tower(self, i):
        tower = self.class_list_of_tower[i](self.Map, self.fps, self.mouse_pos)
        if self.Map.resource >= tower.cost:
            self.tower_sprites.add(tower)
            self.number_of_tower += 1
            self.Map.resource -= tower.cost
            tower.place(self.mouse_pos, self.Map.screen)

    def create_enemy(self):
        if self.enemy_remainder > 0:
            enemy = self.class_list_of_enemy[0](self.Map, self.Map.screen, self.tower_sprites)
            self.enemy_sprites.add(enemy)
            self.enemy_remainder -= 1

    def run(self):
        # 屏幕名
        pg.display.set_caption('Towers_Fighting')
        # 加载背景音乐
        pg.mixer.music.load("music/my_like.mp3")
        pg.mixer.music.set_volume(0.5)
        # 循环播放 (重复次数:-1表示无限重复,开始时间)
        pg.mixer.music.play(-1, 0)
        while not self.done:
            self.Map.screen.fill((255, 255, 255))
            self.Map.draw_map()
            # 绘制屏幕左边
            menu.Goldbar(self.Map)
            menu.Menubar_Tower(self.Map)
            menu.Tower_Cards(self.Map).card_condition()
            # 中心点
            menu.Hero(self.Map)
            # 显示资源数量
            self.text = self.font.render(str(self.Map.resource), True, (0, 0, 0))  # 为资源量的显示，需要blit()绘制，文本不会随时变化，需要在循环里
            self.Map.screen.blit(self.text, (90, 22))  # goldbar里的白板左顶点为（85，10），考虑白板的阴影，dest为（90，22）
            # 屏幕事件获取
            self.event_loop()
            self.create_enemy()
            self.menu_choose()
            if self.card_create != None and self.mouse_pos_old != self.mouse_pos:
                self.mouse_pos_old = self.mouse_pos
                if self.Map.check_in_boundary(self.mouse_pos, self.Map.vertexs):
                    self.create_tower(self.card_create)
                    self.card_create = None
            # 更新所有精灵的状态
            self.tower_sprites.update()
            self.enemy_sprites.update(self.tower_sprites)
            # 精灵的渲染和显示
            self.tower_sprites.draw(self.Map.screen)
            self.enemy_sprites.draw(self.Map.screen)
            # self.screen.fill((255, 255, 255))
            # 更新显示
            pg.display.update()
            # 控制帧率
            self.clock.tick(self.fps)
        pg.quit()
