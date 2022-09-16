FC=gfortran


all: heat


heat: heat_mod.o heat_main.o
	${FC} $^ -o $@


%.o: %.f90
	${FC} -c  -o $@ $<

clean:
	rm heat *.o *.mod

distclean: clean
