# -*- coding:utf-8 -*-
#
# MIT License
#
# Copyright (c) 2017 Mattia Verga <mattia.verga@tiscali.it>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import unittest
from pyongc import ongc

import mock
import numpy as np


class TestDsoClass(unittest.TestCase):
    """Test that Dso objects are created in the right way and that data
    is retrieved correctly.
    """
    @mock.patch('pyongc.ongc.DBPATH', 'badpath')
    def test_fail_database_connection(self):
        """Test a failed connection to database."""
        self.assertRaisesRegex(OSError, 'There was a problem accessing database file',
                               ongc.Dso, 'NGC0001')
        self.assertRaisesRegex(OSError, 'There was a problem accessing database file',
                               ongc.listObjects)
        self.assertRaisesRegex(OSError, 'There was a problem accessing database file',
                               ongc.stats)

    def test_dso_creation_error(self):
        """Test we get a type error if user doesn't input a string."""
        self.assertRaisesRegex(TypeError, 'Wrong type as parameter', ongc.Dso, 1234)

    def test_name_recognition(self):
        """Test the regex used to convert the name of the object inputted by the user
        to the correct form.
        """
        self.assertEqual(ongc.Dso('ngc1')._name, 'NGC0001')
        self.assertEqual(ongc.Dso('ic 1')._name, 'IC0001')
        self.assertEqual(ongc.Dso('ic80 ned1')._name, 'IC0080 NED01')
        self.assertEqual(ongc.Dso('ngc61a')._name, 'NGC0061A')
        self.assertRaisesRegex(ValueError, 'Wrong object name', ongc.Dso, 'M15')
        self.assertRaisesRegex(ValueError, 'Wrong object name', ongc.Dso, 'NGC77777')
        self.assertRaisesRegex(ValueError, 'Wrong object name', ongc.Dso, 'NGC0001ABC')
        self.assertRaisesRegex(ValueError, 'not found in the database', ongc.Dso, 'NGC0001A')

    def test_duplicate_resolving(self):
        """Test that a duplicated object is returned as himself when asked to do so."""
        self.assertEqual(ongc.Dso('ngc20')._name, 'NGC0006')
        self.assertEqual(ongc.Dso('ngc20', returndup=True)._name, 'NGC0020')
        self.assertEqual(ongc.Dso('ic555')._name, 'IC0554')

    @mock.patch('pyongc.ongc._queryFetchOne')
    def test_bad_ra(self, corrupted_data):
        """Test useful error message on object creation if R.A. data is corrupted."""
        corrupted_data.return_value = ('2', 'G', 'Galaxy', 'O0:11:00.88', '-12:49:22.3')
        self.assertRaisesRegex(ValueError, 'I can\'t recognize R.A. data', ongc.Dso, 'IC2')

    @mock.patch('pyongc.ongc._queryFetchOne')
    def test_bad_dec(self, corrupted_data):
        """Test useful error message on object creation if Declination data is corrupted."""
        corrupted_data.return_value = ('2', 'G', 'Galaxy', '00:11:00.88', '-I2:49:22.3')
        self.assertRaisesRegex(ValueError, 'I can\'t recognize Declination data', ongc.Dso, 'IC2')

    def test_object_print(self):
        """Test basic object data representation."""
        obj = ongc.Dso('NGC1')

        expected = 'NGC0001, Galaxy in Peg'
        actual = str(obj)
        self.assertEqual(actual, expected)

    def test_getDec(self):
        """Test Declination as string is returned correctly."""
        obj = ongc.Dso('IC15')
        expected = '-00:03:40.6'
        self.assertEqual(obj.getDec(), expected)
        # Nonexistent object
        obj = ongc.Dso('NGC6991')
        expected = 'N/A'
        self.assertEqual(obj.getDec(), expected)

    def test_getRA(self):
        """Test Declination as string is returned correctly."""
        obj = ongc.Dso('NGC475')
        expected = '01:20:02.00'
        self.assertEqual(obj.getRA(), expected)
        # Nonexistent object
        obj = ongc.Dso('NGC6991')
        expected = 'N/A'
        self.assertEqual(obj.getRA(), expected)

    def test_get_coordinates_successful(self):
        """Test succesful getCoords() method."""
        obj = ongc.Dso('NGC1')

        np.testing.assert_equal(obj.getCoords(), ([[0., 7., 15.84], [27., 42., 29.1]]))

    def test_get_coordinates_nonexistent(self):
        """Test getCoords() on a Nonexistent object which doesn't have coords."""
        obj = ongc.Dso('IC1064')

        expected = 'Object named IC1064 has no coordinates in database.'
        with self.assertRaisesRegex(ValueError, expected):
            obj.getCoords()

    def test_get_PN_central_star_data(self):
        """Test retrieving Planetary Nebulaes central star data."""
        # With central star identifiers
        obj = ongc.Dso('NGC1535')
        expected = (['BD -13 842', 'HD 26847'], None, 12.19, 12.18)
        self.assertEqual(obj.getCStarData(), expected)
        # Without central star identifiers
        obj = ongc.Dso('IC289')
        expected = (None, None, 15.1, 15.9)
        self.assertEqual(obj.getCStarData(), expected)

    def test_get_object_identifiers(self):
        """Test getIdentifiers() method."""
        obj = ongc.Dso('NGC650')
        expected = ('M076', ['NGC0651'], None, ['Barbell Nebula', 'Cork Nebula',
                    'Little Dumbbell Nebula'], ['2MASX J01421808+5134243', 'IRAS 01391+5119',
                    'PN G130.9-10.5'])
        self.assertEqual(obj.getIdentifiers(), expected)

        obj = ongc.Dso('IC5003')
        expected = (None,
                    None,
                    ['IC5029', 'IC5039', 'IC5046'],
                    None,
                    ['2MASX J20431434-2951122', 'ESO 463-020', 'ESO-LV 463-0200',
                     'IRAS 20401-3002', 'MCG -05-49-001', 'PGC 065249'])
        self.assertEqual(obj.getIdentifiers(), expected)

    def test_get_magnitudes(self):
        """Test getMagnitudes() method."""
        obj = ongc.Dso('NGC1')

        expected = (13.4, None, 10.78, 10.02, 9.76)
        self.assertEqual(obj.getMagnitudes(), expected)

    def test_get_main_identifier(self):
        """Test getName() method."""
        obj = ongc.Dso('NGC1')

        expected = 'NGC0001'
        self.assertEqual(obj.getName(), expected)

    def test_get_object_notes(self):
        """Test getNotes() method."""
        obj = ongc.Dso('NGC6543')

        expected = ('Additional radio sources may contribute to the WMAP flux.',
                    'Dimensions taken from LEDA')
        self.assertEqual(obj.getNotes(), expected)

    def test_xephem_format(self):
        """Test object representation in XEphem format."""
        obj = ongc.Dso('NGC1')
        expected = 'NGC0001,f|G,00:07:15.84,+27:42:29.1,13.4,,94.2|64.2|1.07'
        self.assertEqual(obj.xephemFormat(), expected)

        obj = ongc.Dso('NGC405')
        expected = 'NGC0405,f,01:08:34.11,-46:40:06.6,7.17,,||'
        self.assertEqual(obj.xephemFormat(), expected)


class TestDsoMethods(unittest.TestCase):
    """Test functions about DS Objects."""
    def test__distance(self):
        """Test distance calculation."""
        np.testing.assert_allclose(ongc._distance(np.array([[0., 0., 0.], [0., 0., 0.]]),
                                                  np.array([[1., 0., 0.], [0., 0., 0.]])),
                                   (15, 15, 0),
                                   1e-12
                                   )
        np.testing.assert_allclose(ongc._distance(np.array([[0., 0., 0.], [0., 0., 0.]]),
                                                  np.array([[23., 0., 0.], [0., 0., 0.]])),
                                   (15, 345, 0),
                                   1e-12
                                   )
        np.testing.assert_allclose(ongc._distance(np.array([[0., 0., 0.], [0., 0., 0.]]),
                                                  np.array([[0., 0., 0.], [15., 0., 0.]])),
                                   (15, 0, 15),
                                   1e-12
                                   )
        np.testing.assert_allclose(ongc._distance(np.array([[0., 0., 0.], [0., 0., 0.]]),
                                                  np.array([[0., 0., 0.], [-15., 0., 0.]])),
                                   (15, 0, -15),
                                   1e-12
                                   )

    def test__str_to_coords(self):
        """Test conversion from string to coordinates."""
        np.testing.assert_equal(ongc._str_to_coords('00:12:04.5 +22:3:45'),
                                np.array([[0., 12., 4.5], [22., 3., 45.]])
                                )
        np.testing.assert_equal(ongc._str_to_coords('10:02:34.99 -8:44:12.3'),
                                np.array([[10., 2., 34.99], [-8., 44., 12.3]])
                                )

    def test__str_to_coords_not_recognized(self):
        """Test failed conversion from string to coordinates."""
        bad_coords = '11:11:11 1:2:3'
        self.assertRaisesRegex(ValueError,
                               'This text cannot be recognized as coordinates: ' + bad_coords,
                               ongc._str_to_coords, bad_coords)

    def test_calculate_separation_raw(self):
        """Test that the calculated apparent angular separation between two objects
        is correct and reports the raw data to user.
        """
        obj1 = ongc.Dso('NGC6070')
        obj2 = ongc.Dso('NGC6118')

        expected = (4.207483963913541, 2.9580416666666864, -2.9927499999999996)
        self.assertEqual(ongc.getSeparation(obj1, obj2), expected)

    def test_calculate_separation_friendly(self):
        """Test that the calculated apparent angular separation between two objects
        is correct and returns a user friendly output.
        """
        expected = '4° 12m 26.94s'
        self.assertEqual(ongc.getSeparation('NGC6118', 'NGC6070', style='text'), expected)

    def test_get_neighbors(self):
        """Test that neighbors are correctly found and returned."""
        obj1 = ongc.Dso('NGC521')

        neighbors = ongc.getNeighbors(obj1, 15)
        expectedListLength = 2
        expectedNearest = 'IC1694, Galaxy in Cet'
        expectedNearestSeparation = 0.13726168561780452

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_negative_dec(self):
        """Test that neighbors are correctly found and returned - with negative Dec value."""
        obj1 = ongc.Dso('IC60')

        neighbors = ongc.getNeighbors(obj1, 30)
        expectedListLength = 1
        expectedNearest = 'IC0058, Galaxy in Cet'
        expectedNearestSeparation = 0.4064105387726472

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_above0ra(self):
        """Test that neighbors are correctly found and returned - with RA just above 00h."""
        obj1 = ongc.Dso('IC1')

        neighbors = ongc.getNeighbors(obj1, 15)
        expectedListLength = 2
        expectedNearest = 'NGC0016, Galaxy in Peg'
        expectedNearestSeparation = 0.1378555838270968

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_below0ra(self):
        """Test that neighbors are correctly found and returned - with RA just below 00h."""
        obj1 = ongc.Dso('IC1523')

        neighbors = ongc.getNeighbors(obj1, 60)
        expectedListLength = 1
        expectedNearest = 'NGC7802, Galaxy in Psc'
        expectedNearestSeparation = 0.7874886760327793

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_with_filter(self):
        """Test that neighbors are correctly found and returned."""
        neighbors = ongc.getNeighbors('NGC521', 15, catalog='NGC')
        expectedListLength = 1
        expectedNearest = 'NGC0533, Galaxy in Cet'
        expectedNearestSeparation = 0.24140243942744602

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_bad_value(self):
        """Return the right message if search radius value is out of range."""
        self.assertRaisesRegex(ValueError,
                               'The maximum search radius allowed is 10 degrees.',
                               ongc.getNeighbors, 'IC1', 601)

    def test_list_all_objects(self):
        """Test the listObjects() method without filters.
        It should return all objects from database.
        """
        objectList = ongc.listObjects()

        self.assertEqual(len(objectList), 13954)
        self.assertIsInstance(objectList[0], ongc.Dso)

    def test_list_objects_filter_catalog_NGC(self):
        """Test the listObjects() method with catalog filter applied."""
        objectList = ongc.listObjects(catalog='NGC')

        self.assertEqual(len(objectList), 8343)

    def test_list_objects_filter_catalog_IC(self):
        """Test the listObjects() method with catalog filter applied."""
        objectList = ongc.listObjects(catalog='IC')

        self.assertEqual(len(objectList), 5611)

    def test_list_objects_filter_catalog_M(self):
        """Test the listObjects() method with catalog filter applied."""
        objectList = ongc.listObjects(catalog='M')

        self.assertEqual(len(objectList), 107)

    def test_list_objects_filter_type(self):
        """Test the listObjects() method with type filter applied.
        Duplicated objects are not resolved to the main object.
        """
        objectList = ongc.listObjects(type='Dup')

        self.assertEqual(len(objectList), 634)
        self.assertEqual(str(objectList[0]), 'IC0011, Duplicated record in Cas')

    def test_list_objects_filter_constellation(self):
        """Test the listObjects() method with constellation filter applied."""
        objectList = ongc.listObjects(constellation='Boo')

        self.assertEqual(len(objectList), 532)

    def test_list_objects_filter_size(self):
        """Test the listObjects() method with size filters applied."""
        objectList = ongc.listObjects(minsize=15, maxsize=20)

        self.assertEqual(len(objectList), 40)

    def test_list_objects_with_no_size(self):
        """Test the listObjects() method to list objects without size."""
        objectList = ongc.listObjects(maxsize=0)

        self.assertEqual(len(objectList), 2015)

    def test_list_objects_filter_mag(self):
        """Test the listObjects() method with magnitudes filters applied."""
        objectList = ongc.listObjects(uptobmag=8, uptovmag=10)

        self.assertEqual(len(objectList), 168)

    def test_list_objects_with_name(self):
        """Test the listObjects() method to list objects with common name."""
        objectList = ongc.listObjects(withname=True)

        self.assertEqual(len(objectList), 121)

    def test_list_objects_without_name(self):
        """Test the listObjects() method to list objects without common name."""
        objectList = ongc.listObjects(withname=False)

        self.assertEqual(len(objectList), 13833)

    def test_list_objects_wrong_filter(self):
        """Test the listObjects() method when an unsupported filter is used."""
        expected = 'Wrong filter name.'

        with self.assertRaisesRegex(ValueError, expected):
            ongc.listObjects(catalog='NGC', name='NGC1')

    def test_nearby(self):
        """Test that searching neighbors by coords works properly."""
        obj = ongc.Dso('NGC521')
        objCoords = ' '.join([obj.getRA(), obj.getDec()])

        neighbors = ongc.getNeighbors(obj, 15)
        nearby_objects = ongc.nearby(objCoords, separation=15)

        self.assertIsInstance(nearby_objects, list)
        self.assertEqual(len(nearby_objects), len(neighbors)+1)
        self.assertEqual(str(nearby_objects[0][0]), str(obj))
        self.assertEqual(nearby_objects[0][1], 0)
        self.assertEqual(str(nearby_objects[1][0]), str(neighbors[0][0]))
        self.assertEqual(nearby_objects[1][1], neighbors[0][1])

    def test_nearby_with_filter(self):
        """Test that neighbors are correctly filtered."""
        obj = ongc.Dso('NGC521')
        objCoords = ' '.join([obj.getRA(), obj.getDec()])

        neighbors = ongc.getNeighbors('NGC521', 15, catalog='IC')
        nearby_objects = ongc.nearby(objCoords, separation=15, catalog='IC')

        self.assertIsInstance(nearby_objects, list)
        self.assertEqual(len(nearby_objects), len(neighbors))
        self.assertEqual(str(nearby_objects[0][0]), str(neighbors[0][0]))
        self.assertEqual(nearby_objects[0][1], neighbors[0][1])

    def test_nearby_bad_value(self):
        """Return the right message if search radius value is out of range."""
        self.assertRaisesRegex(ValueError,
                               'The maximum search radius allowed is 10 degrees.',
                               ongc.nearby, '01:24:33.78 +01:43:53.0', separation=601)

    def test_print_details_obj_galaxy(self):
        """Test that printDetails() output is formatted in the right way for galaxies."""
        obj_details = ongc.printDetails('NGC1')
        expected = (
            "+-----------------------------------------------------------------------------+\n"
            "| Id: 5612      Name: NGC0001           Type: Galaxy                          |\n"
            "| R.A.: 00:07:15.84      Dec.: +27:42:29.1      Constellation: Peg            |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Major axis: 1.57'      Minor axis: 1.07'      Position angle: 112°          |\n"
            "| B-mag: 13.4    V-mag: N/A     J-mag: 10.78   H-mag: 10.02   K-mag: 9.76     |\n"
            "|                                                                             |\n"
            "| Surface brightness: 23.13     Hubble classification: Sb                     |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Other identifiers:                                                          |\n"
            "|    2MASX J00071582+2742291, IRAS 00047+2725, MCG +04-01-025, PGC 000564,    |\n"
            "|    UGC 00057                                                                |\n"
            "+-----------------------------------------------------------------------------+\n"
            )

        self.assertEqual(obj_details, expected)

    def test_print_details_obj_PN(self):
        """Test that printDetails() output is formatted in the right way for PNs."""
        obj_details = ongc.printDetails('NGC40')
        expected = (
            "+-----------------------------------------------------------------------------+\n"
            "| Id: 5651      Name: NGC0040           Type: Planetary Nebula                |\n"
            "| R.A.: 00:13:01.03      Dec.: +72:31:19.0      Constellation: Cep            |\n"
            "| Common names:                                                               |\n"
            "|    Bow-Tie nebula                                                           |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Major axis: 0.8'       Minor axis: N/A        Position angle: N/A           |\n"
            "| B-mag: 11.27   V-mag: 11.89   J-mag: 10.89   H-mag: 10.8    K-mag: 10.38    |\n"
            "|                                                                             |\n"
            "| Central star identifiers:                                                   |\n"
            "|    HD 000826, HIP 001041, TYC 4302-01297-1                                  |\n"
            "|                                                                             |\n"
            "| Central star magnitudes:                                                    |\n"
            "|    U-mag: 11.14            B-mag: 11.82            V-mag: 11.58             |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Other identifiers:                                                          |\n"
            "|    C2, IRAS 00102+7214, PN G120.0+09.8                                      |\n"
            "+-----------------------------------------------------------------------------+\n"
            )

        self.assertEqual(obj_details, expected)

    def test_print_details_obj_nebula(self):
        """Test that printDetails() output is formatted in the right way for nebulae."""
        obj_details = ongc.printDetails('NGC6523')
        expected = (
            "+-----------------------------------------------------------------------------+\n"
            "| Id: 12540     Name: NGC6523           Type: Nebula                          |\n"
            "| R.A.: 18:03:41.27      Dec.: -24:22:48.6      Constellation: Sgr            |\n"
            "| Also known as:                                                              |\n"
            "|    M008, NGC6533                                                            |\n"
            "| Common names:                                                               |\n"
            "|    Lagoon Nebula                                                            |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Major axis: 45.0'      Minor axis: 30.0'      Position angle: N/A           |\n"
            "| B-mag: 5.0     V-mag: 5.8     J-mag: N/A     H-mag: N/A     K-mag: N/A      |\n"
            "|                                                                             |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Other identifiers:                                                          |\n"
            "|    LBN 25                                                                   |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| NED notes:                                                                  |\n"
            "|    Nominal position for NGC 6533 is -30 arcmin in error.                    |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| OpenNGC notes:                                                              |\n"
            "|    B-Mag taken from LEDA, V-mag taken from HEASARC's messier table          |\n"
            "+-----------------------------------------------------------------------------+\n"
            )

        self.assertEqual(obj_details, expected)

    def test_search_for_LBN(self):
        """Test the searchAltId by passing a LBN identifier."""
        obj = ongc.searchAltId("LBN741")

        self.assertEqual(obj.getName(), 'NGC1333')

    def test_search_for_Messier(self):
        """Test the searchAltId by passing a Messier identifier."""
        obj = ongc.searchAltId("M1")

        self.assertEqual(obj.getName(), 'NGC1952')

    def test_search_for_MWSC(self):
        """Test the searchAltId by passing a MWSC identifier."""
        obj = ongc.searchAltId("MWSC146")

        self.assertEqual(obj.getName(), 'IC0166')

    def test_search_for_PGC(self):
        """Test the searchAltId by passing a PGC identifier."""
        obj = ongc.searchAltId("PGC10540")

        self.assertEqual(obj.getName(), 'IC0255')

    def test_search_for_UGC(self):
        """Test the searchAltId by passing a UGC identifier."""
        obj = ongc.searchAltId("UGC9965")

        self.assertEqual(obj.getName(), 'IC1132')


class TestDatabaseIntegrity(unittest.TestCase):
    """Check data integrity."""
    def test_data_integrity(self):
        allObjects = ongc.listObjects()
        for item in allObjects:
            self.assertIsInstance(item.getId(), int)
            self.assertNotEqual(item.getType(), '')
            if item.getType() != 'Nonexistent object':
                coords = item.getCoords()
                self.assertIsInstance(coords, np.ndarray)
                self.assertEqual(coords.shape, (2, 3))
                self.assertNotEqual(item.getDec(), '')
                self.assertNotEqual(item.getRA(), '')
                self.assertNotEqual(item.getConstellation(), '')
                self.assertIsInstance(item.getDimensions(), tuple)
                self.assertIsInstance(item.getMagnitudes(), tuple)


if __name__ == '__main__':
    unittest.main()
