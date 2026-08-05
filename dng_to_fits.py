# Convert dng to fits

import astropy.io.fits as fits
import numpy as np
import rawpy


def convert_dng_to_fits(dng_path, fits_path):
    """Converts a DNG raw file to an astronomical FITS file."""
    # 1. Read the DNG file
    with rawpy.imread(dng_path) as raw:
        # Extract the raw, unprocessed sensor bayer data (un-debayered)
        # This keeps the pure 16-bit integer values required for scientific analysis
        raw_image_data = raw.raw_image.copy()

    # 2. Package data into an Astropy Primary HDU
    hdu = fits.PrimaryHDU(raw_image_data)

    # 3. Add minimum useful metadata to the FITS header
    hdu.header["ORIGIN"] = "Python DNG Converter"
    hdu.header["COMMENT"] = "Raw image sensor array without demosaicing."

    # 4. Write out the FITS file
    hdu.writeto(fits_path, overwrite=True)
    print(f"Successfully converted {dng_path} -> {fits_path}")
    return fits_path


# Example usage:
#convert_dng_to_fits("test_images/SkyTest3/0.5s/Ex:499991_Gain:1.0_Temp:5.0_1785837712.590334.dng", "output.fits")


import tifffile
from astropy.io import fits
import numpy as np

def tiff_to_fits(tiff_file, fits_file):
    image = tifffile.imread(tiff_file)

    # Ensure a sensible FITS datatype
    image = image.astype(np.float32)

    fits.writeto(
        fits_file,
        image,
        overwrite=True
    )
    print("File converted to fits")
    return fits_file


    