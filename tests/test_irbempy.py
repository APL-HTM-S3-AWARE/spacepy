#!/usr/bin/env	python
#	-*-	coding:	utf-8	-*-
"""
testing	the	irbempy	module

Copyright 2010-2012 Los Alamos National Security, LLC.
"""

import glob
import os
import sys
import unittest
import spacepy_testing
import warnings
import spacepy
import spacepy.omni
import spacepy.time
import spacepy.coordinates
try:
    import spacepy.irbempy as ib
except ImportError: #if IRBEM fails, test suite should not break entirely...
    pass
import numpy as np
import numpy.testing
from numpy import array

__all__ = ['IRBEMBigTests', 'IRBEMTestsWithoutOMNI']


class IRBEMBigTests(unittest.TestCase):

    def setUp(self):
        self.ticks = spacepy.time.Ticktock(['2001-02-02T12:00:00', '2001-02-02T12:10:00'], 'ISO')
        self.loci = spacepy.coordinates.Coords([[3,0,0],[2,0,0]], 'GEO', 'car')
        self.omnivals = spacepy.omni.get_omni(self.ticks, dbase='Test')

    def test_prep_irbem(self):
        expected = {
            'badval': -1e31,
            'degalpha': [0.0] * 25,
            'idoysat': [33.0] * 2 + [0.0] * 99998,
            'ntime_max': 100000,
            'nalp_max': 25,
            'magin': np.zeros((25, 100000)),
            'sysaxes': 1,
            'kext': 10,
            'iyearsat': [2001.] * 2 + [0.0] * 99998,
            'xin3': 0.0 * 100000,
            'xin2': 0.0 * 100000,
            'xin1': [3., 2.] + [0.0] * 99998,
            'utsat': [43200., 43800.] + [0.0] * 99998,
            'options': [1, 0, 0, 0, 0],
            }
        expected['magin'][:, :2] = array(
            [[  3.00000012e+00,   3.00000012e+00],
             [ -9.00000000e+00,  -9.00000000e+00],
             [  3.20000005e+00,   3.15000006e+00],
             [  3.96000000e+02,   3.96000000e+02],
             [  1.07000005e+00,   1.05500005e+00],
             [  2.00000003e-01,  -4.99999917e-02],
             [ -1.00000001e-01,   1.33333326e-01],
             [  9.99999978e-03,   9.99999978e-03],
             [  2.99999993e-02,   2.49999994e-02],
             [  9.99999978e-03,   8.33333313e-03],
             [  2.60000005e-02,   2.46666670e-02],
             [  1.70000009e-02,   1.56666674e-02],
             [  3.16000015e-01,   3.14333344e-01],
             [  6.00000005e-03,   5.50000004e-03],
             [  1.70000009e-02,   1.50000007e-02],
             [  2.19999999e-02,   1.98333332e-02],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00]])

        actual = ib.prep_irbem(self.ticks, self.loci, omnivals=self.omnivals)
        for key in expected:
            numpy.testing.assert_almost_equal(expected[key],
                                              actual[key],
                                              decimal=5)

    def test_prep_irbem_too_many_PA(self):
        """Call prep_irbem with too many pitch angles"""
        with self.assertRaises(ValueError) as cm:
            ib.prep_irbem(self.ticks, self.loci, numpy.arange(5, 180, 5),
                          omnivals=self.omnivals)
        self.assertEqual('Too many pitch angles requested; 25 is maximum.',
                         str(cm.exception))

    def test_find_Bmirror(self):
        expected = {'Blocal': array([ 1031.008992,  3451.98937]),
            'Bmirr': array([ 2495.243004,  8354.355467])}
        for key in expected:
            numpy.testing.assert_almost_equal(expected[key], ib.find_Bmirror(self.ticks, self.loci, [40], omnivals=self.omnivals)[key], decimal=6)

    def test_find_magequator(self):
        expected = {'Bmin': array([ 1030.456337,  3444.077016 ])}
        Bmin_loci = array([[ 2.99935449,  0.005511 , -0.032353  ],
                          [ 2.00289871, -0.00734881,  0.045382]])
        actual = ib.find_magequator(self.ticks, self.loci, omnivals=self.omnivals)
        numpy.testing.assert_almost_equal(expected['Bmin'], actual['Bmin'], decimal=6)
        numpy.testing.assert_almost_equal(Bmin_loci, actual['loci'].data, decimal=6)

    def test_get_Bfield(self):
        """test get_Bfield"""
        expected = {'Blocal': array([ 1031.00899,  3451.98937]),
        'Bvec': array([[    3.49178,  -172.79037 ,  1016.4206],
                       [  335.0928,  -553.03591,  3390.88406]])}
        actual = ib.get_Bfield(self.ticks, self.loci, omnivals=self.omnivals)
        for key in expected.keys():
            numpy.testing.assert_almost_equal(actual[key], expected[key], decimal=5)

    def test_get_Lstar_T01(self):
        # test T01STORM
        expected = {'Xj': array([[ 0.000403], [ 0.00269002]]),
            'Lstar': array([[ 3.025887], [ 2.054195]]),
            'Bmirr': array([[ 1031.008992], [ 3451.98937]]),
            'Lm': array([[ 3.079151], [ 2.059326]]),
            'Bmin': array([ 1030.456337,  3444.077016 ]),
            'MLT': array([ 11.97159175,  12.13313906])}
        actual = ib.get_Lstar(self.ticks, self.loci, [90], omnivals=self.omnivals)
        for key in expected.keys():
            numpy.testing.assert_almost_equal(expected[key], actual[key], decimal=6)

    def test_get_Lstar_T05(self):
        # test T05
        expected = {'Xj': array([[ 0.266114], [ 0.186008]]),
                    'Lstar': array([[ 3.015461], [ 2.043043]]),
                    'Bmirr': array([[ 1150.670441], [ 3895.810805]]),
                    'Lm': array([[ 3.087026], [ 2.059734]]),
                    'Bmin': array([ 1015.468031,  3432.146907]),
                    'MLT': array([ 11.97159175,  12.13313906])}
        actual = ib.get_Lstar(self.ticks, self.loci, [70], extMag='T05', omnivals=self.omnivals)
        for key in expected:
            numpy.testing.assert_almost_equal(expected[key], actual[key], decimal=6)

    def test_get_Lstar_OPQuiet(self):
        # test OP-Quiet
        expected = {'Xj': array([[ 0.001051], [ 0.002722]]),
            'Lstar': array([[ 3.029621], [ 2.059631]]),
            'Blocal': array([ 1019.052401, 3467.52999]),
            'Lm': array([[ 3.091352], [ 2.056261]]),
            'Bmin': array([ 1018.669701,  3459.500966 ]),
            'MLT': array([ 11.97159175,  12.13313906])}
        actual = ib.get_Lstar(self.ticks, self.loci, [90], extMag="OPQUIET", omnivals=self.omnivals)
        for key in expected.keys():
            numpy.testing.assert_almost_equal(expected[key], actual[key], decimal=6)

    def test_get_Lstar_OPQuiet_multi(self):
        """Test Lstar on OPQ forcing multiprocess"""
        cpu_actual = spacepy.config['ncpus']
        # To trigger a worker pool, number of calcs must be
        # more than double number of cpus
        spacepy.config['ncpus'] = 4
        try:
            ticks = spacepy.time.tickrange(self.ticks.ISO[0], self.ticks.ISO[-1], 1/1440.)
            ncalc = len(ticks)  # Forced 10 times in test data range
            loci = spacepy.coordinates.Coords([[nc-4, 6-nc, 0] for nc in range(ncalc)], 'GEO', 'car')
            omnivals = spacepy.omni.get_omni(ticks, dbase='Test')
            expected = {'Lstar': array([[6.84698], [5.58814], [4.35608],
                                        [3.13613], [1.97344], [1.41439],
                                        [2.05375], [3.19979], [4.35920],
                                        [5.38242]]),
                        'Lm': array([[7.61427481], [6.13826804], [4.65907084],
                                     [3.21519241], [1.97225109], [1.41105356],
                                     [2.05626165], [3.28414042], [4.6531115 ],
                                     [5.92800457]])
                        }
            # OPQ won't use the OMNI, but if they're passed in
            # the code still processes them, so answers should be identical
            actuali= ib.get_Lstar(ticks, loci, [90], extMag="OPQUIET", omnivals=omnivals)
            actualn = ib.get_Lstar(ticks, loci, [90], extMag="OPQUIET", omnivals=None)
        finally:
            spacepy.config['ncpus'] = cpu_actual
        # Check that results are as expected
        numpy.testing.assert_almost_equal(expected['Lstar'], actuali['Lstar'], decimal=5)
        numpy.testing.assert_almost_equal(expected['Lm'], actuali['Lm'], decimal=5)
        numpy.testing.assert_almost_equal(expected['Lstar'], actualn['Lstar'], decimal=5)
        numpy.testing.assert_almost_equal(expected['Lm'], actualn['Lm'], decimal=5)

    def test_get_Lstar_TooManyPA(self):
        """test OP-Quiet with too many pitch angles"""
        with self.assertRaises(ValueError) as cm:
            ib.get_Lstar(
                self.ticks, self.loci, numpy.arange(5, 180, 5),
                extMag="OPQUIET", omnivals=self.omnivals)
        self.assertEqual('Too many pitch angles requested; 25 is maximum.',
                         str(cm.exception))

    def test_get_Lstar_OPQuiet_landi2lstar(self):
        # test OP-Quiet with LandI2Lstar routine
        expected = {'Xj': array([[ 0.001051], [ 0.002722]]),
            'Lstar': array([[3.02419 ], [2.053277]]),
            'Blocal': array([ 1019.052401,  3467.52999]),
            'Lm': array([[ 3.091352], [ 2.056261]]),
            'Bmin': array([ 1018.669701,  3459.500966 ]),
            'MLT': array([ 11.97159175,  12.13313906])}
        actual = ib.get_Lstar(self.ticks, self.loci, [90], extMag="OPQUIET", omnivals=self.omnivals,
                              landi2lstar=True)
        for key in expected.keys():
            numpy.testing.assert_almost_equal(expected[key], actual[key], decimal=6)

    def test_AlphaOfK(self):
        '''test calculation of eq. pitch angle from K (regression)'''
        t = spacepy.time.Ticktock(['2001-09-01T04:00:00'], 'ISO')
        loci = spacepy.coordinates.Coords([-4,0,0], 'GSM', 'car')
        ans = spacepy.irbempy.AlphaOfK(t, loci, 0.11, extMag='T89', omnivals=self.omnivals)
        numpy.testing.assert_almost_equal(ans, 50.625, decimal=5)

    def test_find_footpoint(self):
        '''test computation of field line footpoint location/magnitude (regression)'''
        expected = {'Bfoot': numpy.array([ 47626.93407,  47625.97051]),
                    'loci': spacepy.coordinates.Coords([[ 99.28759,  56.14644, -10.29427],
                                     [ 99.33375,  56.14603, -10.29737]],
                                     dtype='GDZ', carsph='sph', units=['km', 'deg', 'deg'])}
        y = spacepy.coordinates.Coords([[3,0,0],[3,0,0]], 'GEO', 'car')
        ans = spacepy.irbempy.find_footpoint(self.ticks, y, omnivals=self.omnivals)
        numpy.testing.assert_almost_equal(expected['Bfoot'], ans['Bfoot'], decimal=5)
        numpy.testing.assert_almost_equal(expected['loci'].data, ans['loci'].data, decimal=5)


class IRBEMTestsWithoutOMNI(unittest.TestCase):

    def setUp(self):
        self.ticks = spacepy.time.Ticktock(['2002-02-02T12:00:00', '2002-02-02T12:10:00'], 'ISO')
        self.loci = spacepy.coordinates.Coords([[3,0,0],[2,0,0]], 'GEO', 'car')

    def test_get_dtype(self):
        sysaxes = 3
        expected = ('GSE', 'car')
        self.assertEqual(expected, ib.get_dtype(sysaxes))

    def test_get_sysaxes(self):
        """Test that expected value is returned for sysaxes query"""
        dtype = 'GSE'
        self.assertEqual(3, ib.get_sysaxes(dtype, 'car'))
        self.assertEqual(None, ib.get_sysaxes(dtype, 'sph'))

    def test_prep_irbem_sysaxesnone(self):
        """prep_irbem should handle 'car' and 'sph' version of systems identically"""
        locc = spacepy.coordinates.Coords([[3,0,0],[2,0,0]], 'GSM', 'car')
        out1 = ib.prep_irbem(ticks=self.ticks, loci=locc,
                             extMag='0', options=[1, 0, 0, 0, 1])
        pos = ib.car2sph(locc.data)
        locs = spacepy.coordinates.Coords(pos, 'GSM', 'sph')
        out2 = ib.prep_irbem(ticks=self.ticks, loci=locs,
                             extMag='0', options=[1, 0, 0, 0, 1])
        self.assertEqual(out1['sysaxes'], out2['sysaxes'])
        numpy.testing.assert_almost_equal(out1['xin1'], out2['xin1'])
        numpy.testing.assert_almost_equal(out1['xin2'], out2['xin2'])
        numpy.testing.assert_almost_equal(out1['xin3'], out2['xin3'])

    def test_sph2car(self):
        loc = [1,45,45]
        expected = array([ 0.5,  0.5,  0.70710678])
        with warnings.catch_warnings(record=True) as w:
            if sys.version_info[0:2] == (2, 7)\
               and hasattr(ib, '__warningregistry__'):
                # filter 'always' is broken in Python 2.7
                # https://stackoverflow.com/questions/56821539/
                for k in ib.__warningregistry__.keys():
                    if k[0].startswith(
                            'moved to spacepy.coordinates') \
                            and k[1] is DeprecationWarning:
                        del ib.__warningregistry__[k]
                        break
            warnings.simplefilter('always', category=DeprecationWarning)
            tst = ib.sph2car(loc)
        self.assertEqual(1, len(w))
        self.assertEqual(DeprecationWarning, w[0].category)
        numpy.testing.assert_almost_equal(expected, tst)

    def test_car2sph(self):
        loc = [ 0.5,  0.5,  0.70710678]
        expected = [1,45,45]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always', category=DeprecationWarning)
            tst = ib.car2sph(loc)
        self.assertEqual(1, len(w))
        self.assertEqual(DeprecationWarning, w[0].category)
        numpy.testing.assert_almost_equal(expected, tst)

    def test_coord_trans(self):
        self.loci.ticks = self.ticks
        expected = array([[ 2.86714166, -0.02178308,  0.88262348],
            [ 1.91462214,  0.06992421,  0.57387514]])
        numpy.testing.assert_almost_equal(expected, ib.coord_trans(self.loci, 'GSM', 'car'))

    def test_GSM_SM_init(self):
        '''test for initialization error in gsm to sm conversion'''
        cc_got = ib.oplib.coord_trans1(2, 4, 2002, 33, 43200, np.asarray([1., 2., 4.]))
        expected = np.array([1.9286, 2., 3.6442])
        # NaN will result if init not done in IRBEM, assert_almost_equal will
        # compare NaNs without complaint
        numpy.testing.assert_almost_equal(expected, cc_got, decimal=3)

    def test_get_AEP8(self):
        """test get_AEP8"""
        c=self.loci
        c.ticks = self.ticks
        E = 2.0 # energy in MeV
        expected = 99492.059080021136
        actual = ib.get_AEP8(E, c)
        numpy.testing.assert_almost_equal(expected, actual)
# -----------------------------------------------------------------------


if	__name__	==	"__main__":
    ##	suite	=	unittest.TestLoader().loadTestsFromTestCase(SimpleFunctionTests)
    ##	unittest.TextTestRunner(verbosity=2).run(suite)

    ##	suite	=	unittest.TestLoader().loadTestsFromTestCase(tFunctionTests)
    ##	unittest.TextTestRunner(verbosity=2).run(suite)

    unittest.main()





