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

First, the ```interface.f90``` looks as follows:
```fortran
module heat2dInterface


contains

  function echo_int(input, output)
      integer :: echo
      integer :: echo_int
      integer ::  input, output
      output = echo(input)
      echo_int = 0
  end function

end module
```
We change this to:
```fortran
module heat2dInterface
  use heatmod

contains

  function commit_parameters() result(ret)
    integer :: ret
    
    call initialize
    ret=0
    
  end function

end module
```
the ```use heatmod``` statement allows us access to the fortran module with our simulation code.
The ```commit_parameters``` (whose naming will be explained below) does nothing more than calling
the existing initialize function, which upon examination of the code, allocates the 
simulation variables. We remove the example ```echo_int``` function.

If we look at the ```interface.py``` function we see that it contains two class definitions,
```Heat2dInterface``` and ```Heat2d```. These define the *low level* and *high level* interfaces of 
our code. For the moment we will concentrate on ```Heat2dInterface```. We see that it contains 
the following definition:
```python
    @legacy_function
    def echo_int():
        function = LegacyFunctionSpecification()  
        function.addParameter('int_in', dtype='int32', direction=function.IN, unit=None)
        function.addParameter('int_out', dtype='int32', direction=function.OUT, unit=None)
        function.result_type = 'int32'
        function.can_handle_array = True
        return function
```
This defines as part of the interface a function ```echo_int``` with one input 
parameter and one output parameter and an integer result type. We can compare with the now
deleted implementation in ```interface.f90```, see above! You can guess that 
we need to replace this with the corresponding definition for ```commit_parameters```:
```python
    @legacy_function
    def commit_parameters():
        function = LegacyFunctionSpecification()  
        function.result_type = 'int32'
        return function
```
or the abbreviated alternative:
```python
    @remote_function    
    def commit_parameters():
        return ()
```

With these changes we can compile again. We want to test our changes (and also 
the tests fails since we have removed a tested function - confirm this!) so
change ```test1``` in test_heat2d.py:
```python
    def test1(self):
        instance = Heat2dInterface(redirection="none")
        error = instance.commit_parameters()
        self.assertEquals(error, 0)
        instance.stop()
```
Confirm that the test works. If you turn on output (```-sv``` pytest flag)
you should see:
```
test_heat2d.py::Heat2dInterfaceTests::test1  initializing model
```
In the output, confirming that the relevant part of the code has indeed been called.



### Completing the low level interface and testing

### The high level interface

#### Data model

#### State model

#### Properties and other loose ends

#### Testing

### Validation

### Applications

### Coupling example
