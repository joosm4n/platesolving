#!/usr/bin/env python3

import numpy as np
from astropy.io import fits

def std_dev_of_raw_file(file_name: str, log: bool) -> float:
    data = fits.getdata(file_name)
    data = np.asarray(data)
    f = data

    if log:
        print("Shape :", data.shape)
        print("Type  :", data.dtype)
        print(f"Mean  : {data.mean():.2f}")
        print(f"Std   : {data.std():.2f}")
    return data.std()


def main():
    file_name: str = "Light_M_8_011.fits"
    std_dev_of_raw_file(file_name, log=True)

if __name__ == "__main__":
    main()



