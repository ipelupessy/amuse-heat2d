! An example of the heat equation.
module heatmod

  implicit none

  real :: dt=0.01
  real :: tnow=0.
  real :: tend=10.

  real :: alpha=0.1

  integer :: nx=100
  integer :: ny=100

  real :: dx=0.1

  real, allocatable :: T(:,:),dT_dt(:,:)

contains

  ! Initializes the model with default hardcoded values.
  subroutine initialize

    print*,"initializing model"

    allocate(T(nx,ny))
    allocate(dT_dt(nx,ny))
    
    T=0.
    dT_dt=0.

    T(40:60,20:80)=1

  end subroutine initialize

  ! implements insulating boundary
  subroutine set_boundary

    T(1,:)=T(2,:)
    T(nx,:)=T(nx-1,:)
    T(:,1)=T(:,2)
    T(:,ny)=T(:,ny-1)

  end subroutine set_boundary

  ! finite difference formula for the heat equation
  subroutine calc_dT_dt

  dT_dt=0.
  dT_dt(2:nx-1,2:ny-1)=alpha*((T(1:nx-2,2:ny-1)+T(3:nx,2:ny-1)-2*T(2:nx-1,2:ny-1))/dx**2 + &
                               (T(2:nx-1,1:ny-2)+T(2:nx-1,3:ny)-2*T(2:nx-1,2:ny-1))/dx**2 )

  end subroutine calc_DT_dt


  ! Steps the heat model forward in time.
  subroutine step(dt)
    real :: dt

    call calc_dT_dt

    T=T+dt*dT_dt
    call set_boundary
    tnow=tnow+dt

  end subroutine step

  ! The solver for the two-dimensional heat equation.
  subroutine run

    print*,"start run"

    do while(tnow<tend-dt/2)
      call step(min(dt,tend-tnow))
    end do

    print*,"done"

  end subroutine

end module heatmod
