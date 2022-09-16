## amuse-heat2d example

This repository contains a worked out example of interfacing and coupling a
physics code with AMUSE. Its the basis for a software carpentry lesson
and a workshop at the Netherlands eScience Center.


This README briefly documents the exercise, ie how to get from the "original"
code in ```code``` to the worked out interface in ```heat2d``` and the test 
scripts ```test_validation.py``` and an example coupling application 
```applications.py```.

### Preparations

For this exercise you need to have a Unix-like machine with a developer 
environment such that you can compile code. Linux, MaxOS and the WSL on 
windows should all work.

You should have installed C and Fortran compilers and the amuse-framework, 
usually in seperate virtual environment:

```bash
virtualenv env
source env/bin/activate
pip install numpy docutils mpi4py h5py wheel pytest amuse-framework
```

Starting point of the exercise is the code contained in the directory 
```code```. Verify that you can compile and run this code. This code 
solves the heat equation for a particular problem, and its fairly 
conventional but typical in its setup.

### Generating a stub AMUSE interface

If AMUSE is installed correctly there will be command ```amusifier```
available which is a tool for completing various AMUSE related tasks.
One thing it can do for you is generate a stub interface which will be the 
starting point for our integration of the ```code```.

So in a suitable working directory execute the following command:

```
amusifier --type=f90 --mode=dir Heat2d
```
This will generate a directory ```heat2d``` with a minimal example of an 
AMUSE interfaced code, where the directory and code interface names are all 
derived from the provided ```Heat2d``` name, but ofcourse do not know 
anything about solving the heat equation yet.

If you go into the directory, take a moment to note the generated files.
you should be able to build the code and interface:
```
cd heat2d
make 
```
You can run a basic test with:
```
pytest test_heat2d.py
```

Examine the the output of the build, and the various files. Note you 
go back to the pristine state of the directory with ```make distclean```.



### Integrating the source code and building a minimal low level interface

### Completing the low level interface and testing

### The high level interface

#### Data model

#### State model

#### Properties and other loose ends

#### Testing

### Validation

### Applications

### Coupling example
