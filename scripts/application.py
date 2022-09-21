"""
 Here we will show how to use the basic interface we made for the heat equation 
 solver to solve a different problem than the one programmed in the original code.
"""

import numpy

from heat2d.interface import heat2d

from matplotlib import pyplot

from amuse.units import generic_unit_system
from amuse.units import units, constants

def heat_pulse():
    """
    This example solves a simple problem: namely what happens if you dump a specified
    amount of energy in a metal plate
    
    """
    converter=generic_unit_system.generic_to_si(1.| units.K, 1.| units.m, 1.|units.s)
    h=heat2d(converter)

    print("default parameters:")
    print(h.parameters)

    # we are going to model a 1m x 1m steel sheet:

    # more detail on the physical model
    thickness=0.1 | units.cm
    density=8. | units.g/units.cm**3
    heat_capacity=0.466 | units.J/units.K/units.g
    thermal_conductivity=45. | units.W/units.m/units.K
    heat_pulse=1000. | units.J

    cellsize=(1. | units.m) / (h.parameters.Ngrid_x)

    h.parameters.alpha=thermal_conductivity/(density*heat_capacity)
    h.parameters.cellsize=cellsize

    # choose a safe time step:
    h.parameters.timestep=0.1*h.parameters.cellsize**2/h.parameters.alpha

    print("parameters:")
    print(h.parameters)

    print("timestep criterion:", h.parameters.alpha*h.parameters.timestep/h.parameters.cellsize**2)

    h.grid.temperature=293. | units.K

    cell_mass=thickness*h.parameters.cellsize**2*density
    deltaT=heat_pulse/heat_capacity/(4*cell_mass)
    h.grid[49:51,49:51].temperature+=deltaT

    dE=(h.grid.temperature-(293 | units.K)).sum()*heat_capacity*density*thickness*(cellsize**2)
    print("dE before:", dE.in_(units.J))

    
    temp=h.grid.temperature.value_in(units.K)
    vmin=temp.min()
    vmax=temp.max()
    print(vmin,vmax)
    
    f,(ax1,ax2)=pyplot.subplots( 2,1)
    ax1.imshow(temp.T, origin="lower", vmin=vmin, vmax=vmax)
    
    # choose the same number of timesteps as above
    tend=100*h.parameters.timestep
    print(" evolving to: ", tend)
    h.evolve_model(tend)

    temp=h.grid.temperature.value_in(units.K)
    vmin=temp.min()
    vmax=temp.max()
    print(vmin,vmax)
    dE=(h.grid.temperature-(293 | units.K)).sum()*heat_capacity*density*thickness*(cellsize**2)
    print("dE after:", dE.in_(units.J))

    ax2.imshow(temp.T, origin="lower", vmin=vmin, vmax=vmax)

    pyplot.savefig("heat_pulse.png")

    h.stop()

if __name__=="__main__":
    heat_pulse()


