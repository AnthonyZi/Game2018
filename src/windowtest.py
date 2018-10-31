import pyglet as pg

class Test(pg.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame_rate = 1/30

        pimg= pg.image.load("../res/char7.png")
        pimg_seq = pg.image.ImageGrid(pimg, 4, 4, item_width=32, item_height=32)

        def get_anim_sprite(pimg_seq,i,t,x,y):
            a = i*4
            b = a+4
            anim = pg.image.Animation.from_image_sequence(pimg_seq[a:b], t, loop=True)
            return pg.sprite.Sprite(anim, x,y)

        def get_sprite(pimg_seq,i,x,y):
            a = i*4
            return pg.sprite.Sprite(pimg_seq[a],x,y)

        self.sprites = dict()

        self.sprites["ad"]    = get_anim_sprite(pimg_seq, 3, 0.25, 200, 200)
        self.sprites["al"]    = get_anim_sprite(pimg_seq, 2, 0.25, 250, 200)
        self.sprites["au"]    = get_anim_sprite(pimg_seq, 0, 0.25, 300, 200)
        self.sprites["ar"]    = get_anim_sprite(pimg_seq, 1, 0.25, 350, 200)
        self.sprites["d"]    = get_sprite(pimg_seq, 3, 200, 250)
        self.sprites["l"]    = get_sprite(pimg_seq, 2, 250, 250)
        self.sprites["u"]    = get_sprite(pimg_seq, 0, 300, 250)
        self.sprites["r"]    = get_sprite(pimg_seq, 1, 350, 250)

    def start(self):
        pg.clock.schedule_interval(self.update, self.frame_rate)
        pg.app.run()

    def update(self,dt):
        pass

    def on_draw(self):
        self.clear()
        for k in self.sprites.keys():
            self.sprites[k].draw()

if __name__ == "__main__":

    t = Test()
    t.start()
