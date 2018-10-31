import pyglet.gl as gl
from settings import *

class Camera(object):
    def __init__(self, width, height):
        self.x, self.y = 0, 0
        self.width = width
        self.height = height
#        self.reset_camera()

    def get_mat(self,matlist):
        mat = (gl.GLfloat*16)()
        mat[:] = matlist
        return mat

    def reset_camera(self):
        gl.glLoadIdentity()
        self.move(-int(self.width/2/TILESIZE),-int(self.height/2/TILESIZE))
#        self.invert_y_axis()

    def set_camera_pos_pix(self, px,py):
        gl.glLoadIdentity()
#        px += int(self.width/2/TILESIZE)
#        py += int(self.height/2/TILESIZE)
        px += TILESIZE/2 - self.width/2
        py += TILESIZE/2 - self.height/2
        mat = self.get_mat([1,0,0,0, 0,1,0,0, 0,0,1,0, -px,-py,0,1])
        self.apply(mat)

    def invert_y_axis(self):
        mat = self.get_mat([1,0,0,0, 0,-1,0,0, 0,0,1,0, 0,0,0,1])
        self.apply(mat)

    def move_pix(self, dx, dy):
        mat = self.get_mat([1,0,0,0, 0,1,0,0, 0,0,1,0, -dx,-dy,0,1])
        self.apply(mat)

    def move(self, dx, dy):
        dx = int(dx)
        dy = int(dy)
        self.x += dx
        self.y += dy
        self.move_pix(dx*TILESIZE,dy*TILESIZE)

    def apply(self, mat):
        gl.glMultMatrixf(mat)
