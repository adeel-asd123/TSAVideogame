from panda3d.core import VideoTexture, MovieTexture, WindowProperties
from direct.showbase.ShowBase import ShowBase

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Load the video file
        video = MovieTexture("my_video")
        video.read(r"models/cutscene.avi")

        # Apply the video texture to a card
        card = self.loader.loadModel(r"models/card.glb")
        card.reparentTo(self.render2d)
        card.setTexture(video)
        # Play the video
        video.play()

app = MyApp()
app.run()