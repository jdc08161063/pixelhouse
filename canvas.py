import cv2
import numpy as np
import collections
from pixelhouse.color.colors import NamedColors

matplotlib_colors = NamedColors()


class canvas():
    '''
    Basic canvas object for quad drawings. 
    Extent measures along the x-axis.
    '''

    def __init__(
            self,
            width=200,
            height=200,
            extent=4.0,
            name='pixelhouseImage',
    ):
        self._img = np.zeros((height, width, 3), np.uint8)
        self.name = name
        self.extent = extent
        self.layers = collections.defaultdict(list)
        

    def __repr__(self):
        return (
            f"pixelhouse (w/h) {self.height}x{self.width}, " \
            f"extent {self.extent}"
        )

    def get_max_layer_number(self):
        if not self.layers:
            return 0
        else:
            return max(self.layers.keys())

    @property
    def height(self):
        return self._img.shape[0]

    @property
    def width(self):
        return self._img.shape[1]

    @property
    def img(self):
        self._img = np.zeros_like(self._img)

        for ln in sorted(self.layers.keys()):
            for layer in self.layers[ln]:
                func, args, blend = layer

                # Saturate or blend the images together
                if blend:
                    dst = canvas(self.width, self.height).img
                    func(dst, *args)
                    cv2.add(self._img, dst, self._img)
                else:
                    func(self._img, *args)

        return self._img

    def transform_x(self, x):
        x *= self.width / 2.0
        x /= self.extent
        x += self.width / 2
        return int(x)

    def transform_y(self, y):
        y *= -self.height / 2.0
        y /= self.extent
        y += self.height / 2        
        return int(y)

    def transform_length(self, r):
        r *= (self.width/self.extent)
        return int(r)
    
    def transform_thickness(self, r):
        # If thickness is negative, leave it alone
        if r>0:
            return self.transform_length(r)
        return r
    

    def transform_color(self, c):
        if isinstance(c, str):
            return matplotlib_colors(c)
        return c

    @staticmethod
    def transform_angle(rads):
        # From radians into degrees, counterclockwise
        return -rads*(360/(2*np.pi))
    
    @staticmethod
    def get_lineType(antialiased):
        if antialiased:
            return cv2.LINE_AA
        return 8

    def load(self, f_image):
        raise NotImplementedError

    def show(self, delay=0):
        # Before we show we have to convert back to BGR
        dst = cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR)
        
        cv2.imshow(self.name, dst)
        cv2.waitKey(delay)

    def save(self, f_save):
        # Before we save we have to convert back to BGR
        dst = cv2.cvtColor(self.img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(f_save, dst)

    def append(self, func, args, blend, layer=None, **kwargs):
        if layer is None:
            layer = self.get_max_layer_number()
            
        self.layers[layer].append( [func, args, blend] )


######################################################################


if __name__ == "__main__":
    from artists import circle
    
    c = canvas(200,200,extent=4)

    color = 'olive'
    #c.circle(thickness=0.5,color=color)
    circle(c, thickness=0.5,color=color)
    
   
    c.show()
    
