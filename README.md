## Setup/install

To install run 
```bash
chmod +x install_script.sh
./install_script.sh 
python3 world_dir.py

```
### QuadSolver

QuadSolver is a module that :
1. Converts raw image files to FITS format
2. Measures the properties of the stars in the images to determine if it should be rejected or not (based on eccentricity)
3. Performs a star alignment on all images, which makes sure any movement between frames is removed and stacking will work properly
4. Integrates the images, currently using a sigma clipping rejection method.
5. Calculates the RA/DEC coordinates of the zenith from the defined location based on image timestamps 
6. Populates the integrated image's FITS header with RA/DEC, capture time, and image scale to make it easier for plate solving
7. Runs ASTAP to solve the image and find the precise astrometric solution

#### Instructions:
1. Check all of the Global Params at the top of the file, particularly the file paths and file types. The pixel size and focal length are very important too. Okay it's actually all important!
2. If you aren't already in the virtual environment, run ```source .venv/bin/activate```
3. Run ```pip install -r requirements.txt```
3. Run ```python QuadSolver.py```
4. Sit back and relax

#### Limitations:
While QuadSolver is perfect, it isn't yet perfect.