import numpy as np
import astropy
from astropy.io import fits
import glob
from astropy.stats import sigma_clip
import astroalign as aa

#aa.register()

def main() :

    files = sorted(glob.glob("/home/thomas/Documents/Code/QuadStar/platesolving/test_images/M_8/*.fits"))
    print(f"Found {len(files)} frames")

    if not files:
        raise RuntimeError("No FITS files found.")

    reference = fits.getdata(files[0]).astype(np.float32)
    frames = [reference] # np.array([fits.getdata(f).astype(np.float32) for f in files])

    print(f"Registering Frames...")
    i = 1
    for f in files[1:]:
        
        source = fits.getdata(f).astype(np.float32)
        # Returns the aligned image and the transformation used
        aligned, footprint = aa.register(source, reference)
        print(f"Successfully aligned image {i}")
        frames.append(aligned)
        i += 1

        #print(f"Number of frames = {len(frames)}")
    frames = np.stack(frames)
    print(frames.shape)

    #meanstack = np.mean(frames, axis=0)

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
    print(type(result))
    fits.writeto('stacked_result2.fits', result, overwrite=True)



if __name__ == "__main__" :
    main()