import numpy as np
import pygame, sys
import pickle

colors=[(0,0,0),(255,0,0),(0,255,0),(0,0,255)]
R = 35
WIDTH=1000
HEIGHT=800
tasks = [] #технологические операции
ts0, ts1 = None, None #соединяемые задачи

def dist(p1, p2):
    dx=p2[0]-p1[0]
    dy=p2[1]-p1[1]
    return np.sqrt(dx*dx+dy*dy)

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    surf=font.render(s, True, (0,0,0))
    screen.blit(surf, (x,y))

# модель задачи
class Task:
    def __init__(self, id, x, y):
        self.id=id
        self.x=x
        self.y=y
        #состояние выполнения задачи
        #0 - недоступна, 1 - доступна, 2 - выполняется, 3 - завершена
        self.state=0
        self.inps=[]
        self.outs=[]
    def getPos(self):
        return (self.x, self.y)
    def draw(self, screen):
        pygame.draw.ellipse(screen, colors[self.state],
                            [self.x - R, self.y - R, 2 * R, 2 * R], 2)
        for ts in self.inps:
            pygame.draw.line(screen, (100,100,100), ts.getPos(), self.getPos(), 2)
        drawText(screen, f"T{self.id}", self.x, self.y)

#поиск задачи под курсором
def findTask(pos, r):
    for ts in tasks:
        if dist(pos, ts.getPos())<r:
            return ts

#поиск доступных для выполнения задач
def findPossibleTasks():
    for ts in tasks:
        if ts.state==0:
            if len(ts.inps)==0 or all([inp.state==3 for inp in ts.inps]):
                ts.state=1

#выполнение задач
def performTasks():
    res=[]
    for ts in tasks:
        if ts.state==1: ts.state=2
        elif ts.state==2: ts.state=3
    return res

def main():
    global tasks, ts0, ts1
    pygame.init()
    screen=pygame.display.set_mode((WIDTH,HEIGHT))

    #цикл отрисовки
    while True:
        for event in pygame.event.get():
            drag=pygame.key.get_pressed()[pygame.K_LSHIFT]
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                ts0 = findTask(event.pos, R)
                if ts0 is None and not drag:
                    ts=Task(len(tasks), *event.pos)
                    tasks.append(ts)
            if event.type == pygame.MOUSEBUTTONUP:
                if drag:
                    ts1 = findTask(event.pos, R)
                    if ts0 is not None and ts1 is not None:
                        ts0.outs.append(ts1)
                        ts1.inps.append(ts0)
                ts0=ts1=None
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_s:
                    f = open("scenario.bin", "wb")
                    pickle.dump(tasks, f)
                    f.close()
                if event.key==pygame.K_l:
                    f = open("scenario.bin", "rb")
                    tasks=pickle.load(f)
                    f.close()
                if event.key==pygame.K_1:
                    findPossibleTasks()
                if event.key==pygame.K_2:
                    performTasks()
                if event.key==pygame.K_3:
                    performTasks()
                    findPossibleTasks()

        screen.fill((255, 255, 255))

        for ts in tasks:
            # ts.simulate()
            ts.draw(screen)
        if drag and ts0 is not None:
            pygame.draw.line(screen, (100,100,100), ts0.getPos(), event.pos, 2)

        pygame.display.update()
        pygame.time.delay(50)


main()