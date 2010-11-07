from contextlib import nested
import math

import pyglet
from pyglet.gl import *

from gletools import ShaderProgram, Matrix, Texture, Sampler2D, DepthTest

from util import View, make_plane

config = Config(buffers=2, samples=4)
window = pyglet.window.Window(config=config, fullscreen=True, vsync=False)
view = View(window)

size = 1024*4
diffuse = Texture.raw_open('data/patches/snowy_mountains.diffuse', 
    width=size, height=size, format=GL_RGBA32F,
    mipmap=4, filter=GL_LINEAR_MIPMAP_LINEAR, clamp='st',
    unit=GL_TEXTURE0,
)
terrain = Texture.raw_open('data/patches/snowy_mountains.terrain',
    width=size, height=size, format=GL_RGBA32F,
    unit=GL_TEXTURE1, clamp='st',
)
noise_tile = Texture.open('data/tilable_noise.png', 
    mipmap=4, filter=GL_LINEAR_MIPMAP_LINEAR, unit=GL_TEXTURE2,
)

program = ShaderProgram.open('terrain.shader',
    diffuse = Sampler2D(GL_TEXTURE0),
    terrain = Sampler2D(GL_TEXTURE1),
    noise_tile = Sampler2D(GL_TEXTURE2),
    lod_factor = 4.0,
)

vbo = make_plane(128, 128)
fps = pyglet.clock.ClockDisplay(color=(144.0/255.0,195.0/255.0,6.0/255.0,0.5))

@window.event
def on_draw():
    window.clear()

    model = Matrix().rotatex(-0.25).translate(-0.5, -0.5, 0.0)
    projection = Matrix.perspective(window.width, window.height, 65, 0.0001, 100.0)
    modelview = view.matrix * model

    program.vars.mvp = projection * modelview
    program.vars.screen_size = float(window.width), float(window.height)

    with nested(DepthTest, diffuse, terrain, noise_tile, program):
        glPatchParameteri(GL_PATCH_VERTICES, 4);
        vbo.draw(GL_PATCHES)
   
    fps.draw()

if __name__ == '__main__':
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glClearColor(1,1,1,1)
    pyglet.app.run()
