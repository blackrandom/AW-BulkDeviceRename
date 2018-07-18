import requests
import csv
import getpass
import base64

serialnamedict = {}

#Change url to your host
url = "https://host.awmdm.com/api/mdm/devices"
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
    #Format example {"searchBy":"Serialnumber","id":"F9FTPXCPHLJJ"}
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

# It's a good idea to enclose the following in a try-except format.
try:
    #response = requests.request("PUT", url, data=payload, headers=headers, params=querystring)

    #enter AirWatch user credentials
    auth_cred = getbasic_authuser()

    #Build the header after getting credentials
    headers = build_header(aw_tenant_code, accept_type, content_type, auth_cred)
    
    with open('input_serial.csv', 'r') as csvfile:
        read = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(read, None) #skip the header in csv
        for row in read:
            #name = (row[0]) and serial = (row[1])
            #store values in dictionary to maintain key value pairs
            serialnamedict[row[1]] = row[0]
        
        #Traverse the dictionary updating names by doing a serial lookup
        for serialval in serialnamedict:
            serial = serialval
            devicename = serialnamedict[serialval]
            print(serial + ": " + devicename)
            response = requests.request("PUT", url, data=build_payload(devicename), headers=headers, params=build_querystring(serial))
            if response.status_code == 204:
                print("Success!")
            else:
                print("Error, check credentials, api key, or mdm url")
           
except requests.exceptions.RequestException as e:
    print('Get request failed with %s' % e)