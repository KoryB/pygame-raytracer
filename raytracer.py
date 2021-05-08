import pygame, math, threading
from math3d import VectorN
from objects3d import *

class Raytracer(object):

    def __init__(self, renderSurface, sceneAmbient=VectorN((1,1,1)), bgColor=(50, 50, 50)):
        """
        This is the raytracer class, it takes in the surface to render onto.
        :param surface: a pygame.Surface object
        :return: N/A
        """

        self.mRenderSurface = renderSurface
        self.mObjects = []
        self.mLights = []
        self.mBGColor = bgColor
        self.mSceneAmbient = sceneAmbient


        # Pygame Screen Variables
        self.mPyWidth, self.mPyHeight = self.mRenderSurface.get_size()

        self.mPyAspectRatio = self.mPyWidth / self.mPyHeight


        # Camera Variables
        self.mCamX = VectorN((1, 0, 0))
        self.mCamY = VectorN((0, 1, 0))
        self.mCamZ = VectorN((0, 0, 1))

        self.mCamPos = VectorN(3)

        self.mCamFOV = 45
        self.mCamNear = 1.0
        self.mCamCOI = VectorN(3)

        self.mCamUp = VectorN((0, 1, 0))


        # Virtual ViewPlane Variables
        self.mViewOrigin = VectorN(3)

        self.mViewHeight = self.mPyHeight + 0
        self.mHalfViewHeight = self.mViewHeight/2

        self.mViewWidth = self.mPyWidth + 0
        self.mHalfViewWidth = self.mViewWidth/2

        self.mVirtualPyWidthRatio = self.mViewWidth / self.mPyWidth
        self.mVirtualPyHeightRatio = self.mViewHeight / self.mPyHeight

        self.mFinalLightComponent = VectorN(3)


        #Tween variables, these are mostly offsets
        self.mIsTweening = True

        self.mTValues = []
        self.mCurTweenFrame = 0
        self.mNumTweenFrames = 0

        self.mTweenCamPos = VectorN(3)
        self.mTweenCamCOI = VectorN(3)
        self.mTweenCamUp = VectorN(3)
        self.mTweenCamFOV = 0
        self.mTweenCamNear = 0


    def setCamera(self, camPos, camCOI, camUp, camFOV, camNear, noTween=True):
        """
        This function sets up the camera for the raytracer

        This includes calculating the ViewOrigin of the virtual View Plane
        :param camPos: Position of the camera in world space
        :param camCOI: The focus point of the camera, where it faces
        :param camUp: General 'up' direction of the camera
        :param camFOV: The Vertical angle of the view of the camera
        :param camNear: The distance from the camera to the Virtual Plane, travelling along camZ
        :return: None
        """

        self.mCamPos = camPos
        self.mCamFOV = camFOV
        self.mCamNear = camNear
        self.mCamCOI = camCOI

        self.mCamZ = (self.mCamCOI - self.mCamPos).normalized_copy()

        self.mCamX = camUp.cross(self.mCamZ).normalized_copy()
        self.mCamY = self.mCamZ.cross(self.mCamX).normalized_copy()

        self.mHalfViewHeight = math.tan(math.radians(self.mCamFOV/2)) * self.mCamNear
        self.mViewHeight = self.mHalfViewHeight * 2

        self.mHalfViewWidth = self.mHalfViewHeight * self.mPyAspectRatio
        self.mViewWidth = self.mHalfViewWidth * 2

        self.mVirtualPyWidthRatio = self.mViewWidth / self.mPyWidth
        self.mVirtualPyHeightRatio = self.mViewHeight / self.mPyHeight

        self.mViewOrigin = self.mCamPos + self.mCamNear*self.mCamZ \
                           + self.mHalfViewHeight*self.mCamY \
                           - self.mHalfViewWidth*self.mCamX


    def setCameraTweenDest(self, numFrames, camPos=None, camCOI=None, camUP=None, camFOV=None, camNear=None):
        """
        This sets up the tween dest, which specify where the camera should go to.
        :param camPos: a Vector3
        :param camCOI: a Vector3
        :param camUP: a Vector3
        :param camFOV: a Float
        :param camNear: a Float
        :return: None
        """

        self.mIsTweening = True

        self.mTValues = []
        for i in range(1, numFrames+1):
            self.mTValues.append(i / numFrames)

        self.mNumTweenFrames = numFrames

        if camPos:
            self.mTweenCamPos = camPos - self.mCamPos

        if camCOI:
            self.mTweenCamCOI = camCOI - self.mCamCOI

        if camUP:
            self.mTweenCamUp = camUP - self.mCamUp

        if camFOV:
            self.mTweenCamFOV = camFOV - self.mCamFOV

        if camNear:
            self.mTweenCamNear = camNear - self.mCamNear


    def updateTween(self, function=None):
        """
        This updates the tween state by one frame
        :return: True if done with tweening, False otherwise
        """

        if not function:
            function = lambda t: 3*t**2 - 2*t**3

        if self.mIsTweening:
            self.mCamPos += self.mTweenCamPos * function(self.mTValues[self.mCurTweenFrame])
            self.mCamCOI += self.mTweenCamCOI * function(self.mTValues[self.mCurTweenFrame])
            self.mCamUp += self.mTweenCamUp * function(self.mTValues[self.mCurTweenFrame])
            self.mCamFOV += self.mTweenCamFOV * function(self.mTValues[self.mCurTweenFrame])
            self.mCamNear += self.mTweenCamNear * function(self.mTValues[self.mCurTweenFrame])

            self.setCamera(self.mCamPos, self.mCamCOI, self.mCamUp, self.mCamFOV, self.mCamNear)

            self.mCurTweenFrame += 1

            if self.mCurTweenFrame >= self.mNumTweenFrames:
                self.mIsTweening = False

        return self.mIsTweening


    def rotateAboutYAxis(self, angle):
        """
        This function rotates the camera position around the Y-Axis a specified angular amount.
        :param angle: the amount to rotate, in radians
        :return: None
        """

        cosAngle = math.cos(angle)
        sinAngle = math.sin(angle)

        self.mCamPos[0] = self.mCamPos[0]*cosAngle - self.mCamPos[2]*sinAngle
        self.mCamPos[2] = self.mCamPos[0]*sinAngle + self.mCamPos[2]*cosAngle

        self.setCamera(self.mCamPos, self.mCamCOI, self.mCamUp, self.mCamFOV, self.mCamNear)


    def calculatePixelPos(self, ix, iy):
        """
        This function contverts a pygame pixel position (ix, iy) into a Virtual View Plane Position
        :param ix: the X Position of the point
        :param iy: the Y Position of the point
        :return: a 3D VectorN, representing the world space position of the 2D input point.
        """

        virtualPixel = self.mViewOrigin \
                       + self.mVirtualPyWidthRatio*ix * self.mCamX\
                       - self.mVirtualPyHeightRatio*iy * self.mCamY

        return virtualPixel


    def rayCast(self, ray, isShadow=False, light=None):
        """
        This casts ray into the world, testing it on every object in the mObjects list
        :param ray:
        :return:
        """

        if light:
            lightDist2 = (light.mPos - ray.mOrigin).magnitudeSquared()

        resultList = []

        # First create the list
        for Object in self.mObjects:
            result = Object.rayHit(ray)

            if result:
                if isShadow and light:
                    for distance in result.mIntersectionDistances:
                        if distance*distance <= lightDist2:
                            return result
                else:
                    resultList.append(result)


        # Next find the smallest distance, assuming there were results
        if len(resultList) == 0 or len(resultList[-1].mIntersectionDistances) == 0:
            return None

        # If is light got this far, it should return None.
        if isShadow and light:
            return None

        distIndex = 0

        curReturnResult = resultList[-1]

        for result in resultList:
            for i in range(len(result.mIntersectionDistances)):
                if result.mIntersectionDistances[i] < curReturnResult.mIntersectionDistances[distIndex]:
                    distIndex = i
                    curReturnResult = result


        # Convert the filled hit result into just holding the smallest distance.
        curReturnResult.mIntersectionPoints = [curReturnResult.mIntersectionPoints[distIndex]]
        curReturnResult.mIntersectionDistances = [curReturnResult.mIntersectionDistances[distIndex]]

        return curReturnResult


    def getColorOfHit(self, hitData):
        """
        This returns the color of the result passed in, no special effects right now
        If hitData is None, jut returns the background color

        :param hitData: a RayHitResult Object, or None
        :return: A tuple of integers
        """

        if hitData:
            # return hitData.mHitObject.mMaterial.getPygameColor()

            ambient = hitData.mHitObject.mMaterial.mAmbient.pairwise(self.mSceneAmbient)

            if len(self.mLights):
                objNormal = hitData.getNormal()
                vectorToCam = -hitData.mRay.mDirection

                for light in self.mLights:
                    lightVector = (light.mPos - (hitData.mIntersectionPoints[0])).normalized_copy()
                    # Check collisions for shadow here

                    if self.rayCast(Ray(hitData.mIntersectionPoints[0] + objNormal*.001, lightVector, isNormalized=True), isShadow=True, light=light):
                        continue


                    # Check Light intensity if spotlight here
                    lightPortion = VectorN(3)

                    lightIntensity = light.getIntensity(hitData.mIntersectionPoints[0])
                    if lightIntensity:

                        # Check Diffuse light
                        diffuseStrength = lightVector.dot(objNormal)
                        # print(diffuseStrength, lightVector, objNormal)

                        if diffuseStrength > 0:
                            lightPortion += diffuseStrength * (light.mDiffuse.pairwise(hitData.mHitObject.mMaterial.mDiffuse))

                        # Check Specular
                        lightVectorParallel = objNormal * diffuseStrength
                        reflectionVector = 2*lightVectorParallel - lightVector

                        specularStrength = reflectionVector.dot(vectorToCam)

                        if specularStrength > 0:
                            # print(specularStrength)
                            lightPortion += specularStrength**hitData.mHitObject.mMaterial.mHardness * (light.mSpecular.pairwise(hitData.mHitObject.mMaterial.mSpecular))

                        ambient += lightPortion*lightIntensity

            return ambient


    def getColorOfHitRecursive(self, hitData, recursionDepth=5):

        if not hitData:
            if recursionDepth == 5:
                return self.mBGColor

            else:
                return VectorN(3)



        if recursionDepth == 5:
            self.mFinalLightComponent = self.getColorOfHit(hitData)

        objNormal = hitData.getNormal()
        vectorToCam = -hitData.mRay.mDirection

        refectionVectorParallel = vectorToCam.dot(objNormal)*objNormal
        reflectionVector = 2*refectionVectorParallel - vectorToCam

        self.mFinalLightComponent = .5*self.mFinalLightComponent + \
                                    .5*self.getColorOfHitRecursive(self.rayCast(
                                        Ray(hitData.mIntersectionPoints[0]+objNormal*.001, reflectionVector))
                                                                   , recursionDepth=recursionDepth-1)

        if recursionDepth == 5:
            self.mFinalLightComponent[0] = min(1, self.mFinalLightComponent[0])
            self.mFinalLightComponent[1] = min(1, self.mFinalLightComponent[1])
            self.mFinalLightComponent[2] = min(1, self.mFinalLightComponent[2])

            return (self.mFinalLightComponent*255).iTuple()

        else:
            return self.getColorOfHit(hitData)


    def renderOneLine(self, iy):
        """
        This renders the world onto one line of the pygame window

        :param iy: the y value of the line
        :return: None
        """

        for x in range(0, self.mPyWidth):
            direction = self.calculatePixelPos(x, iy) - self.mCamPos
            color = self.getColorOfHitRecursive(self.rayCast(Ray(self.mCamPos, direction)))

            self.mRenderSurface.set_at((x, iy), color)
