CC=g++
CFLAGS=-std=c++11 -O3 -Wall

CFILES = main.cpp feature_computer.cpp spectra.cpp
OBJS := $(addsuffix .o,$(basename $(CFILES)))
RM=rm -f

main: $(OBJS)
	$(CC) $(CFLAGS) -I external_code/ -o feature-extractor $(OBJS)

%.o: %.cpp
	$(CC) $(CFLAGS) -c -I external_code/ $<

clean:
	$(RM) $(OBJS)
