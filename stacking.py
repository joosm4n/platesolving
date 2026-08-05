import numpy as np
import astropy
from astropy.io import fits
import glob
from astropy.stats import sigma_clip
import astroalign as aa
from datetime import datetime
import os
from dng_to_fits import  convert_dng_to_fits

#aa.register()

def main() :

    files = sorted(glob.glob("/home/thomas/Documents/Code/QuadStar/platesolving/test_images/SkyTest3/0.5s/*.dng"))
    print(f"Found {len(files)} frames")

    if not files:
        raise RuntimeError("No image files found.")

    now = datetime.now()
    fits_dir = (f"./{now}-fits/")
    os.mkdir(fits_dir)
    converted_files = []
    i=0
    for file in files :
        i += 1
        converted = convert_dng_to_fits(file, f"{fits_dir}/image{i}.fits")
        converted_files.append(converted)

    reference = fits.getdata(converted_files[0]).astype(np.float32)
    frames = [reference] # np.array([fits.getdata(f).astype(np.float32) for f in files])

    print(f"Registering Frames...")
    i = 1
    for f in converted_files[1:]:
        
        source = fits.getdata(f).astype(np.float32)
        # Returns the aligned image and the transformation used
        aligned, footprint = aa.register(source, reference)
        print(f"Successfully aligned image {i}")
        frames.append(aligned)
        i += 1

        #print(f"Number of frames = {len(frames)}")
    frames = np.stack(frames)
    #print(frames.shape)

    def sigma_clipped_stack(frames, sigma=2.5):

        print(f"Integrating Frames")
        """
        Stack frames using sigma-clipped mean.
        Each pixel position is evaluated independently across all frames.
        """
        # sigma_clip returns a masked array — rejected values are masked out
        clipped = sigma_clip(frames, sigma=sigma, axis=0, maxiters=3)

        # Mean of non-rejected values at each pixel position
        stacked = np.ma.mean(clipped, axis=0).data

        return stacked

    result = sigma_clipped_stack(frames, sigma=2.5)
    try :
        os.mkdir("./stacked/")
    except :
        print("Stacked images directory already exists. Skipping!")
    output_path = f'./stacked/{datetime.now()}.fits'
    fits.writeto(output_path, result, overwrite=True)
    print(f"Integration Complete: Image saved as {output_path}")



if __name__ == "__main__" :
    main()