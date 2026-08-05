import numpy as np
import astropy
from astropy.io import fits
import glob
from astropy.stats import sigma_clip
import astroalign as aa
from datetime import datetime
import os
from dng_to_fits import  convert_dng_to_fits, tiff_to_fits
from helpers import calc_image_scale
import subprocess
import zenith_coords

from astropy.time import Time
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from datetime import datetime


# ========== GLOBAL PARAMS ==================
focal_length = 4.5 #mm
pixel_size = 1.55 #microns

raw_image_path = "/home/thomas/Documents/Code/QuadStar/platesolving/test_images/SkyTest3/0.5s_5/"
raw_image_type = "tiff"

# ===========================================

def add_RADEC_to_fits(file, coordinates_dict) :
    obstime = datetime.now()
    data, header = fits.getdata(file, header=True)
    RA = coordinates_dict["RA"]
    DEC = coordinates_dict["DEC"]

    image_scale = calc_image_scale(pixel_size, focal_length)

    # 2. Add or update the RA and DEC keywords
    # Standard FITS format expects decimal degrees
    header["RA"] = RA     # Center RA in DEGREES 17
    header["DEC"] = DEC     # Center Dec in degrees -42

    header["SECPIX"] = (image_scale, "image scale in arcsec/pixel")
    header["DATE-OBS"] = (obstime.isoformat(), "UTC date and time when script ran")

    # Optional: Add descriptive comments
    header.comments["RA"] = "Right Ascension in decimal degrees"
    header.comments["DEC"] = "Declination in decimal degrees"
    print(f"Overwritten fits file with RA: {RA}, DEC: {DEC}")

    # 3. Save the modified header back to disk
    fits.writeto(file, data, header, overwrite=True)

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

# ==========================================================================

def main(raw_image_path, filetype) :

    # ======== Load Images ==========
    files = sorted(glob.glob(f"{raw_image_path}*.{filetype}"))
    print(f"Found {len(files)} frames")

    if not files:
        raise RuntimeError("No image files found.")

    # ======== Convert Raw images to FITS format =========
    now = datetime.now()
    fits_dir = (f"./{now}-fits/")
    os.mkdir(fits_dir)
    converted_files = []
    i=0
    if filetype == "dng" :
        for file in files :
            i += 1
            converted = convert_dng_to_fits(file, f"{fits_dir}/image{i}.fits")
            converted_files.append(converted)
    elif filetype == "tiff" :
        for file in files :
            i += 1
            converted = tiff_to_fits(file, f"{fits_dir}/image{i}.fits")
            converted_files.append(converted)

    # ========= Align Images =========
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

    # ========= Integrate Aligned Images =========
    frames = np.stack(frames)
    result = sigma_clipped_stack(frames, sigma=2.5)

    # ========= Save integrated image to folder =========
    try :
        os.mkdir("./stacked/")
    except :
        print("Stacked images directory already exists. Skipping!")
    output_path = f'./stacked/{datetime.now()}.fits'
    fits.writeto(output_path, result, overwrite=True)
    print(f"Integration Complete: Image saved as {output_path}")

    # ========= Add coords, time, image scale to stacked file ==========
    coordinates = zenith_coords.main()
    coordinates_dict = {
        "RA" : coordinates.ra,       #255.0, # THIS NEEDS TO BE IN DEGREES, NOT HOURS
        "DEC" : coordinates.dec        #-42.0
    }
    add_RADEC_to_fits(output_path, coordinates_dict)

    # ========= Run ASTAP =========
    ASTAP_PROG_NAME: str = "astap" #_cli"
    try:
        result = subprocess.run([ASTAP_PROG_NAME, "-f", output_path, "-log", "-d /home/thomas/Documents/Code/QuadStar/platesolving/ASTAP_DB" ])

    except subprocess.CalledProcessError as e:
        print(f"Failed: {e}")
    except subprocess.TimeoutExpired:
        print("Timeout")


if __name__ == "__main__" :
    main(raw_image_path, raw_image_type)
    