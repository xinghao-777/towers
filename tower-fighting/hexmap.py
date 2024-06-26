import math
import heapq
import pygame as pg
from collections import namedtuple

# 地图格(Hex为一个六边形结构体),r为上下的对角线,箭头向下,代表cube里的z, q则代表cube的x, (y用-(r+q)表示)
Hex = namedtuple('Hex', ['z', 'x', 'y', 'data'])  # 使用Axial coordinates（纵向坐标）
class HexagonalMap: # 地图
    def __init__(self, Screen_width, Screen_height, extend=7, resource=20):
        # 六个偏移方向
        self.Offseting = {
                        'd1': (1, 0, 0),  # 右
                        'd2': (0, 1, math.pi / 3),  # 右下
                        'd3': (-1, 1, math.pi / 3 * 2),  # 左下
                        'd4': (-1, 0, math.pi),  # 左
                        'd5': (0, -1, -math.pi / 3 * 2),  # 左上
                        'd6': (1, -1, -math.pi / 3),  # 右上
                        }
        self.Screen_width = Screen_width
        self.Screen_height = Screen_height
        self.resource = resource  # 初始资源
        self.HEX_SIZE = 36  # 六边形边长
        self.rows = 2 * extend + 1 # 地图行数
        self.per_cols = [i for i in range(1 + extend, self.rows + 1)] + [i for i in range(self.rows - 1, extend, -1)]  # 每行的六边形数量
        self.create_hex_grid(extend) # 创建地图网格
        self.create_vertexs()  # 更新self.vertexs
        # 窗口属性
        self.screen = pg.display.set_mode((self.Screen_width, self.Screen_height))
        # 填充背景
        self.screen.fill((255, 255, 255))
        # 绘制地图边界
        self.draw_map()
    def create_hex_grid(self, extend):
        self.mapdata = {}  # 用来存储所有的Hex,使用轴向坐标系统
        # 根据偏移坐标计算笛卡尔坐标xy
        def __calculate_hex_xy__(row, col):
            x_center = self.Screen_width // 2  # 屏幕宽度的中心
            tar_x = (self.per_cols[row] + 1) / 2  # 计算当前行的对称轴
            x_offset = (col + 1 - tar_x) * self.HEX_SIZE * math.sqrt(3)  # 计算当前六边形中心相对于其所在行对称轴的偏移量
            x = x_center + x_offset  # 计算当前六边形中心的x坐标
            y = self.Screen_height // 2 + (row - (self.rows - 1) // 2) * self.HEX_SIZE * 1.5  # 计算当前六边形中心的y坐标（基于行数）
            return x, y
        for row, d in enumerate(range(-extend, extend + 1)):  # d: 该行距离中间行的值，row：第几行
            l = self.per_cols[row]
            for col in range(l):
                r = d
                if r <= 0:
                    q = col - row
                else:
                    q = col - extend
                # 计算当前六边形的屏幕坐标
                xy = __calculate_hex_xy__(row, col)
                # 创建一个Hex实例并添加到网格中
                self.mapdata[(q, r)] = Hex(r, q, -(r + q), {'center': xy, 'tower': None, 'enemy': 0})

    # 笛卡尔坐标-->轴向坐标
    def Cartesian_to_Axial(self, x, y):
        # -4.440892098500626e-16:一个非常接近于0的负数
        r = (y - self.Screen_height // 2) / 3 * 2 / self.HEX_SIZE
        q = ((x - self.Screen_width // 2) / (self.HEX_SIZE * math.sqrt(3) / 2) - r) / 2
        return round(q), round(r)

    # 轴向坐标-->笛卡尔坐标
    def Axial_to_Cartesian(self, q, r):
        s = -(q + r)
        x = self.Screen_width // 2 + (q - s) * self.HEX_SIZE * math.sqrt(3) / 2
        y = self.Screen_height // 2 + (r - (s + q) / 2) * self.HEX_SIZE
        return x, y

    # 轴向（立体）坐标-->偏移坐标
    def Axial_to_Offset(self, q, r):  # 即z, x
        col = q + (r - (r % 2)) // 2
        row = r
        return col, row # 参照：中心（0，0）

    # 偏移坐标-->纵向（立体）坐标
    def Offset_to_Axial(self, r, c):
        q = c - (r - (r % 2)) // 2
        r = c
        return q, r

    # 创建地图的近六边形形状的六个顶点，用于判断地图的边界
    def create_vertexs(self):
        need_side = (self.rows + 1 / 3) * self.HEX_SIZE * math.sqrt(3) / 2
        vertex_list = []
        for i in range(6):
            angle = math.pi * (1 / 6 + i / 3)
            x = self.Screen_width // 2 + math.sin(angle) * need_side
            y = self.Screen_height // 2 - math.cos(angle) * need_side
            vertex_list.append((x, y))
        self.vertexs = vertex_list

    # 检测鼠标点（x,y）是否在地图外
    def check_in_boundary(self, mouse_pos, vertexs):
        px = mouse_pos[0]
        py = mouse_pos[1]
        is_in = False
        for i, corner in enumerate(vertexs):  # 默认鼠标点击点向右发射射线，看与地图的六条边的交点数
            next_i = (i + 1) if i + 1 < len(vertexs) else 0
            x1, y1 = corner
            x2, y2 = vertexs[next_i]
            if (x1 == px and y1 == py) or (x2 == px and y2 == py):
                is_in = True
                break
            if py == y1 and py == y2:
                if min(x1, x2) < px < max(x1, x2):
                    is_in = True
                    break
            if min(y1, y2) < py <= max(y1, y2):
                x = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
                if x == px:
                    is_in = True
                    break
                elif x > px:
                    is_in = not is_in
        return is_in

    # 检测q,r是否在地图内
    def is_within_bounds(self, q, r):
        # 检查r是否在允许的范围内
        if not (-self.rows // 2 <= r <= self.rows // 2):
            return False
        # 检查q是否在给定的r对应的列数范围内
        row_index = r + self.rows // 2
        if not (0 <= q < self.per_cols[row_index]):
            return False
        return True

    # 获取相邻的六个节点，从d1开始
    def get_neighbors(self, q, r):
        neighbors = []
        for dq, dr, radian in self.Offseting.values():
            new_q, new_r = q + dq, r + dr
            if (new_q, new_r) in self.mapdata:
                neighbors.append((new_q, new_r))
        return neighbors

    # 寻路(dijkstra),node对应(q,r)
    def find_path(self, start, goal):
        distances = {}  # 存储从源点到每个节点的最短距离
        previous = {}  # 存储每个节点的最短路径上的前一个节点
        # 初始化距离和前一个节点
        for node in self.mapdata:
            distances[node] = float('inf')
            previous[node] = None
        distances[start] = 0
        pq = [(0, start)]  # 使用优先队列来存储待处理的节点
        while pq:
            # 弹出距离最短的节点
            current_distance, current_node = heapq.heappop(pq)
            # 如果当前节点计算的距离大于目前的最优距离，则跳过
            if current_distance > distances[current_node]:
                continue
            # 如果找到了目标节点，则停止搜索
            if current_node == goal:
                break
            # 遍历当前节点的所有邻居
            for neighbor in self.get_neighbors(current_node[0], current_node[1]):
                # 计算从源点到邻居节点的距离
                distance = current_distance + 1  # 移动到邻居的代价为1
                # 如果通过当前节点可以得到更短的距离，则更新距离和前一个节点
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        # 如果没有找到路径到目标节点，则返回None
        if distances[goal] == float('inf'):
            return None
        # 重构路径
        path = []
        while goal is not None:
            path.append(goal)
            goal = previous[goal]
        path.reverse()
        return path

    # 鼠标转轴向坐标
    def mouse_xy_to_Axial(self, xy):
        x, y = xy
        # 将屏幕坐标(x,y)转换为纵向坐标（r,q）并四舍五入到最接近的六边形坐标
        q, r = self.Cartesian_to_Axial(x, y)
        # 根据弧度偏移q，r
        def offset_qr(q, r, x, y):
            radian = math.atan2(y - self.mapdata[(q, r)].data['center'][1],
                                x - self.mapdata[(q, r)].data['center'][0])
            if radian < 0: radian += math.pi * 2
            if radian >= 11 / 6 * math.pi or radian < math.pi / 6:
                sector = 1
                new_q = q + self.Offseting[f'd{sector}'][0]
                new_r = r + self.Offseting[f'd{sector}'][1]
            else:
                sector = int((radian - math.pi / 6) // (math.pi / 3)) + 2
                new_q = q + self.Offseting[f'd{sector}'][0]
                new_r = r + self.Offseting[f'd{sector}'][1]
            if self.is_within_bounds(new_q, new_r):
                return new_q, new_r
            return q, r
        # 检测x，y是否在q，r对应的六边形内
        def check_point(q, r, x, y):
            vertexs = []
            for i in range(6):
                angle = math.pi * i / 3
                cx = self.mapdata[(q, r)].data['center'][0] + math.sin(angle) * self.HEX_SIZE
                cy = self.mapdata[(q, r)].data['center'][1] - math.cos(angle) * self.HEX_SIZE
                vertexs.append((cx, cy))
            if self.check_in_boundary((x, y), vertexs):
                return q, r
            else:
                return None
        # 先检查是否在地图内，后检查鼠标x，y是否在对应的格内
        if self.is_within_bounds(q, r) and check_point(q, r, x, y):
            return check_point(q, r, x, y)
        else:
            q, r = offset_qr(q, r, x, y)
            if self.is_within_bounds(q, r) and check_point(q, r, x, y):
                return check_point(q, r, x, y)
        return None

    # 绘制地图
    def draw_map(self):
        # 绘制六边形函数
        def draw_hexagon(surface, xy):
            for i in range(6):
                first = (
                    xy[0] + math.sin(math.pi * i / 3) * self.HEX_SIZE,
                    xy[1] + self.HEX_SIZE * math.cos(math.pi * i / 3))
                end = (xy[0] + math.sin(math.pi * (i + 1) / 3) * self.HEX_SIZE,
                       xy[1] + self.HEX_SIZE * math.cos(math.pi * (i + 1) / 3))
                pg.draw.line(surface, (128, 128, 128), first, end, 1)
        for row in range(self.rows):
            for col in range(self.per_cols[row]):
                r = row - self.rows // 2
                if r <= 0:
                    q = col - row
                else:
                    q = col - self.rows // 2
                coord = self.mapdata[(q, r)].data['center']
                if coord:
                    draw_hexagon(self.screen, coord)  # 绘制一个地图格

