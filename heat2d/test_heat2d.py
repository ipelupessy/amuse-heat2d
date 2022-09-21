from amuse.test.amusetest import TestWithMPI

from .interface import heat2dInterface
from .interface import heat2d

from amuse.units import generic_unit_system

class heat2dInterfaceTests(TestWithMPI):
    
    def test1(self):
        instance = heat2dInterface()
        error = instance.initialize_code()
        self.assertEquals(error, 0)

        error = instance.commit_parameters()
        self.assertEquals(error, 0)

        instance.stop()
    
    def test2(self):
        instance = heat2dInterface()
        error = instance.initialize_code()
        self.assertEquals(error, 0)

        nx=200
        err=instance.set_nx(nx)
        self.assertEquals(err,0)
        _nx, err = instance.get_nx()
        self.assertEquals(nx,_nx)
        self.assertEquals(err,0)
        
        instance.stop()

    def test3(self):
        instance = heat2dInterface()
        error = instance.initialize_code()
        self.assertEquals(error, 0)
        error = instance.commit_parameters()
        self.assertEquals(error, 0)
        error = instance.evolve_model(1)
        self.assertEquals(error, 0)


        instance.stop()

class heat2dTests(TestWithMPI):
    
    def test1(self):
        instance = heat2dInterface()
        instance.stop()

    def test1(self):
        parameters=[ 
          ("alpha", 0.123 | generic_unit_system.length**2/generic_unit_system.time),
          ("Ngrid_x", 321),
          ("Ngrid_y", 123),
          ("cellsize", 321. | generic_unit_system.length),
          ("timestep",  123. | generic_unit_system.time),
        ]

        instance = heat2d()
        
        for param, value in parameters:
            setattr(instance.parameters, param, value)

        for param, value in parameters:
            value2=getattr(instance.parameters, param)
            self.assertAlmostRelativeEqual(value, value2, 7)

        instance.stop()
  
