from amuse.community import *

from amuse.datamodel import CartesianGrid

class heat2dInterface(CodeInterface):
        
    use_modules=["heat_interface"]
        
    def __init__(self, **keyword_arguments):
        CodeInterface.__init__(self, name_of_the_worker="heat2d_worker", **keyword_arguments)
    
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
    
    @remote_function
    def get_model_time():
        returns (model_time=0. | generic_unit_system.time)
    
    @remote_function
    def get_alpha():
        returns (alpha_coef=1. | generic_unit_system.length**2 /generic_unit_system.time)
    
    @remote_function
    def set_alpha(alpha_coef=1. | generic_unit_system.length**2 /generic_unit_system.time):
        returns ()

    @remote_function
    def get_time_step():
        returns (timestep=1. | generic_unit_system.time)
    
    @remote_function
    def set_time_step(timestep=1.| generic_unit_system.time):
        returns ()

    @remote_function(can_handle_array=True)
    def get_temperature(i=0, j=0):
        returns (temperature=0. | generic_unit_system.temperature) 
    
    @remote_function(can_handle_array=True)
    def set_temperature(i=0, j=0, temperature=0. | generic_unit_system.temperature):
        returns () 

    @remote_function
    def get_grid_cellsize():
        returns (cellsize=1. | generic_unit_system.length)
    
    @remote_function
    def set_grid_cellsize(cellsize=1. | generic_unit_system.length):
        returns ()

    @remote_function
    def get_nx():
        returns (ngridx=0)
    
    @remote_function
    def set_nx(ngridx=0):
        returns ()

    @remote_function
    def get_ny():
        returns (ngridy=0)
    
    @remote_function
    def set_ny(ngridy=0):
        returns ()

class heat2d(InCodeComponentImplementation):

    def __init__(self, unit_converter=None, **options):
        self.unit_converter=unit_converter
        
        InCodeComponentImplementation.__init__(self,  heat2dInterface(**options), **options)

    def get_grid_range(self):
        return 1, self.get_nx(), 1, self.get_ny()
        
    def get_grid_position(self, i, j):
        cellsize=self.get_grid_cellsize()
        return (i*cellsize, j*cellsize)

    def define_state(self, handler):
        handler.set_initial_state('UNINITIALIZED')
        
        handler.add_transition(
            'UNINITIALIZED', 'INITIALIZED', 'initialize_code')
        
        handler.add_method('INITIALIZED', 'before_get_parameter')
        handler.add_method('INITIALIZED', 'before_set_parameter')

        handler.add_method('RUN', 'before_get_parameter')
        
        handler.add_transition('INITIALIZED', 'RUN', "commit_parameters")
        handler.add_method('RUN', 'evolve_model')
        
        handler.add_transition('!UNINITIALIZED!STOPPED', 'END', 'cleanup_code')

        handler.add_transition('END', 'STOPPED', 'stop', False)
        handler.add_method('STOPPED', 'stop')
 
        # this is needed because temperature needs to be allocated
        handler.add_method("RUN", "get_temperature")
        handler.add_method("RUN", "set_temperature")


    def define_properties(self, handler):
        handler.add_property('get_model_time', public_name="model_time")

    def define_parameters(self, handler):
        handler.add_method_parameter(
            "get_alpha",
            "set_alpha",
            "alpha",
            "thermal diffusivity", 
            default_value = 0.01 | generic_unit_system.length**2 /generic_unit_system.time
        )

        handler.add_method_parameter(
            "get_nx",
            "set_nx",
            "Ngrid_x",
            "grid size x direction", 
            default_value = 100
        )

        handler.add_method_parameter(
            "get_ny",
            "set_ny",
            "Ngrid_y",
            "grid size y direction", 
            default_value = 100
        )

        handler.add_method_parameter(
            "get_grid_cellsize",
            "set_grid_cellsize",
            "cellsize",
            "grid cell size (uniform)", 
            default_value = 0.1 | generic_unit_system.length
        )

        handler.add_method_parameter(
            "get_time_step",
            "set_time_step",
            "timestep",
            "timestep used by the code", 
            default_value = 0.01 | generic_unit_system.time
        )


    def define_grids(self, handler):
        handler.define_grid('grid',axes_names = ["x", "y"], grid_class=CartesianGrid)
        handler.set_grid_range('grid', 'get_grid_range')
        handler.add_getter('grid', 'get_grid_position', names=["x", "y"])
        handler.add_getter('grid', 'get_temperature', names=["temperature"])
        handler.add_setter('grid', 'set_temperature', names=["temperature"])
        
        
    def define_converter(self, handler):
        if self.unit_converter is not None:
            handler.set_converter(
                self.unit_converter.as_converter_from_si_to_generic()
            )
      
