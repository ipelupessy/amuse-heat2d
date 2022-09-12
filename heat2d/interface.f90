module heat_interface
  use heatmod

contains
  
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
    
  function get_model_time(model_time)
    implicit none
    double precision :: model_time
    integer :: get_model_time
    model_time=tnow
    get_model_time=0
  end function
  
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
  
  function get_time_step(timestep)
    implicit none
    double precision :: timestep
    integer :: get_time_step
    timestep=dt
    get_time_step=0
  end function
  
  function set_time_step(timestep)
    implicit none
    double precision :: timestep
    integer :: set_time_step
    dt=timestep
    set_time_step=0
  end function
  
  function get_temperature(i, j, temperature)
    implicit none
    integer :: i, j
    double precision :: temperature
    integer :: get_temperature
    temperature=T(i,j)
    get_temperature=0
  end function
  
  function set_temperature(i, j, temperature)
    implicit none
    integer :: i, j
    double precision :: temperature
    integer :: set_temperature
    T(i,j)=temperature
    set_temperature=0
  end function
  
  function get_grid_cellsize(cellsize)
    implicit none
    double precision :: cellsize
    integer :: get_grid_cellsize
    cellsize=dx
    get_grid_cellsize=0
  end function
  
  function set_grid_cellsize(cellsize)
    implicit none
    double precision :: cellsize
    integer :: set_grid_cellsize
    dx=cellsize
    set_grid_cellsize=0
  end function
  
  function get_nx(ngridx)
    implicit none
    integer :: ngridx
    integer :: get_nx
    ngridx=nx
    get_nx=0
  end function
  
  function set_nx(ngridx)
    implicit none
    integer :: ngridx
    integer :: set_nx
    nx=ngridx
    set_nx=0
  end function
  
  function get_ny(ngridy)
    implicit none
    integer :: ngridy
    integer :: get_ny
    ngridy=ny
    get_ny=0
  end function
  
  function set_ny(ngridy)
    implicit none
    integer :: ngridy
    integer :: set_ny
    ny=ngridy
    set_ny=0
  end function

end module heat_interface


