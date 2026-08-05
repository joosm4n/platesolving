from astropy.io import fits

hdul = fits.open("stacked_result2.fits")
hdul.info()

for i, hdu in enumerate(hdul):
    print(f"\nHDU {i}:")
    print(type(hdu))
    print(hdu.header)
    print("Data:", None if hdu.data is None else hdu.data.shape)