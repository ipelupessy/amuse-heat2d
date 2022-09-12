from amuse.test.amusetest import TestWithMPI

from .interface import heat2dInterface
from .interface import heat2d

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
