
from astropy.time import Time
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from datetime import datetime


def make_EarthLocation(coords_dict) :
    lat = coords_dict["latitude"]
    lon = coords_dict["longitude"]
    location = EarthLocation.from_geodetic(lon, lat, height=300)
    #print(location)
    return location

def estimate_zenith_coords(time, location) :
    altaz_frame = AltAz(obstime=time, location=location)
    zenith = SkyCoord(0.0,90.0, frame=altaz_frame, unit="deg")
    zenith_equatorial = zenith.transform_to("icrs")
    print(f"Zenith Coordinates for location {location} at time {time}:")
    print(f"RA: {zenith_equatorial.ra}")
    print(f"DEC: {zenith_equatorial.dec}")
    return zenith_equatorial

def main(time=Time.now()) :
    
    coord_dict = {
        "latitude" : -27.8305,
        "longitude" : 142.6080
    } 
    #time = Time.now()
    location = make_EarthLocation(coord_dict)
    return estimate_zenith_coords(time, location)
    