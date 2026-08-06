import numpy as np
import astropy
from astropy.io import fits
import glob
from astropy.stats import sigma_clip
import astroalign as aa
from datetime import datetime, timezone
import os
from format_converter import  convert_dng_to_fits, tiff_to_fits
from helpers import calc_image_scale
import subprocess
import zenith_coords
from astropy.time import Time
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from datetime import datetime
from astropy.stats import sigma_clipped_stats
from photutils.segmentation import detect_sources, SourceCatalog
from world_dir import ra_to_degrees, dec_to_degrees, get_ra_dec
import time as time_mod
import sys

# ========== GLOBAL PARAMS ==================
focal_length = 4.5 #mm
pixel_size = 1.55 #microns
sensor_width = 4056 #px
sensor_height = 3040 #px

# Measurements
ROI_Border = 0.2 # reject stars within this fraction of the edge of the frame

raw_image_path = "/home/thomas/Documents/Code/QuadStar/platesolving/test_images/SkyTest3/0.5s_5/"
raw_image_type = "dng"

ASTAP_PROG_NAME: str = "astap" #_cli"

# ===========================================

def add_RADEC_to_fits(file, coordinates_dict, average_obstime) :
    obstime = average_obstime
    data, header = fits.getdata(file, header=True)
    RA = float(coordinates_dict["RA"].deg)
    DEC = float(coordinates_dict["DEC"].deg)

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

def get_FWHM(image_path) : # UNUSED
    from photutils.detection import DAOStarFinder
    from astropy.stats import sigma_clipped_stats

    image = fits.getdata(image_path)
    mean, median, std = sigma_clipped_stats(image)

    finder = DAOStarFinder(
        threshold=5*std,
        fwhm=3.0,
    )

    sources = finder(image - median)
    print(sources)
    results = []

    for star in sources:
        m = measure_star(image, star["x_centroid"], star["y_centroid"])
        if m is not None:
            results.append(m)

    results = np.array(results)

    median_fwhm = np.median(results[:,0])
    median_ecc  = np.median(results[:,1])

    print("Stars:", len(results))
    print("Median FWHM:", median_fwhm)
    print("Median eccentricity:", median_ecc)

def measure_stars(image_path) :
    
    image = fits.getdata(image_path)
    mean, median, std = sigma_clipped_stats(image)
    threshold = median + 5*std
    segment_map = detect_sources(
        image,
        threshold,
        n_pixels=5
    )

    catalog = SourceCatalog(image, segment_map)
    eccentricities = []
    # ==== Define ROI =====
    # Should be an x and a y range where star measurements are accepted
    x_min = ROI_Border * sensor_width
    x_max = (1 - ROI_Border) * sensor_width
    y_min = ROI_Border * sensor_height
    y_max = (1 - ROI_Border) * sensor_height
 
    for source in catalog:
        
        if x_min < source.x_centroid < x_max :
            if y_min < source.y_centroid < y_max :
                eccentricities.append(source.eccentricity)

    print(f"Detected {len(catalog)} stars, kept {len(eccentricities)}")
    ecc = np.array([source.eccentricity for source in catalog])
    median_ecc = np.median(ecc)
    # Rejection Logic :
    if median_ecc > 0.9 :
        print(f"Frame should be rejected, median eccentricity = {median_ecc}")
        reject = True
    else :
        reject = False
    #print(np.median(ecc))
    return median_ecc, reject




# ==========================================================================

def main(raw_image_path, filetype) :
    start_time = time_mod.perf_counter()
    print(f"Starting QuadSolver...\nGood luck and clear skies!\n")
    print("=================================================================")
    print(f"Looking for {filetype} files in {raw_image_path}")

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
    timestamps = []
    if filetype == "dng" :
        for file in files :
            i += 1
            newname = f"{file.removesuffix(".dng")}".split("/")[-1]
            converted = convert_dng_to_fits(file, f"{fits_dir}/{newname}.fits")
            converted_files.append(converted)
            timestamps.append(f"{newname}".split("_")[-1])
    elif filetype == "tiff" :
        for file in files :
            i += 1
            newname = f"{file.removesuffix('.tiff')}".split("/")[-1]
            converted = tiff_to_fits(file, f"{fits_dir}/{newname}.fits")
            converted_files.append(converted)
            timestamps.append(f"{newname}".split(f"{newname}")[-1])
                 
    datetimes = []
    for time in timestamps :
        datetime_time = datetime.fromtimestamp(float(time), tz=timezone.utc)
        datetimes.append(datetime_time)
    timestamps = datetimes

    # ========= Extract timestamps =========
    print(f"First Timestamp: {min(timestamps)} = {min(datetimes)}")
    print(f"Last Timestamp: {max(timestamps)} = {max(datetimes)}")
    obstime = min(datetimes) # Images will have been captured close to each other, so the time from the first image will be fine.
    
    # ========= Measure Stats for images ========
    print("=================================================================")
    print("Measuring Star Stats...")
    ecc_list = []
    for image in converted_files :
        median_eccentricity, reject = measure_stars(image)
        if reject :
            converted_files.remove(image)
            print(f"Removed image <{image}> from processing pipeline")
        #print(median_eccentricity)
        ecc_list.append(median_eccentricity)
    print(f"Average eccentricity for all frames: {(sum(ecc_list))/(len(ecc_list))}")
    
    # ========= Align Images =========
    print("=================================================================") 
    reference = fits.getdata(converted_files[0]).astype(np.float32)
    frames = [reference] # np.array([fits.getdata(f).astype(np.float32) for f in files])
    if len(converted_files) > 1 : 
        print(f"Registering Frames...")
        i = 1
        for f in converted_files[1:]:
            try :
                source = fits.getdata(f).astype(np.float32)
                # Returns the aligned image and the transformation used
                aligned, footprint = aa.register(source, reference)
                print(f"Successfully aligned image {i}")
                frames.append(aligned)
                i += 1
            except :
                print(f"Oosp! Alignment failed for image: {f}")
        #aligned = []
        print(f"Aligned {len(frames)} images")
    else :
        print(f"WARNING: \nOnly one image... skipping alignment. Is this intentional?")

    # ========= Integrate Aligned Images =========
    print("=================================================================")
    print("Running image integration...")

    frames = np.stack(frames)
    print(f"Integrating {len(frames)} images...")
    result = sigma_clipped_stack(frames, sigma=2.5)

    # ========= Save integrated image to folder =========
    try :
        os.mkdir("./stacked/")
        print("Stacked images directory does not exist. Creating!")
    except :
        print("Found stacked image directory")
    output_path = f'./stacked/{obstime}.fits'
    fits.writeto(output_path, result, overwrite=True)
    print(f"Integration Complete: Image saved as {output_path}")

    # ========= Add coords, time, image scale to stacked file ==========
    print("=================================================================")
    print(f"Estimating RA/DEC of zenith for time {obstime}...")
    coordinates = zenith_coords.main(obstime)
    coordinates_dict = {
        "RA" : coordinates.ra,       #255.0, # THIS NEEDS TO BE IN DEGREES, NOT HOURS
        "DEC" : coordinates.dec        #-42.0
    }
    add_RADEC_to_fits(output_path, coordinates_dict, obstime)

    # ========= Run ASTAP =========
    print("=================================================================")
    print("Running ASTAP on integrated image...")
    print(f"------------------------------------")
    try:
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        result = subprocess.run(
            [ASTAP_PROG_NAME, "-f", output_path, "-d /home/thomas/Documents/Code/QuadStar/platesolving/ASTAP_DB", "-log" ],
            env=env
        )

    except subprocess.CalledProcessError as e:
        print(f"Failed: {e}")
    except subprocess.TimeoutExpired:
        print("Timeout")
    log_path = output_path.removesuffix(".fits")
    ra_str, dec_str = get_ra_dec(log_path + ".log")

    try:
        if ra_str is None or dec_str is None:
            print("No plate solution found. Try integrating more frames?")
        else:
            ra_hrs = ra_to_degrees(ra_str) / 15.0
            dec_degs = dec_to_degrees(dec_str)
            print(f"------------------------------------")
            print("SUCCESS!")
            print(f"RA : {ra_to_degrees(ra_str)}")
            print(f"DEC: {dec_to_degrees(dec_str)}")

    except Exception as e:
        print(f"Failed to convert ra or dec: {e}")

    end_time = time_mod.perf_counter()
    execution_time = end_time - start_time
    print(f"Executed in: {execution_time:.6f} seconds")
    
# ==============================================================================

if __name__ == "__main__" :
    if sys.argv[1] :
        if sys.argv[1] == '-f' :
            raw_image_path = sys.argv[2]
        
        main(raw_image_path, raw_image_type)

