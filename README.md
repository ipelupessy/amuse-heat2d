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

If you are using OpenMPI, its necessary to enable oversubscription of 
the compute nodes by setting the following environemnt variable:
```
export OMPI_MCA_rmaps_base_oversubscribe=true
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

Now we have confirmed the build system and the base functionality of the code 
it is time to expose all variables, parameters and methods we want to be 
able to access through the interface.

#### Parameters

In order to change the behaviour of the simulation we want to retrieve and set the 
parameters, which are: the timestep ```dt```, the heat coefficient ```alpha``` and
the grid size parameters ```nx```, ```ny``` and grid cellsize ```dx```. 

This is implemented as simple getters and setters, e.g.:
```fortran
  function get_alpha(alpha_coef)
    implicit none
    double precision :: alpha_coef
    integer :: get_alpha
    alpha_coef=alpha
    get_alpha=0
  end function
  
  function set_alpha(alpha_coef)
    implicit none
    double precision :: alpha_coef
    integer :: set_alpha
    alpha=alpha_coef
    set_alpha=0
  end function
```
with matching:
```python
    @remote_function
    def get_alpha():
        returns (alpha_coef=1.)

    @remote_function
    def set_alpha(alpha_coef=1.):
        returns ()
```

Add these functions and write a small test confirming that this works.

Its a bit too tedious to repeat the other functions here, 
but you can see how you can expose all parameters like this.

Question: can understand why the ```commit_parameters``` is 
called thus? (if you call a change of say the parameter ```nx``` is 
it still carried through in the simulation after this?)

#### Variables

The variable declarion section of the fortran module in ```heat_mod.f90``` has 
two variables we want to be able to read: the model time ```tnow``` and the 
array with temperatures ```T```.

For the model time we again implement it as a simple getter. For the array variable 
we need to also specify the array index which we want to retrieve:
```fortran
  function get_temperature(i, j, temperature)
    implicit none
    integer :: i, j
    double precision :: temperature
    integer :: get_temperature
    temperature=T(i,j)
    get_temperature=0
  end function
```
and corresponding ```set_temperature```. In the python definition
```python
    @remote_function(can_handle_array=True)
    def get_temperature(i=0, j=0):
        returns (temperature=0.) 
```
we see a new element: the decorator keyword ```can_handle_array``` specifies
that the python interface function shall also accept arrays and optimizes the
transport of those.

#### Simulations method

By inspecting the file ```heat_mod.90``` of the original
code we see that we want to expose the ```initialize``` and ```step``` functions
to be able to run a simulation. In addition to this it may be a good idea to add
a function ```cleanup``` to cleanup memory after the simulations has finished .

The convention in AMUSE is that each code has a method ```evolve_model(tend)``` which 
advances the model to a ```tend```, so this can be easily implemented using a 
call to the ```step``` function. So the following set of interface functions
in ```interface.f90``` are used for simulation management

```fortran
  function initialize_code()
    implicit none
    integer :: initialize_code
! nothing to be done
    initialize_code=0
  end function
  
  function commit_parameters()
    implicit none
    integer :: commit_parameters
! initialize here
    call initialize
    commit_parameters=0
    if(.not.allocated(T)) commit_parameters=-1
  end function
  
  function cleanup_code()
    implicit none
    integer :: cleanup_code
    if(allocated(T)) deallocate(T)
    if(allocated(dT_dt)) deallocate(dT_dt)
    cleanup_code=0
  end function
  
  function evolve_model(tend)
    implicit none
    double precision :: tend
    integer :: evolve_model
    
    do while(tnow<tend-dt/2)
      call step(min(dt, real(tend-tnow) ))
    end do    
    
    evolve_model=0
  end function
```
Note, the ```initialize_code``` function does not do anything here - normally it
would be a good place to initialize the codes parallel library or logging. Its 
convention any interface should have this method.

What would be the corresponding python prototype definitions? Answer:

```python
    @remote_function
    def initialize_code():
        returns ()

    @remote_function    
    def commit_parameters():
        return ()
    
    @remote_function
    def cleanup_code():
        returns ()

    @remote_function
    def evolve_model(tend=0.| generic_unit_system.time):
        returns ()
```


#### units

Now when we compare the above low level python interface definitions
(and any you have added on you own) with the actual implementation, we 
see another element added to the function in put and out parameters:
```python
    @remote_function
    def get_alpha():
        returns (alpha_coef=1. | generic_unit_system.length**2 /generic_unit_system.time)
```
For each of the function inputs, a unit can be specified. At first this may seems 
strange: what is this ```generic_unit_system.length**2 /generic_unit_system.time```?
The reason for this is that we have recognized that the code does not specify any
units for the positions or cellsizes, nor for the time or temperature. Still its 
possible to identify unit dimensions that are implictly assumed for the input and
output. So in this case the ```alpha``` coefficient is specified to have units
```length**2/time```. We can see later how this information is used by the framework
in case we want to couple to other codes and hence we specify a definite scaling 
to the units.

Note that you can define the units in the low level class ```heat2dInterface```,
but are only visible when using the high level ```heat2d```

Exercise: test this out.

```
>>> from heat2d import interface
>>> h=interface.heat2dInterface()
>>> h.get_alpha()
OrderedDictionary({'alpha_coef':0.10000000149011612, '__result':0})
>>> h.stop()
>>> h=interface.heat2d()
>>> h.get_alpha()
quantity<0.10000000149 length**2 * time**-1>
```

With this it should be clear what is in the ```interface.f90``` and ```heat2dInterface```
class of ```interface.py```. Check that you indeed understand this.

### The high level interface

The units are an example of one of the services AMUSE provides. Others 
are: (1) A data model, (2) management of the code state and (3) defining parameters
and (4) error handling and stopping conditions. These need to be defined in the 
high level interface class ```heat2d```.

#### Data model

The low level interface we build above provides access to the simulation grid,
but hardly any easier than managing the standard fortran arrays. During initialization
of the high level interface a method, ```define_grid``` is called which allows one to
define a data structure to handle this. (A stub is part of the parent class 
InCodeComponentImplementation)

```python
    def define_grids(self, handler):
        handler.define_grid('grid',axes_names = ["x", "y"], grid_class=CartesianGrid)
        handler.set_grid_range('grid', 'get_grid_range')
        handler.add_getter('grid', 'get_grid_position', names=["x", "y"])
        handler.add_getter('grid', 'get_temperature', names=["temperature"])
        handler.add_setter('grid', 'set_temperature', names=["temperature"])
```
Try to see if you can figure out what each of the lines do. Answer:
 1 ```define_grid``` defines a grid attribute ```grid```, sets its class and defines
   the axes names.
 2 ```set_grid_range``` defines the method used to get the range of the grid
 3 ```add_getter``` adds attributes to the grid and defines the getter function used.
   This is done for the grid position attributes ```x``` and ```y``` as well as the variable 
   ```temperature```.
 4 The ```temperature``` should also be possible to set and this line defines the setter.
 

This needs two additional helper methods:
```python
    def get_grid_range(self):
        return 1, self.get_nx(), 1, self.get_ny()
        
    def get_grid_position(self, i, j):
        cellsize=self.get_grid_cellsize()
        return (i*cellsize, j*cellsize)
```
These where not part of the low level interface.

#### State model

If you look at the code there are certain preconditions before the different
methods in the interface can be called, e.g. before the ```evolve_model```
the code needs to be initialized (otherwise unallocated memory is accessed) or
the grid size can be set, but only before initialization.

It would be very tedious if the user of the code would need to remember or 
lookup the exact calling sequence required, hence we capture this information in
the interface and manage the state of the code, using a state model.

The definition of the state model is slightly verbose:

```python
    def define_state(self, handler):
        handler.set_initial_state('UNINITIALIZED')
        
        handler.add_transition(
            'UNINITIALIZED', 'INITIALIZED', 'initialize_code')
        
        handler.add_method('INITIALIZED', 'before_get_parameter')
        handler.add_method('INITIALIZED', 'before_set_parameter')

        handler.add_transition('INITIALIZED', 'RUN', "commit_parameters")

        handler.add_method('RUN', 'before_get_parameter')
        handler.add_method("RUN", "get_temperature")
        handler.add_method("RUN", "set_temperature")
        handler.add_method('RUN', 'evolve_model')
        
        handler.add_transition('RUN', 'END', 'cleanup_code')

        handler.add_transition('END', 'STOPPED', 'stop', False)
        handler.add_method('STOPPED', 'stop')
 ```

Most of the methods used in constructing the state model are more or less 
self-explanatory. The ```set_initial_state``` method names the initial state.
The ```add_transition``` adds a transition between its first argument and second
argument triggered by the name of the method in the third argument. If the 
(string) state names do not exist it is created (same is true for the state
argument in ```add_method```. A fourth optional boolean argument to add_transition
indicates whether the call can be automatically triggered by the state model to 
effect the transition (```True``` by default). By default the interface method 
can always be called. The ```add_method``` method makes the method named in the 
second argument only calleable in the state (first arguemnt). Methods can be 
calleable in multiple states.

#### Properties and parameters

You can define shorthands for certain variables, e.g. the model time is
available as property on the class:

```python
    def define_properties(self, handler):
        handler.add_property('get_model_time', public_name="model_time")
```

The code parameters can be gathered in a dict like attribute ```parameters```
by defining the parameters of the code:

```python
    def define_parameters(self, handler):

        handler.add_method_parameter(
            "get_alpha",
            "set_alpha",
            "alpha",
            "thermal diffusivity", 
            default_value = 0.01 | generic_unit_system.length**2 /generic_unit_system.time
        )
```
So you provide the getter, setter and a name for the parameters as well as a short description
and a default value.

#### Other loose ends

If a code is using scaleless units internally and you would like to be able to 
assign the computation a definite scale, one needs to change the ```__init__``` and
add the following ```define_converter``` function. 

```python
    def __init__(self, unit_converter=None, **options):
        self.unit_converter=unit_converter
        
        InCodeComponentImplementation.__init__(self,  heat2dInterface(**options), **options)

    def define_converter(self, handler):
        if self.unit_converter is not None:
            handler.set_converter(
                self.unit_converter.as_converter_from_si_to_generic()
            )
```

Try out the following:
```
>>> from heat2d import interface
>>> from amuse.units import units, generic_unit_system
>>> conv=generic_unit_system.generic_to_si(1| units.K, 1.|units.m, 1.|units.s)
>>> h=interface.heat2d(conv)
>>> print(h.parameter.alpha)
0.10000000149 m**2 * s**-1
```

### Testing


### Validation

### Applications

### Coupling example
