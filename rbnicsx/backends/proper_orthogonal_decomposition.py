# Copyright (C) 2021-2022 by the RBniCSx authors
#
# This file is part of RBniCSx.
#
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Backend to compute the proper orthogonal decomposition of dolfinx objects."""

import functools
import typing

import dolfinx.fem
import numpy as np
import petsc4py
import ufl

from rbnicsx._backends.proper_orthogonal_decomposition import (
    proper_orthogonal_decomposition_functions as proper_orthogonal_decomposition_functions_super,
    proper_orthogonal_decomposition_functions_block as proper_orthogonal_decomposition_functions_block_super,
    proper_orthogonal_decomposition_tensors as proper_orthogonal_decomposition_tensors_super)
from rbnicsx.backends.functions_list import FunctionsList
from rbnicsx.backends.projection import bilinear_form_action
from rbnicsx.backends.tensors_list import TensorsList


@functools.singledispatch
def proper_orthogonal_decomposition(
    snapshots: typing.Iterable, N: int, tol: float, normalize: bool = True
) -> typing.Tuple[
    np.typing.NDArray[float], typing.Iterable, typing.List[petsc4py.PETSc.Vec]
]:
    """
    Compute the proper orthogonal decomposition of a set of snapshots or tensors.

    Please the dispatched implementation for more details.
    """
    raise RuntimeError("Please run the dispatched implementation.")


@proper_orthogonal_decomposition.register
def _(
    functions_list: FunctionsList, inner_product: ufl.Form, N: int, tol: float, normalize: bool = True
) -> typing.Tuple[
    np.typing.NDArray[float], FunctionsList, typing.List[petsc4py.PETSc.Vec]
]:
    """
    Compute the proper orthogonal decomposition of a set of snapshots.

    Parameters
    ----------
    functions_list : rbnicsx.backends.FunctionsList
        Collected snapshots.
    inner_product : ufl.Form
        Bilinear form which defines the inner product. The resulting modes will be orthonormal
        w.r.t. this inner product.
    N : int
        Maximum number of modes to be computed.
    tol : float
        Tolerance on the retained energy.
    normalize : bool, optional
        If true (default), the modes are scaled to unit norm.

    Returns
    -------
    np.typing.NDArray[float]
        Eigenvalues of the correlation matrix, largest first. All computed eigenvalues are returned.
    rbnicsx.backends.FunctionsList
        Retained modes from the snapshots. Only the first few modes are returned, till either the
        maximum number N is reached or the tolerance on the retained energy is fulfilled.
    typing.List[petsc4py.PETSc.Vec]
        Eigenvectors of the correlation matrix. Only the first few eigenvectors are returned, till
        either the maximum number N is reached or the tolerance on the retained energy is fulfilled.
    """
    compute_inner_product = bilinear_form_action(inner_product)

    return proper_orthogonal_decomposition_functions_super(
        functions_list, compute_inner_product, _scale_function, N, tol, normalize)


def proper_orthogonal_decomposition_block(
    functions_lists: FunctionsList, inner_products: typing.List[ufl.Form], N: typing.Union[int, typing.List[int]],
    tol: typing.Union[float, typing.List[float]], normalize: bool = True
) -> typing.Tuple[
    typing.List[np.typing.NDArray[float]], typing.List[FunctionsList], typing.List[typing.List[petsc4py.PETSc.Vec]]
]:
    """
    Compute the proper orthogonal decomposition of a set of snapshots, where each snapshot is made of several blocks.

    Parameters
    ----------
    functions_lists : typing.List[rbnicsx.backends.FunctionsList]
        Collected snapshots. Each snapshot is made of several blocks, defined on possibly different function spaces.
        The inner FunctionsList contains all snapshots of a single block, while the outer list collects the different
        blocks.
    inner_products : typing.List[ufl.Form]
        Bilinear forms which define the inner products of each block. The resulting modes
        will be orthonormal w.r.t. these inner products.
    N : typing.Union[int, typing.List[int]]
        Maximum number of modes to be computed. If an integer value is passed then the same maximum number is
        used for each block. To set a different maximum number of modes for each block pass a list of integers.
    tol : float
        Tolerance on the retained energy. If a floating point value is passed then the same tolerance is
        used for each block. To set a different tolerance for each block pass a list of floating point numbers.
    normalize : bool, optional
        If true (default), the modes are scaled to unit norm.

    Returns
    -------
    typing.List[np.typing.NDArray[float]]
        Eigenvalues of the correlation matrix, largest first. All computed eigenvalues are returned.
        The outer list collects the eigenvalues of different blocks.
    typing.List[rbnicsx.backends.FunctionsList]
        Retained modes from the snapshots. Only the first few modes are returned, till either the
        maximum number N is reached or the tolerance on the retained energy is fulfilled.
        The outer list collects the retained modes of different blocks.
    typing.List[typing.List[petsc4py.PETSc.Vec]]
        Eigenvectors of the correlation matrix. Only the first few eigenvectors are returned, till
        either the maximum number N is reached or the tolerance on the retained energy is fulfilled.
        The outer list collects the eigenvectors of different blocks.
    """
    compute_inner_products = [bilinear_form_action(inner_product) for inner_product in inner_products]

    return proper_orthogonal_decomposition_functions_block_super(
        functions_lists, compute_inner_products, _scale_function, N, tol, normalize)


@proper_orthogonal_decomposition.register
def _(
    tensors_list: TensorsList, N: int, tol: float, normalize: bool = True
) -> typing.Tuple[
    np.typing.NDArray[float], TensorsList, typing.List[petsc4py.PETSc.Vec]
]:
    """
    Compute the proper orthogonal decomposition of a set of tensors.

    Parameters
    ----------
    tensors_list : rbnicsx.backends.TensorsList
        Collected tensors.
    N : int
        Maximum number of modes to be computed.
    tol : float
        Tolerance on the retained energy.
    normalize : bool, optional
        If true (default), the modes are scaled to unit norm.

    Returns
    -------
    np.typing.NDArray[float]
        Eigenvalues of the correlation matrix, largest first. All computed eigenvalues are returned.
    rbnicsx.backends.TensorsList
        Retained modes from the tensors. Only the first few modes are returned, till either the
        maximum number N is reached or the tolerance on the retained energy is fulfilled.
    typing.List[petsc4py.PETSc.Vec]
        Eigenvectors of the correlation matrix. Only the first few eigenvectors are returned, till
        either the maximum number N is reached or the tolerance on the retained energy is fulfilled.
    """
    return proper_orthogonal_decomposition_tensors_super(tensors_list, N, tol, normalize)


def _scale_function(function: dolfinx.fem.Function, factor: float) -> None:
    """Scale a dolfinx Function."""
    with function.vector.localForm() as function_local:
        function_local *= factor
