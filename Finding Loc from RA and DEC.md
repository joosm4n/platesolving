[](https://astronomy.stackexchange.com/posts/38290/timeline)

### Question:
Given a picture of stars - assume it is possible to identify the stars and their Right Ascension (RA) and Declination (Dec). By choosing one near the center of the image (or interpolating RA/Dec to the center) the effective "pointing angle" of the camera would be known.

With the RA/Dec of the camera, plus the Roll (R), Pitch (P), and Yaw (Y) of the camera, and the precise time (TAI, UTC, and/or UT1) the picture was taken... how would a location calculation of where the camera was on Earth when it was taken be possible (assume it is possible).

It seems like it would be a simple coordinate transformation, however understanding how time affects the calculation isn't clear. I can't find a simple resource of algorithms to find one close enough.

ETA: Roll, Pitch, and Yaw could be found in a few different ways... in my current case I took a good first initial "guess" and then plotted an overlay of stars based on perturbing the initial first guess until the stars overlaid well over the image (of course, this required I knew where the picture was taken!) However, it is also possible to know R,P,Y based on a local gravity vector and inertial mechanics (a simply INU)... which is where I would eventually like to get to.

The RA and Dec is currently found using [http://astrometry.net/](http://astrometry.net/) by uploading the picture they returned astrometric meda-data.

Here is an example set of numbers: R=10.7deg, P=63.1deg, Y=-174.8deg

Time=2016,Oct,1,0hr,31m,28s

Leap Secs=36 GPS-TAI

UT1-UTC = -0.28

Center of Image (~pointing vector of camera)

RA = 90.7 (6h,2m,53.422s),

Dec=3.56(3deg, 33' 24.95)

### Answer 

Picture was taken somewhere near 30°22'02.0"N 75°00'35.7"E Bathinda, Punjab, India.

Answering your question about time - how it enters into the sight reduction: RA, all by itself, isn't useful. It's the angle between the plane of the meridian of a celestial location and the plane of the meridian of the first point of Aries. That angle is more or less fixed, but the first point of Aries, and its meridian, are continually changing, going through 360 degrees in a sidereal day.

Assumptions: pitch is the altitude of the celestial location (its angular distance above the horizon), and it's not corrected for refraction. Yaw is the azimuth of the location, CW degrees from north.

General method: knowing the time, find the Greenwich hour angle (GHA) of the first point of Aries at that time, by interpolating between hourly values in an almanac. The GHA of the celestial location is the GHA of Aries minus RA. The geographical position (GP) of a celestial location, is the point on the earth's surface where the celestial location is in the zenith. The GP I found after some number crunching was 3.56 deg N, 72.655 deg E. It's in the middle of the Arabian Sea. That GP, the observer's unknown location, and the north pole form a spherical triangle, which must be solved to get the observer's location fix. Two sides and an angle are known: one of the sides is 90 deg minus the latitude of the GP, the other is 90 deg minus the observed altitude of the celestial location. The angle is the 360 deg minus the azimuth of the location. It's one of those awkward spherical triangles where the angle is not the included angle between the sides. It's solved by first using the law of sines to find the angle at the pole then using Napier's Analogies to find the third side.

In this particular case, the celestial location GP is almost due south of the observer, so there's a way to make a simple estimate. The observer is roughly 26.9 deg north of the GP, a little less than 30.46 deg N, and a little east of the GP 72.65 E.

I have a few more things to say if anyone's interested. I'd appreciate a check on my numbers. It's very easy to make a mistake, which is why sight reductions in the pre-GPS era were done by two persons independently who'd compare their results. An unintentional grounding can ruin your whole day.