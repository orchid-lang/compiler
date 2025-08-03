# Orchid compiler

The orchid compiler is currently in it's first stage.

## Structure

The way the Orchid compiler is structured changes with the stages. However it will usually always be a bunch of Orchid files, including `main.orh` abd `stdlib.orh`. The standard library will mostly be written in C in `orchidlibstd.c`. The way functions are called from the standard library in C is using the standard library wrapper `stdlib.orh` which will be imported by default into every Orchid file that gets compiled (except itself of course). The way that `stdlib.orh` calls functions is through `_callSharedLib`. `_callSharedLib` takes 3 arguements; `(string: library, string: function, any[]: args)`. The standard library that is written in C is available as the library `orchidstd`. Keep in mind that in order to use functions written in C, they must be prefixed with an underscore. For example: `void stdprint(const char* str) { ... }` in C, gets called in Orchid using `_callSharedLib("orchidstd", "_stdprint", [str])`

## Building instructions

### Requirements

- Python installed to your machine, specifically the `python3` command.
- An installation of `nasm`
- An installation of `gcc`


### Instructions

Step one is always to clone the project.

In the current stage, in order to build the project you will have to run `python3 ./comp.py`. `comp.py` takes 2 optional arguements; `comp.py \<path\> \<first_file_flag\>`. If the path is set, the compiler will compile that Orchid file, if not it will compile `./compiler/main.orh` by default. If the `first_file_flag` is set at all, the compiler will consider it a chained file and will not execute a lot of the building commands.

## Stages?

The orchid compiler project progress in 'stages'. Right now we are working on the first stage.

Down below are listed each of the stages and what they mean.

## Stages!

### Stage 1

In this stage Orchid code gets compiled to assembly and then to an executable with one really big python script.

### Stage 2

At this point, the python script should be able to compile the most basic of basic versions of Orchid. At that point we will rewrite the compiler in Orchid itself.

### Stage 3

At this final stage, the Orchid compiler will have all the core functionality. Most commits will either target small fixes or the standard library.

## License

Licensing information may be found in [`LICENSE`](LICENSE)
