import math
import pygame as pg
import random
import time

# 塔精灵
class Tower(pg.sprite.Sprite):  # 继承父类
    def __init__(self, Map, fps, pos):  # 有bug，pos在place时使用
        super().__init__()
        self.Map = Map  # 接受地图实例
        self.fps = fps  # 帧率
        self.qr = self.Map.mouse_xy_to_Axial(pos)
        self.levelpoint = 1  # 等级点数
        self.levels = 1  # 初始等级
        self.cost = None  # 留给下级继承
        self.health = None  # 留给下级继承
        self.damage = None  # 留给下级继承(当前血量)
        self.max_health = None  # 留给下级继承(初始血量)
        self.name = None  # 留给下级继承（名字)
        self.image = None  # 留给下级继承
        self.rect = None  # 留给下级继承
        self.dt=0  #距离上一次攻击的帧数差

    def place(self):  # 放置塔数据在地图格上（pos为鼠标的位置（元组））
        if not self.Map.mapdata[self.qr].data["tower"]: # 当前格没有卡牌, 调用hexagons属性的下标行列要根据实际行列减一
            self.Map.mapdata[self.qr].data["tower"] = self.name  # 更改hex_map的属性，表示该格有牌

    def destroy(self):  # 摧毁，需要改逻辑，self.health被enemy调用而减少，还有铲子的操作
        if self.rect and self.qr is not None:  # 确保 self.rect 和 self.position 都被设置了
            if self.health <= 0:
                self.Map.mapdata[self.qr].data["tower"] = None
                self.kill()

    def up_level(self):  # 与击杀关联
        if self.levels < 3:
            if self.levelpoint >= 5:  # 每五点经验升一级
                self.max_health += 5
                self.health = self.max_health  # 回复满血
                if self.damage:
                    self.damage += 2
                self.levelpoint = 0
                self.levels += 1

class Shooter(Tower): # 射击者
    def __init__(self, Map, fps=60, pos=(0, 0)):
        super().__init__(Map, fps, pos)  # 传递必要的参数给父类
        # Shooter 特有的属性初始化
        self.name = 'shooter'
        self.cost = 10
        self.health = 10
        self.max_health = self.health  # 用于回复血量
        self.damage = 2  # 伤害
        self.shoot_rate = 1  # 攻速
        self.shoot_direction = 1  # 攻击方向，默认朝右
        self.shoot_distance = 4  # 攻击距离,格为单位
        # 精灵属性
        self.image_path = "images/Card_tower/shooter/shooter.png"
        self.image = pg.image.load(self.image_path).convert_alpha()
        x, y = self.Map.mapdata[self.qr].data['center']
        self.rect = self.image.get_rect(center=(x, y))
        # 子弹的精灵组
        self.bullet_group = pg.sprite.Group()
    def set_shoot_distance(self, distance):
        if distance is not None:
            self.shoot_distance = distance
    def set_shoot_rate(self, rate):
        if rate is not None:
            self.shoot_rate = rate
    def set_shoot_direction(self, direction):
        if direction is not None:
            self.shoot_distance = direction
    def rotate(self):  # 旋转，默认顺时针60°
        self.shoot_direction += 1
        # 设置旋转角度
        angle = 60
        # 旋转图像
        rotated_image = pg.transform.rotate(self.image, angle)
        # 获取旋转后图像的矩形边界
        rotated_rect = rotated_image.get_rect()
        # 计算旋转后图像的新位置
        self.dx = self.rect.centerx - rotated_rect.centerx
        self.dy = self.rect.centery - rotated_rect.centery
        rotated_rect.x += self.dx
        rotated_rect.y += self.dy
        self.image = rotated_image
        self.rect = rotated_rect
    def shoot(self):
        if self.damage > 0:  # 能攻击
            q, r = self.qr
            x, y = self.rect.center  # 储存当前xy坐标
            offset = f'd{self.shoot_direction}'
            for i in range(self.shoot_distance + 1):  # 包括本格
                if self.Map.is_within_bounds(q, r) and self.Map.mapdata[(q, r)].data['enemy'] and self.dt >= self.shoot_rate:  # 遍历的格是否在地图内 and 敌人是否在攻击范围里 and 满足攻击间隔
                    bullet = Shooter_bullet((x, y), self.Map, self.shoot_direction, self.damage)  # 创建子弹实例,bullet只是临时变量名，若要访问它，在group里遍历得到指定bullet
                    self.bullet_group.add(bullet)
                    self.dt=0
                    break
                q += self.Map.Offseting[offset][0]
                r += self.Map.Offseting[offset][1]

    def update(self):
        self.bullet_group.update()
        self.shoot()
        self.bullet_group.draw(self.Map.screen)
        self.dt+=1/60
class Golder(Tower): # 淘金者
    def __init__(self, Map, fps=60, pos=(0, 0)):
        super().__init__(Map, fps, pos)  # 传递必要的参数给父类
        self.name = 'golder'
        self.cost = 10
        self.health = 10
        self.produce_rate = 10  # 每隔多少秒产生$
        self.max_health = self.health
        # 精灵属性
        self.image_path = "images/Card_tower/golder/golder.png"
        self.image = pg.image.load(self.image_path)
        x, y = self.Map.mapdata[self.qr].data['center']
        self.rect = self.image.get_rect(center=(x, y))
        self.dt = 0
    def produce(self):
        if self.dt >= self.produce_rate:
            self.dt=0
            self.Map.resource += 5  # 每次加5$
    def update(self):
        self.dt+=1/60
        self.produce()
class Spearer(Tower): # 舞枪者
    def __init__(self, Map, fps=60, pos=(0, 0)):
        super().__init__(Map, fps, pos)  # 传递必要的参数给父类
        self.cost = 20
        self.health = 30
        self.damage = 2  # 伤害
        self.shoot_rate = 1  # 攻速
        self.shoot_direction = 1  # 攻击方向，默认朝右
        self.shoot_distance = 2  # 攻击距离,格为单位
        self.max_health = self.health
        self.name = 'spearer'
        # 精灵属性
        self.image_path = "images/Card_tower/spears/spears.png"
        self.image = pg.image.load(self.image_path)
        x, y = self.Map.mapdata[self.qr].data['center']
        self.rect = self.image.get_rect(center=(x, y))
    def slash(self): # 斩击
        pass
class Shooter_bullet(pg.sprite.Sprite):
    def __init__(self, xy, Map, direction, damage=None):
        super().__init__()
        self.Map = Map
        self.direction = direction  # 攻击方向，用角度表示，当竖直向上为0，顺时针增大
        self.damage = damage  # 威力
        # shooter的子弹精灵属性
        self.image_path = "images/Card_tower/shooter/shoot_arrow.png"
        self.image = pg.image.load(self.image_path)
        self.rect = self.image.get_rect(center = (xy[0], xy[1]))  # 图片以中心点为图片放置参考点
        self.speed = 2 * self.Map.HEX_SIZE * math.sqrt(3)  # 每秒移动2个格的距离
    def update(self):
        self.dx = math.sin(self.direction) * self.speed / 60
        self.dy = -math.cos(self.direction) * self.speed / 60
        self.rect.move_ip(self.dx,self.dy)
        # 检查子弹是否移出屏幕，如果是，移除
        if not self.Map.screen.get_rect().colliderect(self.rect):
            self.kill()
# 敌方
class Basic_enemy(pg.sprite.Sprite):
    def __init__(self, Map, screen, tower_sprites, image_path="images/enemy/basic_enemy.png"):
        super().__init__()
        self.Map = Map  # 获取地图实例
        self.screen = screen # 获取屏幕
        self.health = 20  # 血量
        self.attack = 5  # 攻击
        self.last_attach_time = 0
        self.attack_rate = 1 # 每秒一次
        self.speed = self.Map.HEX_SIZE * math.sqrt(3)  # 速度,每秒多少格
        self.image = pg.image.load(image_path) if image_path else None
        self.rect = self.image.get_rect() if self.image else None
        self.create()  # 调用本体方法，生成初始位置
        print(math.cos(5/3*math.pi),math.sin(5/3*math.pi))

    def create(self):
        extend = self.Map.rows // 2
        # 只在外圈生成敌人
        r_list = [_ for _ in range(-extend, extend + 1)]
        # 构建权重列表
        weights = [self.Map.per_cols[0]]
        for i in range(self.Map.rows - 2):
            weights.append(2)
        weights.append(self.Map.per_cols[0])
        r = random.choices(r_list, weights)  # 随机行（1到最大行），返回单列表
        r = r[0]  # 取int
        if r != -extend or r != extend:  # 非首尾行只取改行的首尾列
            if r <= 0:
                q = random.choice([-(extend + r), extend])
            else:
                q = random.choice([-extend, (extend - r)])
        else:
            if r == -extend:
                q = random.randint(-(extend + r), extend)
            else:
                q = random.randint(-extend, (extend - r))
        self.Map.mapdata[(q, r)].data['enemy'] += 1
        self.qr = q, r
        self.move_path = self.Map.find_path(self.qr,(0,0))
        self.rect.center =self.Map.mapdata[(q, r)].data['center']
        print(self.move_path)
    def move(self):
        self.move_direction = (self.move_path[1][0] - self.move_path[0][0], self.move_path[1][1] - self.move_path[0][1])
        print(self.move_direction, end='   ')
        for i in range(1, 7):
            key_offset = f'd{i}'
            if self.move_direction == (self.Map.Offseting[key_offset][0], self.Map.Offseting[key_offset][1]):
                self.move_direction = self.Map.Offseting[key_offset][2]
        print(math.degrees(self.move_direction), end='   ')
        print(self.qr)
        dx = self.speed / 60 * math.cos(self.move_direction)
        dy = self.speed / 60 * math.sin(self.move_direction)
        self.rect.x += dx
        self.rect.y += dy
        if self.Map.mouse_xy_to_Axial(self.rect.center) == self.move_path[1]:
            self.Map.mapdata[self.qr].data["enemy"] -= 1  # 先删除之前格的标记
            self.qr = self.Map.mouse_xy_to_Axial(self.rect.center)  # 更新q,r
            self.Map.mapdata[self.qr].data["enemy"] += 1  # 后增加当前格的标记
            self.move_path.pop(0)  # 删除首路径
    def attach(self):
        attached_tower = pg.sprite.spritecollide(self, self.tower_sprites, False)
        if attached_tower:
            for tower in attached_tower:
                if time.time() - self.last_attach_time >= 1:
                    tower.health -= self.attack
                    self.last_attach_time = time.time()
                    return True  # 只攻击第一个塔并返回
        return False  # 没有碰撞到塔
    def die(self):
        if self.health <= 0:
            self.kill()
            self.Map.mapdata[self.qr].data['enemy'] -= 1
    def update(self, towers):
        self.tower_sprites = towers
        if self.attach(): # 执行攻击后不移动
            pass
        else:
            if len(self.move_path) != 1:
                self.move()



