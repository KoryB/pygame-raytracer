#Kory Byrne
#Lab 01
#ETGG 1803
import math

class VectorN(object):
    """
    Used to make a Vector Object of any dimension. Will later be extended with
    the ability to use arithmetic operations on VectorN objects.
    """
    def __init__(self, param):
        """
        :param param: Can be either an int or a sequence type object, or a VectorN
        :return: N/A
        Will create a Vector of N length based on param.
        If param is an int, it will create a VectorN of length param, with float values of 0.0 filling mData
        If param is a sequence type or VectorN, the values of param will be copied into the new VectorN
        """

        if isinstance(param, int):
            self.mData = [0.0] * param
            self.mDim = param

        elif hasattr(param, "__len__") and hasattr(param, "__getitem__"):
            self.mData = []
            self.mDim = len(param)

            for element in param:
                self.mData.append(float(element))

        else:
            raise Exception(TypeError("<param> is of an unsupported type: " + str(type(param))))

    def __str__(self):
        """
        :return: String representation of self
        called when converting object to a string, will return useful information rather than just a memory address
        """
        header_str = "<Vector" + str(self.mDim) + ": "
        mData_str = ""
        footer_str = ">"

        for element in self.mData:
            mData_str += str(element) + ", "

        mData_str = mData_str[0:-2]

        return header_str + mData_str + footer_str

    def __len__(self):
        """
        :return: number of elements the VectorN contains. Returns mDim
        """

        return self.mDim

    def __getitem__(self, item):
        """
        :param item: index of mData trying to access
        :return: self.mData[item]
        """

        return self.mData[item]

    def __setitem__(self, key, value):
        """
        :param key: index of mData trying to access
        :param value: value attempting write into mData at index <key>
        :return: None
        """

        self.mData[key] = float(value)

    def __eq__(self, other):
        """
        :param other: another VectorN, if not a VectorN will return false
        :return: True if length of VectorN and all elements of mData are equal. False otherwise. False if not a VectorN
        Description: Tests each condition, returns false if a condition isn't met. True otherwise
        """

        if not isinstance(other, VectorN):
            return False

        if self.mDim != other.mDim:
            return False

        for i in range(0, self.mDim):
            if self.mData[i] != other.mData[i]:
                return False

        return True

    def __add__(self, other):
        """
        :param other: another VectorN, of same length
        :return: a VectorN where each element is equal to the corresponding element of self and other added individually
        """
        tmData = []

        if not isinstance(other, VectorN):
            raise Exception(TypeError("You can only add another Vector" + str(self.mDim) + " to this Vector" + str(self.mDim)))

        if self.mDim != other.mDim:
            raise Exception(TypeError("You can only add another Vector" + str(self.mDim) + " to this Vector" + str(self.mDim)))

        for i in range(0, self.mDim):
            tmData.append(self[i] + other[i])

        return VectorN(tmData)

    def __radd__(self, other):
        """
        :param other: another VectorN, of same length
        :return: a VectorN where each element is equal to the corresponding element of self and other added individually
        """
        return self + other

    def __sub__(self, other):
        """
        :param other: another VectorN, of same length
        :return: a VectorN where each element is equal to the corresponding element of self and other subtracted individually
        """

        if not isinstance(other, VectorN):
            raise Exception(TypeError("You can only subtract another Vector" + str(self.mDim) + " to this Vector" + str(self.mDim)))

        if self.mDim != other.mDim:
            raise Exception(TypeError("You can only subtract another Vector" + str(self.mDim) + " to this Vector" + str(self.mDim)))

        tmData = []

        for i in range(0, self.mDim):
            tmData.append(self[i] - other[i])

        return VectorN(tmData)

    def __rsub__(self, other):
        """
        :param other: another VectorN, of same length
        :return: a VectorN where each element is equal to the corresponding element of other and self subtracted individually
        """

        if not isinstance(other, VectorN):
            raise Exception(TypeError("You can only subtract another Vector" + str(self.mDim) + " to this Vector" + str(self.mDim)))

        if self.mDim != other.mDim:
            raise Exception(TypeError("You can only subtract another Vector" + str(self.mDim) + " to this Vector" + str(self.mDim)))

        tmData = []

        for i in range(0, self.mDim):
            tmData.append(other[i] - self[i])

        return VectorN(tmData)

    def __mul__(self, scaler):
        """
        :param scaler: a scaler number, either a float or an int
        :return: a new VectorN with elements equal to the corresponding values of self multiplied by scaler
        """

        if not isinstance(scaler, (int, float)):
            raise Exception(TypeError("You can only multiply this Vector by a scaler"))

        tmData = []

        for element in self.mData:
            tmData.append(float(element * scaler))

        return VectorN(tmData)

    def __rmul__(self, scaler):
        """
        :param scaler: a scaler number, either a float or an int
        :return: a new VectorN with elements equal to the corresponding values of self multiplied by scaler
        """
        
        return self * scaler

    def __truediv__(self, scaler):
        """
        :param scaler: a scaler number, either a float or an int
        :return: a new VectorN with elements equal to the corresponding values of self divided by scaler
        """

        if not isinstance(scaler, (int, float)):
            raise Exception(TypeError("You can only divide this Vector by a scaler"))

        tmData = []

        for element in self.mData:
            tmData.append(float(element / scaler))

        return VectorN(tmData)
    
    def __rtruediv__(self, other):
        """ 
        :param other: doesn't matter
        :return: a NotImplementedError
        """
        
        raise Exception(NotImplementedError("You cannot divide anything by a VectorN"))

    def __neg__(self):
        """
        :return: a new VectorN with elements equal to the corresponding values of self * -1
        """

        tmData = []

        for element in self.mData:
            tmData.append(-element)

        return VectorN(tmData)

    def copy(self):
        """
        :return: a new VectorN object with the same values of self
        """
        newVectorN_data = []

        for element in self.mData:
            newVectorN_data.append(float(element))

        return VectorN(newVectorN_data)

    def iTuple(self):
        """
        :return: a tuple of integer values of mData
        """
        tlist = []

        for element in self.mData:
            tlist.append(int(element))

        return tuple(tlist)

    def isZero(self):
        """
        :return: True if all elements of mData are equal to 0.0, False otherwise
        """

        rv = True

        for element in self.mData:
            rv = element == 0.0

            if not rv:
                break

        return rv

    def magnitude(self):
        """
        :return: the magnitude of self. Equal to the sqrt of the sum of squares of the elements of mData
        """

        if self.isZero():
            return 0

        else:
            squared_sum = 0

            for element in self.mData:
                squared_sum += element ** 2

            return squared_sum ** .5

    def magnitudeSquared(self):
        """
        simple function to quickly get the magnitude squared of a vector. computed with Dot Product
        :return: the magnitude squared of a vector.
        """

        if self.isZero():
            return 0

        else:
            return self.dot(self)

    def normalized_copy(self):
        """
        :return: if self is not zero, a copy of self, with each element divided by self'-s magnitude. returns self.copy() otherwise
        """
        if self.isZero():
            return self.copy()

        else:
            magnitude = self.magnitude()
            tmData = []

            for element in self.mData:
                tmData.append(float(element / magnitude))

            return VectorN(tmData)

    def dot(self, otherVector):
        """
        Computes the dot product between self and another VectorN of the same length.

        :param otherVector: another VectorN of the same length as self, raises an error if this is not the case.
        :return: None.
        """
        if not isinstance(otherVector, VectorN):
            raise Exception(TypeError("dot product must be with a VectorN"))

        if self.mDim != otherVector.mDim:
            raise Exception(TypeError("dot product must be with a Vector" + str(self.mDim)))

        dotProduct = 0.0
        for i in range(self.mDim):
            dotProduct += self.mData[i] * otherVector.mData[i]

        return dotProduct

    def cross(self, otherVector3):
        """
        This function preforms the cross product of two 3D VectorN's, and returns the result.
        :param otherVector3: a 3D VectorN
        :return: a 3D VectorN, representing the normal to the plane the two Vectors make
        """

        if not isinstance(otherVector3, VectorN):
            raise Exception(TypeError("cross product must be with a VectorN"))

        if self.mDim != 3:
            raise Exception(TypeError("cross product must be with a Vector3, the left hand vector is a Vector" + str(self.mDim)))

        if self.mDim != 3:
            raise Exception(TypeError("cross product must be with a Vector3, the right hand vector is a Vector" + str(otherVector3.mDim)))


        crossVector = VectorN((
            self[1]*otherVector3[2] - self[2]*otherVector3[1],
            self[2]*otherVector3[0] - self[0]*otherVector3[2],
            self[0]*otherVector3[1] - self[1]*otherVector3[0]
        ))

        return crossVector

    def pairwise(self, otherVector):
        """
        This function computes the pairwise product on two VectorN objects
        :param otherVector: a VectorN object of the same length as self
        :return: a VectorN with each respective element of the two input vectors multiplied together
        """

        if not isinstance(otherVector, VectorN):
            raise Exception(TypeError("pairwise product must be with a VectorN"))

        if self.mDim != otherVector.mDim:
            raise Exception(TypeError("pairwise product must be with a Vector" + str(self.mDim)))

        pairwiseList = []

        for i in range(self.mDim):
            pairwiseList.append(self[i]*otherVector[i])

        return VectorN(pairwiseList)


if __name__ == "__main__":
    # # Note: By adding this if statement, we'll only execute the following code
    # # if running this module directly (F5 in Idle, or the play button in
    # # pyscripter). But…if we import this module from somewhere else (like our
    # # raytracer), it won't execute this code. Neat trick, huh?
    # import pygame
    # v = VectorN(5)
    # print(v) # <Vector5: 0.0, 0.0, 0.0, 0.0, 0.0>
    # w = VectorN((-1.2, "3", 5))
    # # q = VectorN(pygame.Surface((10,10))) # Should raise an exception
    # # q = VectorN((1.2, "abc", 5)) # Should raise an exception
    # # q = VectorN("abc") # Should raise an exception
    # x = VectorN(w)
    # print(x)
    # print(w) # <Vector3: 1.2, 3.0, 5.0>
    # z = w.copy()
    # z[0] = 9.9
    # z[-1] = "6"
    # # z["abc"] = 9.9 # Should raise an exception
    # print(z) # <Vector3: 9.9, 3.0, 6.0>
    # print(w) # <Vector3: 1.2, 3.0, 5.0>
    # print(z == w) # False or print(z.__eq__(w))
    # print(z == VectorN((9.9, "3", 6))) # True
    # print(z == 5) # False
    # w[1] = 5
    # print(w, x)
    # print(x)
    # print(z[0]) # 9.9
    # print(len(v)) # 5
    # print(w.iTuple()) # (1, 3, 5)

    v = VectorN((13.5, 52.3, -55))
    w = VectorN((-5555, 40065, -.00523))

    print(v.cross(w))
