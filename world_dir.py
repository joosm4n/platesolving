#!/usr/bin/env python3
import re
from pathlib import Path
import subprocess
from skyfield.positionlib import ICRF, position_of_radec
from skyfield.api import load
from skyfield.framelib import itrs
from datetime import datetime, UTC
import math
import numpy as np
from scipy.optimize import least_squares, minimize

ts = load.timescale()
t = ts.from_datetime(datetime.now(UTC))


def get_ra_dec(log_file: str) -> tuple[str | None, str | None]:
    """
    Extract RA and DEC from an ASTAP log file.

    Returns:
        (ra, dec) as strings, or (None, None) if no solution is found.
    """

    pattern = re.compile(
        r"Solution found:\s*"
        r"(\d{1,2}:\s*\d{2}\s+\d{2}(?:\.\d+)?)\s+"  # RA
        r"([+-]?\d+°\s*\d{2}\s+\d{2}(?:\.\d+)?)"  # DEC
    )

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                ra = " ".join(match.group(1).split())
                dec = " ".join(match.group(2).split())
                return ra, dec

    return None, None


def ra_to_degrees(ra: str) -> float:
    hms = ra.replace(":", " ").split()
    h, m, s = map(float, hms)
    return (h + m / 60 + s / 3600) * 15


def dec_to_degrees(dec: str) -> float:
    dec = dec.replace("°", " ")
    parts = dec.split()
    sign = -1 if parts[0].startswith("-") else 1
    d = abs(float(parts[0]))
    m = float(parts[1])
    s = float(parts[2])
    return sign * (d + m / 60 + s / 3600)


def raw_unit_vector(ra_hrs: float, dec_degs: float) -> tuple[float, float, float]:

    ra_rad = math.radians(ra_hrs * 15.0)
    dec_rad = math.radians(dec_degs)
    x = math.cos(dec_rad) * math.cos(ra_rad)
    y = math.cos(dec_rad) * math.sin(ra_rad)
    z = math.sin(dec_rad)

    return (x, y, z)


def enu_to_ecef(lat, lon) -> np.ndarray:

    sl = np.sin(lat)
    cl = np.cos(lat)

    sb = np.sin(lon)
    cb = np.cos(lon)

    return np.array([[-sb, -sl * cb, cl * cb], [cb, -sl * sb, cl * sb], [0, cl, sl]])


def residual(x, cam_enu, star_ecef) -> float:
    lat, lon = x
    pred = enu_to_ecef(lat, lon) @ cam_enu
    return pred - star_ecef


def solve(cam_enu, star_ecef) -> tuple[float, float]:
    guess = np.radians([0, 0])

    dir_earth_centre = np

    sol = least_squares(residual, guess, args=(cam_enu, star_ecef))

    lat = np.degrees(sol.x[0])
    lon = np.degrees(sol.x[1])
    return (lat, lon)


ASTAP_PROG_NAME: str = "astap_cli"

if __name__ == "__main__":
    file_name = "Light_M_8_011"

    try:
        result = subprocess.run([ASTAP_PROG_NAME, "-f", file_name + ".fits", "-log"])

    except subprocess.CalledProcessError as e:
        print(f"Failed: {e}")
    except subprocess.TimeoutExpired:
        print("Timeout")

    ra_str, dec_str = get_ra_dec(file_name + ".log")

    try:
        if ra_str is None or dec_str is None:
            print("No plate solve found.")
        else:
            ra_hrs = ra_to_degrees(ra_str) / 15.0
            dec_degs = dec_to_degrees(dec_str)
            print(f"RA : {ra_to_degrees(ra_str)}")
            print(f"DEC: {dec_to_degrees(dec_str)}")

            vec = position_of_radec(ra_hrs, dec_degs, t=t)
            print(f"skyfield Vec: {vec.distance()}")

            ecef = vec.frame_xyz(itrs).km
            ecef_norm = ecef / np.linalg.norm(ecef)
            print(f"ecef: {ecef}")

            # NOTE: Gravity is ~ 9.69m/s^2 at 40km, calculate this further

            gx = 0.95
            gy = gz = 0.22079
            grav = np.array([gx, gy, gz])
            grav_norm = grav / np.linalg.norm(grav)

    except Exception as e:
        print(f"Failed to convert ra or dec: {e}")
