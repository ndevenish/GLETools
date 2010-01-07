from __future__ import with_statement

import pyglet
from util import Mesh, gl_init, ChangeValue, nested, quad
from gletools.gl import *
from gletools import (
    Screen, Projection, Lighting, Color, VertexObject, Texture, Framebuffer,
    ShaderProgram, FragmentShader,
)

class Heightmap(object):
    def __init__(self, source):
        self.source = source
        self.view = Screen(0, 0, source.width, source.height)

        self.vertex_texture = Texture(source.width, source.height, GL_RGB)
        self.normal_texture = Texture(source.width, source.height, GL_RGB)
        self.fbo = Framebuffer(
            self.vertex_texture,
            self.normal_texture,
        )
        self.fbo.drawto = GL_COLOR_ATTACHMENT0_EXT, GL_COLOR_ATTACHMENT1_EXT

        self.program = ShaderProgram(
            FragmentShader.open('shaders/heightmap_normal.frag'),
            offsets = (1.0/source.width, 1.0/source.height),
            scale = 0.2,
        )
        self.vbo = self.generate_vbo(source.width, source.height)

    def generate_vbo(self, width, height):
        v3f = []
        for z in range(height):
            for x in range(width):
                v3f.extend((x/float(width), 0, z/float(height)))

        n3f = []
        for z in range(height):
            for x in range(width):
                n3f.extend((0, 1, 0))

        at = lambda x, y: x+y*width

        indices = []
        for z in range(height-1):
            for x in range(width-1):
                indices.extend((
                    at(x, z), at(x, z+1), at(x+1, z+1)        
                ))
                indices.extend((
                    at(x, z), at(x+1, z+1), at(x+1, z)        
                ))

        return VertexObject(
            pbo                 = True,
            indices             = indices,
            dynamic_draw_v3f    = v3f,
            dynamic_draw_n3f    = n3f,
        )
 
        pass

    def update(self):
        with nested(self.fbo, self.view, self.source, self.program):
            quad(self.source.width, self.source.height, 0, 0)
            self.vbo.vertices.copy_from(self.vertex_texture)
            self.vbo.normals.copy_from(self.normal_texture)

    def draw(self):
        self.vbo.draw(GL_TRIANGLES)

if __name__ == '__main__':
    window = pyglet.window.Window()
    projection = Projection(0, 0, window.width, window.height, near=0.1, far=100)
    angle = ChangeValue()
    heightmap = Heightmap(
        Texture.open('images/heightmap.png')
    )

    @window.event
    def on_draw():
        window.clear()
        
        heightmap.update()

        with nested(projection, Lighting):
            glPushMatrix()
            glTranslatef(0, 0, -1)
            glRotatef(20, 1, 0, 0)
            glRotatef(angle, 0.0, 1.0, 0.0)
            glTranslatef(-0.5, 0, -0.5)
            heightmap.draw()
            glPopMatrix()

        heightmap.source.draw(10, 10)
        heightmap.vertex_texture.draw(148, 10)
        heightmap.normal_texture.draw(286, 10)

    gl_init()
    pyglet.app.run()
