import sys
import os
import inspect
import pprint as pp
import numpy as np
import pytest
from collections.abc import Iterable
from pymoc.column import Column

@pytest.fixture(scope="module", params=[
  { 'Area': 6e13, 'z': np.asarray(np.linspace(-4000, 0, 80)), 'kappa': 2e-5 },
  { 'Area': None, 'z': np.asarray(np.linspace(-4000, 0, 80)), 'kappa': 2e-5 },
  { 'Area': 6e13, 'z': None, 'kappa': 2e-5 },
  { 'Area': 6e13, 'z': 50, 'kappa': 2e-5 },
  { 'Area': 6e13, 'z': np.array([]), 'kappa': 2e-5 },
  { 'Area': 6e13, 'z': np.asarray(np.linspace(-4000, 0, 80)), 'kappa': None },
  { 'Area': 6e13, 'z': np.asarray(np.linspace(-4000, 0, 80)), 'kappa': 2e-5, 'bs': 0.05, 'bbot': 0.02, 'bzbot': 0.01, 'b': 0.03, 'N2min': 2e-7 },
  { 'Area': 6e13, 'z': np.asarray(np.linspace(-4000, 0, 80)), 'kappa': 2e-5, 'b': np.arange(0.0, 8.0, 0.1) },
])

def column_config(request):
  return request.param

class TestColumn(object):
  def test_column_init(self, column_config):
    if not column_config['Area']:
      with pytest.raises(TypeError) as areainfo:
        Column(**column_config)
      assert(str(areainfo.value) == "('Area', 'needs to be either function, numpy array, or float')")
      return

    if not column_config['kappa']:
      with pytest.raises(TypeError) as kappainfo:
        Column(**column_config)
      assert(str(kappainfo.value) == "('kappa', 'needs to be either function, numpy array, or float')")
      return

    if not isinstance(column_config['z'], np.ndarray) or not len(column_config['z']):
      with pytest.raises(TypeError) as zinfo:
        Column(**column_config)
      assert(str(zinfo.value) == "z needs to be numpy array providing grid levels")
      return

    column = Column(**column_config)

    # The constructor assigns all expected properties
    assert hasattr(column, 'z')
    assert hasattr(column, 'kappa')
    assert hasattr(column, 'Area')
    assert hasattr(column, 'b')
    assert hasattr(column, 'bs')
    assert hasattr(column, 'bbot')
    assert hasattr(column, 'bzbot')
    assert hasattr(column, 'N2min')

    column_signature = inspect.signature(Column)

    # The constructor initializes all scalar properties
    # Uses explicit property if present, or the default
    for k in ['bs', 'bbot', 'bzbot', 'N2min']:
      assert getattr(column, k)  == (column_config[k] if k in column_config and column_config[k] else column_signature.parameters[k].default)

    # The constructor initializes all vector properties
    # Uses explicit property if present, or the default
    assert all(column.z == column_config['z'])
    assert all(column.b  == column.make_array(column_config['b'] if 'b' in column_config and not column_config['b'] is None else column_signature.parameters['b'].default, 'b'))

    # The constructor initializes all z-dependent callable properties
    # Uses explicit property if present, or the default
    for k in ['Area', 'kappa']:
      f = getattr(column, k)
      ft = column.make_func(column_config[k], k)
      for z in column.z:
        assert f(z) == ft(z)

  def test_make_func(self):
    column = Column(**{ 'Area': 6e13, 'z': np.asarray(np.linspace(-4000, 0, 80)), 'kappa': 2e-5 }) 
    myst = lambda: 42
    assert column.make_func(myst, 'myst')() == myst()
    myst = np.arange(0.0, 8.0, 0.1)
    for z in column.z:
      assert column.make_func(myst, 'myst')(z) == np.interp(z, column.z, myst)
    myst = 6.0
    for z in column.z:
      assert column.make_func(myst, 'myst')(z) == myst
    myst = 1
    with pytest.raises(TypeError) as mystinfo:
      column.make_func(myst, 'myst')
    assert(str(mystinfo.value) == "('myst', 'needs to be either function, numpy array, or float')")

  