import os
import shutil
import xml.etree.ElementTree as ET
import time as TIME
import datetime
startdir = '.'
version = '1.1'
#ts = time.strftime("%Y%m%d%H%M")

def copyFiles ():

        count = 0
        
        for (dirname, dirs, files) in os.walk('.'):
                for f in files:
                        if (f[0:][-4:] == '.xml'):
                                dst = startdir + '\\..\\Processed Data\\' + str(dirname)
                                src = str(dirname)+'\\'+str(f)
                                if not (os.path.isdir(dst)):
                                        os.makedirs(dst)
                                        print('Created new directory')
                                shutil.copy2(src, dst)
                                count = count + 1
        print(str(count) + ' files copied')

def checkFile (file):
        
        with open(file, 'r') as f:
                filecount=0
                lines = f.read().splitlines()
                last_line = lines[-1]
                if (last_line != '</Protocol>'):
                        f.close()
                        with open(file, 'a') as f:
                                f.write('</Protocol>')
                                print('File amended: ', file)                           
                                f.close()
                                return 1
        return 0

def processFiles ():
        
        count = 0
        updates = 0
        
        for (dirname, dirs, files) in os.walk('.\\..\\Processed Data\\'):
                for filename in files:
                        if filename.endswith('.xml'):
                                file = dirname + '\\' + filename
                                updates = updates + checkFile(file)
                                count = count + 1
        return [count, updates]

def checkFiles ():
                
                highHumidity = 65.4
                lowHumidity = 55
                highTemp = 27.5
                lowTemp = 22.5
                outOfSpec = []
                ts = TIME.strftime('%y%m%d%H%M')
                output = 'assessment_' + TIME.strftime('%y%m%d%H%M') + '.txt'
                
                for (dirname, dirs, files) in os.walk('.\\..\\Processed Data\\'):
                        errors = [0,0]
                        
                        with open(output,'a') as f:
                                for filename in files:
                                        if filename.endswith('.xml'):
                                                file = dirname + '\\' + filename
                                                print('Reading file: ' + file)
                                                tree = ET.parse(file)
                                                root = tree.getroot()
                                                for elem in root.iter('PI'):
                                                        if type(elem.attrib.get('T1R')) == None:
                                                                continue
                                                        else:
                                                                time = elem.attrib.get('Tm')
                                                                h=float(elem.attrib.get('HR'))
                                                                t=float(elem.attrib.get('T1R'))
                                                                
                                                                if h >= highHumidity or h <= lowHumidity:
                                                                        f.write('Humidity error on timestamp: ' + time + ' ----- [FROM FILE ' + os.path.abspath(file) +']\n')
                                                                        errors[0] += 1
                                                                        if errors[0] >= 1440:
                                                                                outOfSpec.append('Humidity error: ' + file + '--' + time)
                                                                else: errors[0] = 0
                                                                
                                                                if t >= highTemp or t <= lowTemp:
                                                                        f.write('Temperature error on timestamp: ' + time + ' ----- [FROM FILE ' + os.path.abspath(file) +']\n')
                                                                        errors[1] += 1
                                                                        if errors[1] >= 1440:
                                                                                outOfSpec.append('Temperature error: ' + file + '--' + time)
                                                                else: errors[1] = 0
                
                with open(output,'a') as f:             
                        if len(outOfSpec)>=1:
                                        f.write('Out of specification errors were found!\n' + 
                                                'Timestamps marking end of discrepancy period:\n')
                                        for i in outOfSpec:
                                                f.write('     ' + i +'\n')
                        f.write('\n')
                return outOfSpec, output

def getTime():
        cTime = TIME.localtime()
        hour = cTime[3]
        minute = cTime[4]

        return str(hour) + ':' + str(minute)

def getDate():
        date = datetime.date.today()
        return str(date.day) + '-' + str(date.month) + '-' + str(date.year)
        
def main():
        copyFiles()
        [count, updates] = processFiles()
        errors = checkFiles()
        count = 'Total files scanned: ' + str(count)
        updates = 'File structures updated: ' + str(updates)
        oos = 'Number of out of spec periods: ' + str(len(errors[0]))
        
        with open(errors[1],'a') as f:          
                f.write(count + '\n')
                f.write(updates + '\n')
                f.write(oos + '\n')
                f.write('\n')
                f.write('Stability Assessor run by: ' + os.getenv('username'))
                f.write(' at ' + getTime() + ' on ' + getDate() +'\n')
                f.write('Produced by "stabilityAssessor.py" Version: ' + version + '\n')

        if len(errors[0])>0: 
                print('Out of specification errors were found! \nCheck ' + errors[1])

        raw_input('Press enter to exit')
        
main()
