# Copyright (C) 2021-2022 by the RBniCSx authors
#
# This file is part of RBniCSx.
#
# SPDX-License-Identifier: LGPL-3.0-or-later
"""RBniCSx main module."""

# Simplify import of mpi4py.MPI, petsc4py.PETSc and slepc4py.SLEPc in internal modules by importing them here
# once and for all. Internal modules will now only need to import the main packages mpi4py, petsc4py and slepc4py.
import mpi4py
import mpi4py.MPI  # noqa: F401
import petsc4py
import petsc4py.PETSc  # noqa: F401
import slepc4py
import slepc4py.SLEPc  # noqa: F401


# We require a very small subset of the numpy typing library, namely NDArray. To avoid enforcing
# a requirement numpy>=1.21.0, we mock numpy.typing.NDArray for older numpy versions.
import types
import typing

import numpy

try:
    import numpy.typing
except ImportError:  # pragma: no cover
    numpy.typing = types.ModuleType("typing", "Mock numpy.typing module")
finally:
    if not hasattr(numpy.typing, "NDArray"):  # pragma: no cover
        numpy.typing.NDArray = typing.Iterable

# Clean up imported names so that they are not visible to end users
del types
del typing

del mpi4py
del numpy
del petsc4py
del slepc4py
