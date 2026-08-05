import numpy as np
import astropy
import PIL

def calc_image_scale(pixel_size, focal_length) : # Calculates the image scale based on sensor specs and optics
    return 206 * pixel_size / focal_length
    




#=================== RUN ====================#

if __name__ == "__main__" :
    print(f"Image Scale: {calc_image_scale(1.5, 16)} arcsec/pixel")
