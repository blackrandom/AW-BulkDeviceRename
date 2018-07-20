import requests
import json
import csv
import getpass
import base64

serialnamedict = {}
masterserialname = {}
errorserial = []

#Change url to your host
baseurl = "https://host.awmdm.com"
#Add your api key
aw_tenant_code = "apikey"
accept_type = "application/json;version=1"
content_type = "application/json;version=1"
auth_cred = "Basic empty"
headers = {
    'aw-tenant-code': "empty",
    'Accept': "empty",
    'Content-Type': "empty",
    'Authorization': "Basic empty",
    }

def build_querystring(serialnumber):
    #Format example {"searchBy":"Serialnumber","id":"AAABBBCCCDDDEE"}
    query = {"searchby":"Serialnumber",
             "id": serialnumber}
    return query

def build_payload(friendlyname):
    #Format example "{\n\t\"DeviceFriendlyName\": \"SHE-STU018TT\"\n}"
    json_payload = "{\n\t\"DeviceFriendlyName\": \""+ friendlyname +"\"\n}"
    return json_payload

def build_header(tenantcode, apptype, contenttype, authcred):
    #Build with updated authcred in main
    header = {
        'aw-tenant-code': tenantcode,
        'Accept': apptype,
        'Content-Type': contenttype,
        'Authorization': authcred,
        }    
    return header

def getbasic_authuser():
    #Generate Basic auth encoding in Base64, used by airwatch to authenticate user
    user = input("Enter user name: ")
    password = getpass.getpass("Enter password: ")
    credentials = user + ':' + password
    encodedString = base64.urlsafe_b64encode(credentials.encode('UTF-8')).decode('ascii')
    return "Basic " + encodedString

def get_deviceid(baseurl, headers, serial):
    url = "%s/api/mdm/devices" % baseurl
    query = {"searchby": "Serialnumber", "id": serial}
    try:
        response = requests.request("GET", url, headers=headers, params=query)
        data = json.loads(response.text)
        return data['Id']['Value']
    except requests.exceptions.RequestException as e:
        return print('Request failed with %s' % e)

def change_ou(headers, deviceid, groupid):
    url = "%s/api/mdm/devices/%s/commands/changeorganizationgroup/%s" % (baseurl, deviceid, groupid)
    if groupid != -1:
        try:
            response = requests.request("PUT", url, headers=headers)
            print("Success! Changed OU to %s" % groupid)
                         
        except requests.exceptions.RequestException as e:
            print('Request failed with %s' % e)
    else:
        print("Group ID was invalid")

def change_devicename(baseurl, devicename, headers, serial):
    url = "%s/api/mdm/devices"% baseurl
    try:
        # Update device, using SerialNumber as the identifier
        response = requests.request("PUT", url, data=build_payload(devicename), headers=headers, params=build_querystring(serial))

        # If the above gives a 4XX or 5XX error
        response.raise_for_status()
        if response.status_code == 204:
            print("Success!")
        else:
            print("Error, check credentials, api key, or mdm url")
            
    except requests.exceptions.RequestException as e:
        print('Request failed with %s' % e)

def get_groupid(devicename):
    #Pre-assigned and hardcoded since we only have a few groups
    groupid = 0
    if "fis-stu" in devicename.lower():
        groupid = 2485
    elif "she-stu" in devicename.lower():
        groupid = 2486
    elif "oca-stu" in devicename.lower():
        groupid = 2483
    else:
        groupid = -1
        print("%s is either invalid or does not belong to one of the 3 schools"% devicename)
    return groupid

def ipad_validname(serial):
    #Check if serial is in master file, returns the devicename if found
    if serial in masterserialname:
        devicename = masterserialname[serial]
    else:
        devicename = "Not found"
        
    return devicename

def load_csv(csvfilename, dictionary):
    #Loads csv information into memory during session for quicker lookups
    with open(csvfilename, 'r') as csvfile:
        read = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(read, None) #skip the header in csv
        for row in read:
            #name = (row[0]) and serial = (row[1])
            #store values in dictionary to maintain key value pairs
            dictionary[row[1]] = row[0]
        
#
#Main starts here
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

#enter AirWatch user credentials
auth_cred = getbasic_authuser()

#Build the header after getting credentials
headers = build_header(aw_tenant_code, accept_type, content_type, auth_cred)

#Load csv files to memory
load_csv('iPads_SerialName_Full.csv', masterserialname)
load_csv('input_serial.csv', serialnamedict)


#Traverse the serialnamed dictionary updating names by doing a serial lookup
for serialval in serialnamedict:
    devicename = ipad_validname(serialval)
    deviceid = get_deviceid(baseurl, headers, serialval)
    groupid = get_groupid(devicename)
    
    print(serialval + ": " + devicename)
    
    if ipad_validname(serialval) != "Not found":
        #Serial is valid and was found in master file
        change_devicename(baseurl, devicename, headers, serialval)
        change_ou(headers, deviceid, groupid)
        print("Device name changed to %s and moved to %s OU\n" % (devicename, groupid))
    else:
        #Serial was not found in master file
        print("%s not found in master file, logged to error serial list\n"% serialval)
        errorserial.append(serialval)

if errorserial:
    #If serials were not found in the master list print the list
    print("\nSerials that were not found in the master list")
    print(*errorserial, sep = ", ")
    
