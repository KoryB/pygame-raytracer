import pygame, math
from math3d import *
from objects3d import *
import raytracer


# Pygame setup
pygame.display.init()
screen = pygame.display.set_mode((300, 200))
done = False
currentLine = 0

# Raytracer setup
RT = raytracer.Raytracer(screen)
RT.mObjects.append(Plane(VectorN((0,1,0)), 0, Material(VectorN((1,1,0)))))
RT.mObjects.append(Sphere(VectorN((0,0,0)), 10, Material(VectorN((1,0,0)))))
RT.mObjects.append(AABB(VectorN((25,5,0)), VectorN((40,25,20)), Material(VectorN((0,1,0)))))
RT.mObjects.append(CylinderY(VectorN((-17,6,30)), 22.0, 15.0, Material(VectorN((0.7,0.7,1)))))

RT.mLights.append(Spotlight(VectorN((0, 55, 0)), VectorN((.5,1,1)), VectorN((1,1,1)), 30, 70, VectorN((0, -1, 0)), isNormalized=True))
# RT.mLights.append(Light(VectorN((-10,3,-20)), VectorN((1,1,1)), VectorN((1,1,1))))

# print(RT.mObjects[0].mMinPt, RT.mObjects[0].mMaxPt)
RT.setCamera(VectorN((0, 3, -50)), VectorN((0, 0, 1)), VectorN((0, 1, 0)), 60.0, 1.0)
# RT.setCameraTweenDest(6, camCOI=VectorN((-17, 6, 30)))
deltaAngle = math.pi / 50
numPics = 0
while not done:
    # Input
    eList = pygame.event.get()
    for e in eList:
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            done = True

    # Draw
    if currentLine < screen.get_height():
        RT.renderOneLine(currentLine)
        currentLine += 1

    pygame.display.flip()

pygame.display.quit()
