from pybaseball import statcast_pitcher
import pandas as pd
import numpy as np

def statcast_pitcher_spin(start_dt=None, end_dt=None, player_id=None):
	pitcher_data = statcast_pitcher(start_dt, end_dt, player_id)

	spin_df = pitcher_data[['release_extension', 'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az']].copy()

	spin_df = find_release_point(spin_df)
	spin_df = find_release_time(spin_df)
	spin_df = find_release_velocity_components(spin_df)
	spin_df = find_flight_time(spin_df)
	spin_df = find_average_velocity_components(spin_df)
	spin_df = find_average_velocity(spin_df)
	spin_df = find_average_drag(spin_df)
	spin_df = find_magnus_acceleration_magnitude(spin_df)
	spin_df = find_average_magnus_acceleration(spin_df)
	spin_df = find_magnus_magnitude(spin_df)
	spin_df = find_spin_axis(spin_df)

	pitcher_data[['Mx', 'Mz', 'phi']] = spin_df[['Mx', 'Mz', 'phi']].copy()
	return pitcher_data

def get_statcast_pither_test_data():
	df = pd.read_csv("tests/statcast_pitching_test_data.csv")
	return df

def find_release_point(df):
	df['yR'] = (60.5 - df['release_extension'])
	return df

def find_release_time(df):
	df['tR'] = time_duration(df['yR'], df['vy0'], df['ay'], 50, False)
	return df

def find_release_velocity_components(df):
	df['vxR'] = df['vx0'] + (df['ax'] * df['tR'])
	df['vyR'] = df['vy0'] + (df['ay'] * df['tR'])
	df['vzR'] = df['vz0'] + (df['az'] * df['tR'])
	return df

def find_flight_time(df):
	df['tf'] = time_duration(df['yR'], df['vyR'], df['ay'], 17/12, True)
	return df

def find_average_velocity_components(df):
	df['vxbar'] = (2*df['vxR'] + df['ax']*df['tf'])/2
	df['vybar'] = (2*df['vyR'] + df['ay']*df['tf'])/2
	df['vzbar'] = (2*df['vzR'] + df['az']*df['tf'])/2

	df['vxbar'] = df['vxbar'].round(4)
	df['vybar'] = df['vybar'].round(4)
	df['vzbar'] = df['vzbar'].round(4)
	return df

def find_average_velocity(df):
	df['vbar'] = three_comp_average(df['vxbar'], df['vybar'], df['vzbar'])
	return df

def find_average_drag(df):
	df['adrag'] = -(df['ax']*df['vxbar'] + df['ay']*df['vybar'] + (df['az'] + 32.174)*df['vzbar'])/ df['vbar']
	return df

def find_magnus_acceleration_magnitude(df):
	df['amagx'] = df['ax'] + df['adrag']*df['vxbar']/df['vbar']
	df['amagy'] = df['ay'] + df['adrag']*df['vybar']/df['vbar']
	df['amagz'] = df['az'] + df['adrag']*df['vzbar']/df['vbar'] + 32.174
	return df

def find_average_magnus_acceleration(df):
	df['amag'] = three_comp_average(df['amagx'], df['amagy'], df['amagz'])
	return df

def find_magnus_magnitude(df):
	df['Mx'] = 6 * df['amagx'] * (df['tf']**2)
	df['Mz'] = 6 * df['amagz'] * (df['tf']**2)
	return df

def find_spin_axis(df):
	df['phi'] = np.where(df['amagz'] > 0,
		np.arctan2(df['amagz'], df['amagx'])*180/np.pi,
		360 + np.arctan2(df['amagz'], df['amagx'])*180/np.pi)+90
	df['phi'] = df['phi'].round(0).astype('int64')
	return df

# HELPERS
def time_duration(s, v, acc, adj, forward):
	"""
		Finds flight time given an original position, velocity, accelaration, and target position.

		Direction does not affect the time duration. It helps assign a positive or negative
		value to the flight time.

		s = (pd.Series) spacial point at known time
		v = (pd.Series) velocity at known time
		acc = (pd.Series) acceleration
		adj = (pd.Series) spacial difference between known and unknown points
		forward = (bool) idicating whether space_diff is in the positive or negative y direction
	"""
	return (-v - np.sqrt( v**2 - 2*acc*( (1 if forward else -1) * (s-adj) ))) / acc

def three_comp_average(comp1, comp2, comp3):
	return np.sqrt(comp1**2 + comp2**2 + comp3**2).round(4)
