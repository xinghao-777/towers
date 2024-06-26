import pygame as pg
import control_system

if __name__ == "__main__":
    pg.init()
    con = control_system.Control()
    con.run()
# 受限与图片大小 和 不同模块间屏幕位置参数为直接赋值， 屏幕大小不得随便修改
# 塔在地图内手动点击可旋转攻击方向
# 怪物随机生成，并按照最初定义的最短路径前进
# 卡牌分为tower(塔)和element(元素)，菜单栏里可容纳5个tower和2个element
# 塔为基础设施，元素有两个使用方式，一是为塔附加属性，而是产生一次性效果
# 地图属性position以代表中心格（8，8），rc则是（0，0），xy为笛卡尔坐标
