import sys, pygame
import numpy as np
import math
import random
import datetime
import time

sz = (800, 600)

def dist(p1, p2): #расчет расстояния
    return np.linalg.norm(np.subtract(p1, p2))

def ang(p1,p2):
    return math.atan2(*np.subtract(p1,p2)[::-1])

def angDiff(theta1, theta2):
    # Calculate the raw difference
    delta_theta = theta2 - theta1
    
    # Normalize the angle to the range (-pi, pi]
    delta_theta = (delta_theta + math.pi) % (2 * math.pi) - math.pi
    
    return delta_theta
def rot(v, ang): #функция для поворота на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def rotArr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]


pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    surf=font.render(s, True, (0,0,0))
    screen.blit(surf, (x,y))
def drawRotRect(screen, color, pc, w, h, ang): #точка центра, ширина высота прямоуг и
    pts = [
    [- w/2, - h/2],
    [+ w/2, - h/2],
    [+ w/2, + h/2],
    [- w/2, + h/2],
    ]
    pts = rotArr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

class Bullet:
    def __init__(self, x, y, ang):
        self.x = x
        self.y = y
        self.ang = ang
        self.vx = 200
        self.L = 10
        self.exploded = False
    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p0 = self.getPos()
        p1 = [-self.L/2, 0]
        p1=rot(p1, self.ang)
        p2 = [+self.L/2, 0]
        p2=rot(p2, self.ang)
        pygame.draw.line(screen, (0, 0, 0), np.add(p0, p1), np.add(p0, p2), 3)
    def sim(self, dt):
        vec=[self.vx, 0]
        vec=rot(vec, self.ang)
        self.x+=vec[0]*dt
        self.y+=vec[1]*dt

class Tank:
    def __init__(self, id, x, y, ang, cmd):
        self.id=id
        self.x=x
        self.y=y
        self.ang=ang
        self.cmd = cmd
        self.cd = 0.5
        self.angGun=0
        self.L=70
        self.W=45
        self.vlin = 20
        self.alin = 1
        self.gunlin = 2
        self.vx=0
        self.vy=0
        self.va=0
        self.vaGun=0
        self.health=100
        self.color = (255,0,0) if self.cmd==0 else (0,0,255)
        self.ugol_obezda = np.pi/1.7#((random.random())*np.pi/4+np.pi/4 )*(random.randint(0,1)-0.5)/0.5
        self.use_strat = False
    def fire(self,dt):
        if self.cd>0:
            self.cd-=dt
            return None
        r = self.W / 2.3
        LGun = self.L / 2
        p2 = rot([r + LGun, 0], self.ang + self.angGun)
        p2=np.add(self.getPos(), p2)
        b=Bullet(*p2, self.ang + self.angGun)
        self.cd=2
        return b
    def getPos(self):
        return [self.x, self.y]
    def draw(self, screen):
        pts=[[self.L/2, self.W/2], [self.L/2, -self.W/2], [-self.L/2, -self.W/2], [-self.L/2, self.W/2]]
        pts=rotArr(pts, self.ang)
        pts=np.add(pts, self.getPos())
        pygame.draw.polygon(screen, self.color, pts, 2)
        r=self.W/2.3
        pygame.draw.circle(screen, self.color, self.getPos(), r, 2)
        LGun=self.L/2
        p0=self.getPos()
        p1=rot([r, 0], (self.ang+self.angGun))
        p2=rot([r+LGun, 0], self.ang+self.angGun)
        pygame.draw.line(screen, self.color, np.add(p0, p1), np.add(p0, p2), 3)
        drawText(screen, f"{self.id} ({self.health})", self.x, self.y - self.L/2 - 12)
    def _calcClosestEnemy(self, tanks):
        enemies = []
        for tank in tanks:
            if tank.cmd != self.cmd and tank.health>0:
                enemies.append(tank)
        if not enemies:
            return None, None
        min_dist = 100500
        closest_enemy = None
        for enemy in enemies:
            if dist((self.x, self.y), (enemy.x, enemy.y))<min_dist:
                min_dist = dist((self.x, self.y), (enemy.x, enemy.y))
                closest_enemy = enemy
        return closest_enemy, min_dist

    def sim(self, dt, tanks):
        if self.health <=0:
            self.color = (0,0,0)
            return
        if self.ang<-np.pi:
            self.ang = np.pi*2 + self.ang
        elif self.ang>np.pi:
            self.ang = self.ang - 2*np.pi
        if self.angGun<-np.pi:
            self.angGun = np.pi*2 + self.angGun
        elif self.angGun>np.pi:
            self.angGun = self.angGun - 2*np.pi
        ang_gun = self.ang+self.angGun
        if ang_gun<-np.pi:
            ang_gun = np.pi*2 + ang_gun
        elif ang_gun>np.pi:
            ang_gun = ang_gun - 2*np.pi
        
        
        vec=[self.vlin, 0]
        vec=rot(vec, self.ang)

        enemy, enemy_dist = self._calcClosestEnemy(tanks)
        if enemy is not None:
            
            vec=[self.vlin, 0]
            vec=rot(vec, self.ang)
            self.x+=vec[0]*dt
            self.y+=vec[1]*dt
            if self.x>800:
                self.x-=800
            if self.y>600:
                self.y-=600
            if self.x<0:
                self.x+=800
            if self.y<0:
                self.y+=600
            enemy_ang = ang((enemy.x, enemy.y), (self.x,self.y))
            enemy_mv_vec = np.array(rot([enemy.vlin, 0],enemy.ang))*(self.cd + enemy_dist/200) + np.array(enemy.getPos())
            self_lin_vec = np.array(vec)*(self.cd) + np.array(self.getPos())
            enemy_ang_cd = ang(enemy_mv_vec, self_lin_vec)

            if enemy_dist>250:
                if abs(angDiff(self.ang, enemy_ang)) > abs(self.va*dt):
                    mod = angDiff(self.ang, enemy_ang)/abs(angDiff(self.ang, enemy_ang))
                    self.ang+=self.va*dt*mod
            else:
                if abs(angDiff(self.ang, enemy_ang+self.ugol_obezda)) > abs(self.va*dt):
                    mod = angDiff(self.ang, enemy_ang+self.ugol_obezda)/abs(angDiff(self.ang, enemy_ang+self.ugol_obezda))
                    self.ang+=self.va*dt*mod
            if self.use_strat:
                if abs(angDiff(ang_gun, enemy_ang_cd)) > abs(self.alin*dt)*3:
                    mod = angDiff(ang_gun, enemy_ang_cd)/abs(angDiff(ang_gun, enemy_ang_cd))
                    self.angGun +=self.vaGun * dt*mod
                else:
                    return self.fire(dt)
            else:
                if abs(angDiff(ang_gun, enemy_ang)) > abs(self.alin*dt)*3:
                    mod = angDiff(ang_gun, enemy_ang)/abs(angDiff(ang_gun, enemy_ang))
                    self.angGun +=self.vaGun * dt*mod
                else:
                    return self.fire(dt)

tanks = []
for i in range(4):
    tank=Tank(i*2, 215+random.randint(-50,50), 100+i*100+random.randint(-50,50), 1, 0)
    tank.vlin=80 + (random.random()-0.5)*40
    tank.va=2 + (random.random()-0.5)*0.5
    tank.vaGun=4+ (random.random()-0.5)*1
    tank.use_strat = True
    tank1=Tank(i*2+1, 615+random.randint(-50,50), 100+i*100+random.randint(-50,50), np.pi-1, 1)
    tank1.vlin=80 + (random.random()-0.5)*40
    tank1.va=2+ (random.random()-0.5)*0.5
    tank1.vaGun=4+ (random.random()-0.5)*1
    tank1.use_strat = True
    tanks.append(tank)
    tanks.append(tank1)

time_begin = time.time()
def getWinner(tanks):
    command0 = 0
    command1 = 0
    for tank in tanks:
        if tank.cmd==0:
            command0 +=tank.health
        if tank.cmd==1:
            command1 +=tank.health
    if command0<=0:
        return 1, command1
    if command1<=0:
        return 0, command0
    return None,None

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20
    bullets=[]

    while True:

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
        dt=1/fps
        for t in tanks:
            bullet = t.sim(dt, tanks)
            if bullet is not None:
                bullets.append(bullet)
        for b in bullets:
            b.sim(dt)
            if dist(b.getPos(), [sz[0] / 2, sz[1] / 2]) > sz[0]:
                b.exploded=True
            for t in tanks:
                if dist(t.getPos(), b.getPos())<t.L/2 and (t.health>0):
                    b.exploded = True
                    t.health-=10
                    break
        bullets=[b for b in bullets if not b.exploded]
        screen.fill((255, 255, 255))
        tank.draw(screen)
        for b in bullets: b.draw(screen)
        for t in tanks: t.draw(screen)
        drawText(screen, f"NBullets = {len(bullets)}", 5, 5)
        com, csum = getWinner(tanks)
        if com is not None:
            time_sim = datetime.timedelta(seconds = (time.time()-time_begin))

            drawText(screen, f"Command {com} wins with combined health {csum} in {time_sim}", 5,25)
            while True:
                for ev in pygame.event.get():
                    if ev.type==pygame.QUIT:
                        sys.exit(0)
                    pygame.display.flip()
                    timer.tick(fps)
        pygame.display.flip()
        timer.tick(fps)


main()