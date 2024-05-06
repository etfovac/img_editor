
class ImgType():
    def __init__(self):
        self.PNG = ".png"
        self.JPEG = ".jpg"
        self.GIF = ".gif"
        self.PPM = ".ppm"

class ImgSize(object):
    def __init__(self,
                 S=(320,240),
                 M=(640,480),
                 L=(1280,720),
                 ):
        self.Small = S
        self.Medium = M
        self.Large = L

class Prop():
    ImgSize = ImgSize()
    ImgType = ImgType()
    PreviewFile = "temp"+ImgType.PNG
