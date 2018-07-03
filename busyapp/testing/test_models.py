from django.test import TestCase #this inherits from unittest.TestCase

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
        pass

    def test_46A_regression(self):
        pass


    #run your clean up here (if any)
    def tearDown(self):
        pass