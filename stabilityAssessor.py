'''stabilityAssessor.py - Automated assessment of stability chamber xml output files

	Version 1.0
	Creation date 21/08/18
	Author Spencer Skett
	
	The script assesses all xml files in current and sub- directories and reports out of range temperature and humidity readings. 
	A sequence of 1440 out of range readings will be reported as an out-of-spec result.

	A timestamped output file is created with a record of all out of range values and summary of the number of files processed, 
	number of out of range values found and detail of any out-of-spec results found (filename and timestamp of end of invalid period).
''' 

import os
import xml.etree.ElementTree as ET
import time as TIME


# Set current directory as root for the file search and location for output report
startdir = '.'

'''Check all files in current and sub- directories for valid xml structure'''
def processfiles ():
	
	count = 0
	updates = 0

	for (dirname, dirs, files) in os.walk(startdir):
		for filename in files:
			if filename.endswith('.xml'):
				file = dirname + '\\' + filename
				updates = updates + checkfile(file)
				#Keep count of total number of files checked
				count = count + 1
	return [count, updates]



'''Creates valid xml file from Memmert HP110 output files'''
def checkfile (file):
	
	# Open the file in 'readonly' state to check valid structure
	with open(file, 'r') as f:
		filecount=0
		lines = f.read().splitlines()
		last_line = lines[-1]
		#Check that last line of file has a closing tag
		if (last_line != '</Protocol>'):
			f.close()
			#If no closing tag file is reopened in writeable state and tag appended at end of file
			with open(file, 'a') as f:
				f.write('</Protocol>')
				print('File amended: ', file)				
				f.close()
				#Add 1 to count of amended files
				return 1
	#Do not add to count of amended files if file already valid.
	return 0


'''Processing of each valid log file in the folder structure for out of range temperature and humidity readings''' 
def checkfiles ():
		
		#Set allowed ranges
		highHumidity = 65.4
		lowHumidity = 55
		highTemp = 27.5
		lowTemp = 22.5

		outOfSpec = []
		ts = TIME.strftime('%y%m%d%H%M')
		
		for (dirname, dirs, files) in os.walk(startdir):
			errors = [0,0]
			output = 'assessment_' + ts + '.txt'
			with open(output,'a') as f:
				for filename in files:
					#Only process xml files
					if filename.endswith('.xml'):
						file = dirname + '\\' + filename
						tree = ET.parse(file)
						root = tree.getroot()
						for elem in root.iter('PI'):
							#Ignore any lines of output file that have no readings (should be first line only)
							if type(elem.attrib.get('T1R')) == None:
								continue
							else:
								#Get the time, humidity and temperature values for the line's readings
								time = elem.attrib.get('Tm')
								h=float(elem.attrib.get('HR'))
								t=float(elem.attrib.get('T1R'))
								
								#Check if humidity is outside of the allowed range. Log any out of range results.
								if h >= highHumidity or h <= lowHumidity:
									f.write('Humidity error on timestamp: ' + time + ' ----- [FROM FILE' + file +']\n')
									errors[0] += 1
									#If there are 24hours worth of continuous out of range readings, record an out of spec result
									if errors[0] >= 1440:
										outOfSpec.append('Humidity error: ' + file + '--' + time)
								else: errors[0] = 0
								
								#Check if temperature is outside of the allowed range. Log any out of range results.
								if t >= highTemp or t <= lowTemp:
									f.write('Temperature error on timestamp: ' + time + ' ----- [FROM FILE' + file +']\n')
									errors[1] += 1
									#If there are 24hours worth of continuous out of range readings, record an out of spec result
									if errors[1] >= 1440:
										outOfSpec.append('Temperature error: ' + file + '--' + time)
								else: errors[1] = 0
		#Record an alert in the output file that out of spec results exist, and specify the file and timestamp of the end of the invalid period
		with open(output,'a') as f:		
			if len(outOfSpec)>=1:
					f.write('Out of specification errors were found!\n' + 
						'Timestamps marking end of discrepancy period:\n')
					for i in outOfSpec:
						f.write('     ' + i +'\n')
			f.write('\n')
		return outOfSpec, output

'''Main function to run tests and create summary in output file'''	
def main():
	
	#Check xml files in folder structure are valid. Amend any that aren't.
	[count, updates] = processfiles()
	
	#Process xml files to check for temp/humidity excursions.	
	errors = checkfiles()

	#Generate summary of assessment to append to end of output file
	count = 'Total files scanned: ' + str(count)
	updates = 'File structures updated: ' + str(updates)
	oos = 'Number of out of spec periods: ' + str(len(errors[0]))
	
	with open(errors[1],'a') as f:		
		f.write(count + '\n')
		f.write(updates + '\n')
		f.write(oos + '\n')
		

	if len(errors[0])>0: 
		print('Out of specification errors were found! \nCheck ' + errors[1])

	
#Call main program loop
main()
