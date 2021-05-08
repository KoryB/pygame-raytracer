import math3d
from math3d import VectorN
import pygame, math

drawThickness = 3
FULL_INTENSITY = 1.00
NO_INTENSITY = 0.00

class Material(object):
    def __init__(self, diffuseColor, specularColor=VectorN((1,1,1)), hardness=18):
        self.mAmbient = diffuseColor.pairwise(VectorN((.3,.3,.3)))
        self.mDiffuse = diffuseColor
        self.mSpecular = specularColor

        self.mHardness = hardness

    def getPygameColor(self):
        return (255 * self.mDiffuse).iTuple()


class RayHitResult(object):
    def __init__(self, ray, obj):
        self.mRay = ray                   # The ray involved in the collision
        self.mHitObject = obj             # The other object in the collision
        self.mIntersectionPoints = []     # The intersection points on the primitive and ray
        self.mIntersectionDistances = []  # The distances along the ray to each of the intersection points.

    def getNormal(self, index=0):
        """
        This gets the normal vector of the specified point
        :param index: an optional paramater specifying which point to get normal of
        :return: a Vector3 object
        """

        if self.mHitObject.mIsAABB:
            point = self.mIntersectionPoints[index] - .001*self.mRay.mDirection
            return self.mHitObject.getNormal(point)
        else:
            return self.mHitObject.getNormal(self.mIntersectionPoints[index])

    def appendIntersection(self, dist):
        P = self.mRay.getPoint(dist)
        self.mIntersectionPoints.append(P)
        self.mIntersectionDistances.append(dist)


class Ray(object):
    def __init__(self, origin, direction, isNormalized=False):
        self.mOrigin = origin.copy()

        if not isNormalized:
            self.mDirection = direction.normalized_copy()
        else:
            self.mDirection = direction.copy()

    def pygameRender(self, surf, name=None, font=None):
        maxDist = surf.get_width() + surf.get_height()
        ptA = self.mOrigin.iTuple()[0:2]
        ptB = self.getPoint(maxDist).iTuple()[0:2]
        pygame.draw.line(surf, (255,255,255), ptA, ptB)
        pygame.draw.circle(surf, (255,255,255), ptA, 5)

        ptC = self.getPoint(20)

        if name != None and font != None:
            temps = font.render(name, False, (255,255,255))
            surf.blit(temps, (ptC[0] - temps.get_width() / 2, \
                              ptC[1] - temps.get_height() / 2))

    def getPoint(self, dist):
        return self.mOrigin + dist * self.mDirection


class Sphere(object):
    def __init__(self, center, radius, material):
        self.mCenter = center.copy()
        self.mRadius = radius
        self.mRadiusSq = radius ** 2
        self.mMaterial = material

        self.mIsAABB = False

    def pygameRender(self, surf, name=None, font=None):
        global drawThickness
        color = self.mMaterial.getPygameColor()
        pygame.draw.circle(surf, color, self.mCenter.iTuple()[0:2], self.mRadius, drawThickness)
        if name != None and font != None:
            temps = font.render(name, False, color)
            surf.blit(temps, (self.mCenter[0] - temps.get_width() / 2, \
                              self.mCenter[1] - temps.get_height() / 2))

    def getNormal(self, point):
        """
        Gets the normal at a point
        :param point: Point (VectorN) on object to calculate the normal
        :return: a normalized VectorN
        """

        return (point - self.mCenter) / self.mRadius

    def rayHit(self, R):
        toCenter = self.mCenter - R.mOrigin     # Vector from ray origin to sphere center
        projDist = toCenter.dot(R.mDirection)   # [scalar] Distance along ray to get closest to sphere center
        closestDistSq = toCenter.dot(toCenter) - projDist * projDist
        if closestDistSq >= self.mRadiusSq:
            # No hit!
            return None
        f = (self.mRadiusSq - closestDistSq) ** 0.5

        result = RayHitResult(R, self)
        if toCenter.magnitudeSquared() > self.mRadiusSq:
            # The Ray originates outside of the sphere
            if projDist - f > 0:
                result.appendIntersection(projDist - f)
            if projDist + f > 0:
                result.appendIntersection(projDist + f)
        else:
            # The Ray originates inside the sphere.
            result.appendIntersection(projDist + f)

        return result


class Plane(object):
    def __init__(self, normal, dvalue, material):
        self.mNormal = normal.normalized_copy()
        self.mD = dvalue
        self.mMaterial = material

        self.mIsAABB = False

    def pygameRender(self, surf, name=None, font=None):
        global drawThickness
        if abs(self.mNormal[0]) > abs(self.mNormal[1]):
            # More of a Vertical plane
            ptA = (int(self.mD / self.mNormal[0]), 0)
            y = surf.get_height() - 1
            ptB = (int((self.mD - self.mNormal[1] * y) / self.mNormal[0]), y)
        else:
            # More of a Horizontal plane
            ptA = (0, int(self.mD / self.mNormal[1]))
            x = surf.get_width() - 1
            ptB = (x, int((self.mD - self.mNormal[0] * x) / self.mNormal[1]))
        color = self.mMaterial.getPygameColor()
        pygame.draw.line(surf, color, ptA, ptB, drawThickness)

        if name != None and font != None:
            temps = font.render(name, False, color)
            surf.blit(temps, ((ptA[0] + ptB[0]) / 2 - temps.get_width() / 2, \
                              ( ptA[1] + ptB[1]) / 2 - temps.get_height() / 2 - 10))

    def getNormal(self, point):
        """
        Gets the normal at a point
        :param point: Point (VectorN) on object to calculate the normal
        :return: a normalized VectorN
        """

        return self.mNormal

    def rayHit(self, R):
        den = R.mDirection.dot(self.mNormal)
        if den == 0.0:
            # Ray is parallel to plane.  No hit.
            return None
        num = self.mD - R.mOrigin.dot(self.mNormal)
        t = num / den
        if t < 0:
            # A "backwards" hit -- ignore
            return None
        result = RayHitResult(R, self)
        result.appendIntersection(t)
        return result


class AABB(object):
    def __init__(self, ptA, ptB, material):
        self.mMinPt = ptA.copy()
        self.mMaxPt = ptB.copy()
        for i in range(ptA.mDim):
            if ptB[i] < self.mMinPt[i]:
                self.mMinPt[i] = ptB[i]
            if ptA[i] > self.mMaxPt[i]:
                self.mMaxPt[i] = ptA[i]
        self.mMaterial = material
        normals = (math3d.VectorN((-1,0,0)), math3d.VectorN((1,0,0)), \
                   math3d.VectorN((0,-1,0)), math3d.VectorN((0,1,0)), \
                   math3d.VectorN((0,0,-1)), math3d.VectorN((0,0,1)))
        self.mPlanes = []
        for i in range(6):
            if i % 2 == 0:
                p = self.mMinPt
            else:
                p = self.mMaxPt
            self.mPlanes.append(Plane(normals[i], normals[i].dot(p), material))

        self.mIsAABB = True

    def pygameRender(self, surf, name=None, font=None):
        global drawThickness
        dim = self.mMaxPt - self.mMinPt
        color = self.mMaterial.getPygameColor()
        pygame.draw.rect(surf, color, self.mMinPt.iTuple()[0:2] + dim.iTuple()[0:2], drawThickness)

        if name != None and font != None:
            temps = font.render(name, False, color)
            surf.blit(temps, (self.mMinPt[0] + dim[0] / 2 - temps.get_width() / 2, \
                              self.mMinPt[1] + dim[1] / 2 - temps.get_height() / 2))

    def getNormal(self, point):
        """
        Gets the normal at a point
        The point is assumed to be on the box
        :param point: Point (VectorN) on object to calculate the normal
        :return: a normalized VectorN
        """

        if   point[0] <= self.mMinPt[0]:
            return self.mPlanes[0].mNormal
        elif point[0] >= self.mMaxPt[0]:
            return self.mPlanes[1].mNormal
        elif point[1] <= self.mMinPt[1]:
            return self.mPlanes[2].mNormal
        elif point[1] >= self.mMaxPt[1]:
            return self.mPlanes[3].mNormal
        elif point[2] <= self.mMinPt[2]:
            return self.mPlanes[4].mNormal
        else:
            return self.mPlanes[5].mNormal

    def rayHit(self, R):
        hitDistances = []
        for i in range(6):
            planeResult = self.mPlanes[i].rayHit(R)
            if planeResult:
                # We hit that bounding plane.  Now see if we hit within the boundaries
                # of the plane.  Hint: if we hit a PLANE, we have exactly one hit (and
                # so one thing in result.mIntersectionDistances
                currentDimension = i // 2
                inBounds = True
                hitPoint = planeResult.mIntersectionPoints[0]
                hitDist = planeResult.mIntersectionDistances[0]
                for j in range(3):
                    if j == currentDimension:
                        continue
                    if hitPoint[j] < self.mMinPt[j] or hitPoint[j] > self.mMaxPt[j]:
                        inBounds = False
                        break
                if inBounds:
                    hitDistances.append(hitDist)
        # If hitDistances is empty, no hit.
        if len(hitDistances) == 0:
            result = None
        else:
            result = RayHitResult(R, self)
            for t in hitDistances:
                result.appendIntersection(t)
        return result


class CylinderY(object):
    def __init__(self, basePos, height, radius, material):
        self.mBase = basePos
        self.mHeight = height
        self.mRadius = radius
        self.mRadiusSq = radius ** 2
        self.mMaterial = material

        self.mIsAABB = False

    def pygameRender(self, surf, name=None, font=None):
        color = self.mMaterial.getPygameColor()
        pygame.draw.rect(surf, color, (self.mBase[0] - self.mRadius, self.mBase[1], self.mRadius * 2, self.mHeight), drawThickness)

        if name != None and font != None:
            temps = font.render(name, False, color)
            surf.blit(temps, (self.mBase[0] - temps.get_width()/2, self.mBase[1] + self.mHeight / 2 - temps.get_height() / 2))

    def getNormal(self, point):
        """
        Gets the normal at a point.
        The passed in point is assumed to be on the cylinder
        :param point: Point (VectorN) on object to calculate the normal
        :return: a normalized VectorN
        """

        if point[1] <= self.mBase[1]:
            # The point is on the bottom plane
            return VectorN((0, -1, 0))

        elif point[1] >= self.mBase[1] + self.mHeight:
            # The point is on the top plane
            return VectorN((0, 1, 0))

        else:
            # The point is now assumed to be on the cylindrical portion
            return (point - VectorN((self.mBase[0], point[1], self.mBase[2]))) / self.mRadius

    def rayHit(self, R):
        Ox = R.mOrigin[0]
        Oz = R.mOrigin[2]
        Dx = R.mDirection[0]
        Dz = R.mDirection[2]
        Bx = self.mBase[0]
        Bz = self.mBase[2]
        epsilon = 0.0001

        # Check the sides of the cylinder
        a = Dx ** 2 + Dz ** 2
        b = 2 * (-Bx * Dx - Bz * Dz + Ox * Dx + Oz * Dz)
        c = -2 * Bx * Ox - 2 * Bz * Oz + Bx ** 2 + Bz ** 2 + Ox ** 2 + Oz ** 2 - self.mRadiusSq
        inner = b ** 2 - 4 * a * c
        den = 2 * a
        if inner < 0 or den < epsilon:
            return None

        inner **= 0.5

        root1 = (-b + inner) / den
        root2 = (-b - inner) / den
        result = RayHitResult(R, self)
        oneHit = False
        if root1 > 0:
            P1 = R.getPoint(root1)
            if P1[1] >= self.mBase[1] - epsilon and P1[1] <= self.mBase[1] + self.mHeight + epsilon:
                oneHit = True
                result.appendIntersection(root1)
        if root2 > 0:
            P2 = R.getPoint(root2)
            if P2[1] >= self.mBase[1] - epsilon and P2[1] <= self.mBase[1] + self.mHeight + epsilon:
                oneHit = True
                result.appendIntersection(root2)

        # Now check the top / bottom of the cylinder
        planeT = Plane(math3d.VectorN((0,1,0)), self.mBase[1] + self.mHeight, self.mMaterial)
        planeB = Plane(math3d.VectorN((0,-1,0)), -self.mBase[1], self.mMaterial)
        resultT = planeT.rayHit(R)
        if resultT:
            P = resultT.mIntersectionPoints[0]
            if (P[0] - Bx) ** 2 + (P[2] - Bz) ** 2 < self.mRadiusSq:
                result.appendIntersection(resultT.mIntersectionDistances[0])
                oneHit = True
        resultB = planeB.rayHit(R)
        if resultB:
            P = resultB.mIntersectionPoints[0]
            if (P[0] - Bx) ** 2 + (P[2] - Bz) ** 2 < self.mRadiusSq:
                result.appendIntersection(resultB.mIntersectionDistances[0])
                oneHit = True

        if oneHit:
            return result
        else:
            return None


class Light(object):

    def __init__(self, pos, diffuse, specular):
        """
        This is the constructor for the point-light class
        :param pos: Position of the light
        :return: N/A
        """

        self.mPos = pos.copy()
        self.mDiffuse = diffuse
        self.mSpecular = specular


    def getIntensity(self, point):
        """
        This will be inherited and modified, for now just returns VectorN((1,1,1))
        :param point:
        :return:
        """

        return FULL_INTENSITY


class Spotlight(Light):

    def __init__(self, pos, diffuse, specular, innerAngle, outerAngle, direction, isNormalized=False):
        Light.__init__(self, pos, diffuse, specular)

        self.mInnerAngle = min(innerAngle, 179.99)
        self.mInnerHalfAngle = self.mInnerAngle/2
        self.mInnerHalfAngleTangent = math.tan(math.radians(self.mInnerHalfAngle))
        self.mInnerHalfAngleTangent2 = self.mInnerHalfAngleTangent ** 2

        self.mOuterAngle = min(outerAngle, 179.99)
        self.mOuterHalfAngle = self.mOuterAngle/2
        self.mOuterHalfAngleTangent = math.tan(math.radians(self.mOuterHalfAngle))
        self.mOuterHalfAngleTangent2 = self.mOuterHalfAngleTangent ** 2

        self.mTangent2Difference = self.mOuterHalfAngleTangent2 - self.mInnerHalfAngleTangent2

        if isNormalized:
            self.mDirection = direction
        else:
            self.mDirection = direction.normalized_copy()


    def getIntensity(self, point):

        # First check if point is inside inner cone, if yes return full intensity

        toPointVector = point - self.mPos
        toPointParallel = self.mDirection.dot(toPointVector)

        if toPointParallel > 0:

            toPointDist2 = toPointVector.magnitudeSquared()

            toPointParallel2 = toPointParallel**2
            toPointPerp2 = toPointDist2 - toPointParallel2

            toPointTangent2 = toPointPerp2 / toPointParallel2

            if toPointTangent2 <= self.mInnerHalfAngleTangent2:
                return FULL_INTENSITY
            elif toPointTangent2 <= self.mOuterHalfAngleTangent2:
                return 1 - (toPointTangent2 - self.mInnerHalfAngleTangent2)/self.mTangent2Difference
            else:
                return NO_INTENSITY

