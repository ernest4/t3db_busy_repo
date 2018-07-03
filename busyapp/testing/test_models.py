from django.test import TestCase #this inherits from unittest.TestCase
from busyapp import ml

class ModelTest(TestCase):
    #run your setup here (if any)
    def setUp(self):
        pass


    #example test...
    def test_simple_check(self):
        self.assertEqual(1, 1)
        self.assertTrue(True)
        self.assertFalse(False)
        with self.assertRaises(Exception):
            raise Exception


    # the main test(s)
    def test_46A_SVM(self):
        self.assertEqual(round(ml.predictor_svm(busNum='46A',
                                                start_stop=1,
                                                end_stop=20,
                                                time_of_day=50000,
                                                weatherCode=803,
                                                testing=True)[0]), 2503) #???

    def test_46A_regression(self):
        self.assertEqual(round(ml.predictor_regression(busNum='46A',
                                                      start_stop=1,
                                                      end_stop=4,
                                                      time_of_day=43200,
                                                      weatherCode=None,
                                                      testing=True)[0]), 229)


    #run your clean up here (if any)
    def tearDown(self):
        pass