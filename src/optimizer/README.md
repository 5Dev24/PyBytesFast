## Precondition

PyBytesFast assumes there isn't any introspection/reflections done on
the code being optimized else it cannot fully determine the full usage
of variables and methods and thus wouldn't be able to increase runtime
as well.

## Goal

The goal of this project would be to be able to pass the source code
to this project into it and get an optimized version out.