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

Our first goal will be to integrate the heat equation solver ```code``` into
the build system of our stub interface. The steps to take, which are explained
in more detail below, are the following:
  1. copy the source files to the ```src``` directory. 
  2. adapt the Makefile in the ```src``` directory to build and link the 
     ```code``` source.
  3. add some simple interface functions to verify that we can start up the 
     code, veryfing that the build was succesful. 

In our case the source code is very simple, and we just copy over the files
from the ```code``` directory to the ```src``` directory. 
This will also overwrite the ```Makefile``` in the
```src``` directory - however we want to retain the building of the library,  
so make a backup copy of the ```Makefile```, e.g. renaming it ```Makefile.amuse```:
```bash
cd heat2d
cd src
cp Makefile Makefile.amuse
cp /path/to/the/code/* ./
```

At this point we want to merge the two makefiles in ```src```, in a way that 
retains the build instructions in the ```Makefile``` for the original code 
and generates a code library as in ```Makefile.amuse```. If we inspect the 
two makefiles we see that they in fact are very similar and we can just add 
the build instructions for ```heat_mod.o``` to the ```Makefile.amuse```
by changing the line
```
CODEOBJS = test.o
```
to
```
CODEOBJS = test.o heat_mod.o
```
and copying ```Makefile.amuse``` back to ```Makefile```:
```
cp Makefile.amuse Makefile
rm Makefile.amuse
```

Note that this is a bit of a coincedence, in practice one should be careful 
in this step.

We can again verify the interface builds:
```
cd ..
make distclean
make
```

Somewhere in the output will be confirmation that our code is part of the now 
appropiately named ```libheat2d.a```:
```
ar: creating libheat2d.a
a - test.o
a - heat_mod.o
```

However, we have not exposed any of the functionality of ```code``` in our interface.
This is done in the ```interface.f90``` and ```interface.py``` in the root of our 
stub package.


### Completing the low level interface and testing

### The high level interface

#### Data model

#### State model

#### Properties and other loose ends

#### Testing

### Validation

### Applications

### Coupling example
