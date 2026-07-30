## What this does

- world_dir.py
Currently this will take a .fits file and try to plate solve it for Right Ascension and Declination, and is currently outputting an Astropy ICRS object.
 
- preprocess_img.py
This currently takes a .fits file and finds the standard deviation of all the pixels, this is a simple and quick way to check the sharpness. 
Will need to test/calculate what a good or bad reading for this should be.

## Setup/install

To install clone the repo and run 
```bash
cd platesolving
chmod +x install_script.sh
./install_script.sh 
python3 world_dir.py
```
