"""
  This validation script tests the capability of the interface to replicate a standalone run.

  - it prints the parameters
  - plots the initial state
  - evolves for a set amount of time
  - plots the final state

"""

import numpy

from heat2d.interface import heat2dInterface,heat2d

from matplotlib import pyplot

from amuse.units import generic_unit_system
from amuse.units import units

def low_level_comparison_run():
    h=heat2dInterface()
    
    h.initialize_code()
    
    alpha,err=h.get_alpha()
    timestep,err=h.get_time_step()
    cellsize,err=h.get_grid_cellsize()
    nx,err=h.get_nx()
    ny,err=h.get_ny()

    print("timestep criterion:", alpha*timestep/cellsize**2)

    print("plot the initial state")

    ix,iy=numpy.meshgrid(numpy.arange(1,nx+1),numpy.arange(1,ny+1))
    
    
    h.commit_parameters()
     
    temp,err=h.get_temperature(ix.flat,iy.flat)
    temp=temp.reshape((nx,ny))
    
    print(temp.shape)
    
    
    f,(ax1,ax2)=pyplot.subplots( 2,1)
    ax1.imshow(temp, origin="lower", vmin=0, vmax=1)
    
    h.evolve_model(1.)

    temp,err=h.get_temperature(ix.flat,iy.flat)
    temp=temp.reshape((nx,ny))

    ax2.imshow(temp, origin="lower", vmin=0, vmax=1)

    pyplot.savefig("temperature.png")

    h.cleanup_code()

    h.stop()


def high_level_comparison_run():
    h=heat2d()
    
    print("parameters:")
    print(h.parameters)

    print("timestep criterion:", h.parameters.alpha*h.parameters.timestep/h.parameters.cellsize**2)

    print("plot the initial state")
    
    temp=h.grid.temperature
    
    f,(ax1,ax2)=pyplot.subplots( 2,1)
    ax1.imshow(temp.number.T, origin="lower", vmin=0, vmax=1)
    
    h.evolve_model(1. | generic_unit_system.time)

    temp=h.grid.temperature

    ax2.imshow(temp.number.T, origin="lower", vmin=0, vmax=1)

    pyplot.savefig("temperature.png")

    h.stop()

def physical_units_comparison_run():
    converter=generic_unit_system.generic_to_si(1.| units.K, 1.| units.m, 1.|units.s)
    h=heat2d(converter)

    print("default parameters:")
    print(h.parameters)

    # we are going to model a 1m x 1m steel sheet:
    h.parameters.alpha=12. | units.milli(units.m)**2/units.s
    h.parameters.cellsize=(1. | units.m) / (h.parameters.Ngrid_x)

    # choose a safe time step:
    h.parameters.timestep=0.1*h.parameters.cellsize**2/h.parameters.alpha

    print("actual parameters:")
    print(h.parameters)

    print("timestep criterion:", h.parameters.alpha*h.parameters.timestep/h.parameters.cellsize**2)

    temp=h.grid.temperature
    
    f,(ax1,ax2)=pyplot.subplots( 2,1)
    ax1.imshow(temp.value_in(units.K).T, origin="lower", vmin=0, vmax=1)
    
    # choose the sme number of timesteps as above
    tend=100*h.parameters.timestep
    print(" evolving to: ", tend)
    h.evolve_model(tend)

    temp=h.grid.temperature

    ax2.imshow(temp.value_in(units.K).T, origin="lower", vmin=0, vmax=1)

    pyplot.savefig("temperature.png")


    h.stop()


if __name__=="__main__":
    physical_units_comparison_run()


