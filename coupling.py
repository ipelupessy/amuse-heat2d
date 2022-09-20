"""
 Here we will show how to use the basic interface we made for the heat equation 
 solver to solve a problem a coupled problem. For this we will couple a simple model 
 for radiative emission of radiation and heating by a candle to the heat equation solver.
"""

import numpy

from heat2d.interface import heat2dInterface,heat2d

from matplotlib import pyplot

from amuse.units import generic_unit_system
from amuse.units import units, constants

class BlackBodyEmitterWithHeating:
    def __init__(self, grid, dt, density,heat_capacity, thickness, Tenvironment, heat_power):
        self.grid=grid
        self.density=density
        self.heat_capacity=heat_capacity
        self.thickness=thickness
        self.Tenvironment=Tenvironment
        self.heat_power=heat_power
        self.cellsize=self.grid.cellsize()[0] 
        
        self.dt=dt
        self.model_time=0. | units.s
  
    # emission of radiation by blackbody radiation
    def emission(self):
            return constants.Stefan_hyphen_Boltzmann_constant*self.cellsize**2*(self.grid.temperature**4-self.Tenvironment**4)

    def total_emission(self):
            return self.emission().sum()

    def evolve_model(self, tend):
        while self.model_time<tend-self.dt/2:
            cell_mass=self.density*self.thickness*(self.cellsize**2)
            self.grid.temperature=self.grid.temperature-self.dt*self.emission()/(self.heat_capacity*cell_mass)
            
            heating=self.dt*self.heat_power/self.heat_capacity/(4*cell_mass)

            self.grid[49:51,49:51].temperature+=heating

            self.model_time+=self.dt

def candle_under_a_copper_plate():
    """
      Here we will show a simple coupled model of a copper sheet heated by a candle and
      emitting its heat. We will develop it as an example of coupling between the 
      heat equation code and a (python based) implementation of simple radiative model.
    
    
    """
    converter=generic_unit_system.generic_to_si(1.| units.K, 1.| units.m, 1.|units.s)


    # parameters of the physical model
    thickness=0.1 | units.cm
    density=8.92 | units.g/units.cm**3
    heat_capacity=0.38 | units.J/units.K/units.g
    thermal_conductivity=401. | units.W/units.m/units.K
    Tenvironment=293 | units.K
    # this is the heating power of a candle:
    heating_power=80. | units.W

    h=heat2d(converter)

    cellsize=(1. | units.m) / (h.parameters.Ngrid_x)

    h.parameters.alpha=thermal_conductivity/(density*heat_capacity)
    h.parameters.cellsize=cellsize

    # choose a safe time step:
    timestep=0.25*h.parameters.cellsize**2/h.parameters.alpha
    h.parameters.timestep=timestep/2

    # initial condition
    h.grid.temperature=293. | units.K
    
    # some reasonable number of timesteps
    tend=0.25 | units.hour
    print(" evolving to: ", tend)

    b=BlackBodyEmitterWithHeating(h.grid.copy(), timestep/2, density, heat_capacity, thickness, 
                                    Tenvironment, heating_power)

    channel1=b.grid.new_channel_to(h.grid)
    channel2=h.grid.new_channel_to(b.grid)

    tnow=0. | units.s
    while tnow<tend-timestep/2:
        b.evolve_model(tnow+timestep/2)
        channel1.copy_attributes(["temperature"])
        h.evolve_model(tnow+timestep)
        channel2.copy_attributes(["temperature"])
        b.evolve_model(tnow+timestep)
        channel1.copy_attributes(["temperature"])
        tnow+=timestep

        print(tnow, h.grid.temperature.max(), h.grid.temperature.mean(), b.total_emission().in_(units.W))

    f,ax1=pyplot.subplots( 1,1)

    temp=h.grid.temperature.value_in(units.K)
    vmin=temp.min()
    vmax=temp.max()

    im=ax1.imshow(temp.T, origin="lower", vmin=vmin, vmax=vmax, extent=[-0.5,0.5,-0.5,0.5])
    
    ax1.set_xlabel("x (m)")
    ax1.set_xlabel("y (m)")
    
    f.colorbar(im,label="Temperature (K)")
    
    pyplot.savefig("candle.png")

    h.stop()
    
    
if __name__=="__main__":
    candle_under_a_copper_plate()


