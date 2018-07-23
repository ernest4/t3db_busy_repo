from django.test import TestCase #this inherits from unittest.TestCase
from busyapp import ml
from sklearn.externals import joblib
import datetime
import json

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
    # def test_46A_SVM(self):
    #     self.assertEqual(round(ml.predictor_svm(busNum='46A',
    #                                             start_stop=1,
    #                                             end_stop=20,
    #                                             time_of_day=50000,
    #                                             weatherCode=803,
    #                                             testing=True)), 2503) #???

    def test_46A_regression(self):
        self.assertEqual(round(ml.predictor_regression(busNum='46A',
                                                      start_stop=1,
                                                      end_stop=4,
                                                      time_of_day=43200,
                                                      weatherCode=None,
                                                      testing=True)), 229)

    def test_46A_ann(self):
        self.assertEqual(round(ml.predictor_ann(busNum='46A',
                                                  start_stop=1,
                                                  end_stop=4,
                                                  time_of_day=43200,
                                                  weatherCode=801,
                                                  testing=True)), 238)

    # def test_46A_ann_improved(self):
    #     # Automatically get current time of day
    #     now = datetime.datetime.now() + datetime.timedelta(minutes=60)  # time of day since epoch + 1h correction for linux server
    #     time_of_day = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    #
    #     year2018inSeconds = 1514764800
    #     startOfYear = datetime.datetime.utcfromtimestamp(year2018inSeconds)
    #     ratio = (startOfYear - now).total_seconds()
    #     dayOfYear = ratio
    #
    #     weekDay = {'mon': 0, 'tue': 1, 'wed': 0, 'thu': 0, 'fri': 0, 'sat': 0, 'sun': 0}  # testing...
    #
    #     self.assertEqual(round(ml.predictor_ann_improved(busNum='46A',
    #                                                      start_stop=1/59,
    #                                                      end_stop=4/59,
    #                                                      time_of_day=time_of_day/86400,
    #                                                      weatherCode=800/804,
    #                                                      secondary_school=0,
    #                                                      primary_school=0,
    #                                                      trinity=0,
    #                                                      ucd=0,
    #                                                      bank_holiday=0,
    #                                                      event=0,
    #                                                      day_of_year=dayOfYear,
    #                                                      weekday=weekDay)), 238)


    # Test findModel to return file name
    def test_getModelAndProgNum(self):
        # Assert return pkl reference
        self.assertTrue(ml.getModelAndProgNum('46a', 'Phoenix Park', 810, 2795, True), ('46A_1', 12, 4))

        print(ml.getModelAndProgNum('46a', 'Phoenix Park', 810, 2795, True))

        # Assert return None if route not found
        self.assertEqual(ml.getModelAndProgNum('3000', 'Phoenix Park', 0, 0, True), None)

        # Assert return None if direction not found
        self.assertEqual(ml.getModelAndProgNum('1', '', 0, 0, True), None)


    def test_getProgNum(self):
        with open('static/bus_data/routes.json') as f:
            data = json.load(f)

            self.assertEqual(ml.getProgNum(data, '46A', 'I', 2795), 12)

            self.assertEqual(ml.getProgNum(data, '7', 'I', 2040), 40)

            self.assertEqual(ml.getProgNum(data, '4', 'I', 7113), 3)

            self.assertEqual(ml.getProgNum(data, '36', 'I', 0), None)


    #run your clean up here (if any)
    def tearDown(self):
        pass