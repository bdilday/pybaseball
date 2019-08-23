import pybaseball as pbb
import pandas as pd
from numpy import sqrt
import unittest
import os

class TestStatcastSpinCalculations(unittest.TestCase):

	def test_data_import(self):
		frame = pd.read_csv(os.path.relpath('./statcast_pitching_test_data.csv'))
		self.assertFalse(frame.size == 0)


if __name__ == '__main__':
	unittest.main()
