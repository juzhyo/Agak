<div align="center">
  
# Photocurrent Mapper

A spatial photocurrent mapping program

![Agaration Screenshot](https://github.com/juzhyo/agaration/blob/main/screenshots/run.gif)

</div>

---

### Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Instruments](#instruments)
- [Roadmap](#roadmap)

# Introduction
This is an in-house program written to add spatial photocurrent mapping capability 
to our optical setup. The measurement involves controlling a laser's position on a device 
through a galvo mirror system, and reading its current/voltage output. In time, it is hoped 
that it can perform temperature-, wavelength-, and bias-dependent mappings as well. A GUI 
unifies the measurement system and allows monitoring of the orchestra of instruments that 
are working together.

# Features
- Software control of SR830 settings
- Live time trace of SR830 channels
- Spatial photocurrent mapping
- Visual update of mapping progression


# Instruments
+ SR830 DSP lock-in amplifier
+ M Squared SolsTiS
+ Custom galvo mirror system
+ Agilent B2902A sourcemeter
+ Thorlabs PM100D power meter


# Roadmap
The program is very much still a work-in-progress. Hopefully more functions 
will be added soon. Some of the functions that are in consideration are:

+ Live laser positioning control
+ Custom saving directory
+ Wavelength-dependent measurement
+ Live camera capture
+ Bias-dependent mapping with sourcemeter



