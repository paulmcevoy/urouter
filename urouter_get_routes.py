import googlemaps
from datetime import datetime
import requests
import sys
import pandas as pd
import urllib
import os
import calendar
import time
from ftplib import FTP
sys.stdout.flush()

'''
This program fetches a set of latitude and longitude coordinates from a CSV file
and combines with an order to do lookups stored in routes.csv
It then does a lookup and calculates the worst time to get between a source 
and destination when a waypoint via is taken into account
This data is stored in an array which is used in urouter.html to compare 
against the players attempts
Google's Directions API is used to calculate the relevant travel time etc
Finally the data obtained is stored and uploaded to a webpage to run remotely
'''

#def get_maps():
locs_df = pd.read_csv('locs.csv')
routes_df = pd.read_csv('routes.csv')

#Store the maps in a separate folder that can be emptied at startup
dir_path = "maps"
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
fileList = os.listdir(dir_path)
for fileName in fileList:
    os.remove(dir_path+"/"+fileName)
    
#Start off with 0 maps  found
maps_found = 0

#create initial dataframes that will store the API response data
map_df_head = pd.DataFrame([])  
map_df_nohead = pd.DataFrame([])  

#pick an arbitrary point in time to estimate travel time in traffic
month_fixed = 'Dec'
day_fixed = '06'
year_fixed = '2016'
hour_fixed = '08'
minute_fixed = '00'

#just do 8 maps for now
for i in range(8):

    #set valid maps to 0 in case the lookup fails
    valid_map = 0
    #print("day: {}".format(str(day_fixed)))
    print("Getting map number: {}".format(i+1))
    
    #Convert the time to UTC to to the directions lookup
    dep_time = (calendar.timegm(time.strptime(month_fixed + ' ' + day_fixed + ' ' + year_fixed + ' @ '+ hour_fixed + ':' + minute_fixed + ':00 UTC', '%b %d %Y @ %H:%M:%S UTC')))

    #The codes indicate which lat/long values to grab from the locations CSV
    src_code = routes_df.src[i]
    dst_code = routes_df.dst[i]
    via_code = routes_df.via[i]
    

    #Get the src, dst and via lat and longitude values
    src = locs_df.iloc[[src_code]]
    dst = locs_df.iloc[[dst_code]]
    via = locs_df.iloc[[via_code]]

    src_name = src.iloc[0,0]
    dst_name = dst.iloc[0,0]
    via_name = via.iloc[0,0]

    src_lat = src.iloc[0,1]
    src_long = src.iloc[0,2]
    dst_lat = dst.iloc[0,1]
    dst_long = dst.iloc[0,2]
    via_lat = via.iloc[0,1]
    via_long = via.iloc[0,2]

    print("Src: {} {} Dest: {} {} Via: {} {}".format(src_name, src_code, dst_name, dst_code, via_name, via_code))

    
    #do a lookup on durations between points for a best guess, this value isn't that important
    traffic_model = 'best_guess'    
    dirs_url_bes = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + str(src_lat) +',' + str(src_long) + '&destination=' + str(dst_lat) +',' + str(dst_long) + '&waypoints=via:' + str(via_lat) +',' + str(via_long) + '&alternatives=false&mode=driving&traffic_model=' + traffic_model + '&departure_time=' + str(dep_time) + '&key=AIzaSyAYtY6mU5yzSCIror1uX16u-mNQJESHr8I'
    dirs_dict_bes = requests.get(dirs_url_bes).json()  
    encd1 = dirs_dict_bes['routes'][0]['overview_polyline']['points']
    print("Done all best lookups")


    #do a lookup on durations between points for a optimistic, useful to note
    traffic_model = 'optimistic'
    dirs_url_opt = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + str(src_lat) +',' + str(src_long) + '&destination=' + str(dst_lat) +',' + str(dst_long) + '&waypoints=via:' + str(via_lat) +',' + str(via_long) + '&alternatives=false&mode=driving&traffic_model=' + traffic_model + '&departure_time=' + str(dep_time) + '&key=AIzaSyAYtY6mU5yzSCIror1uX16u-mNQJESHr8I'
    dirs_dict_opt = requests.get(dirs_url_opt).json()  
    print("Done all opt lookups")

    
    #This is the value we really want, we compare this against the players guess
    traffic_model = 'pessimistic'
    dirs_url_pes = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + str(src_lat) +',' + str(src_long) + '&destination=' + str(dst_lat) +',' + str(dst_long) + '&waypoints=via:' + str(via_lat) +',' + str(via_long) + '&alternatives=false&mode=driving&traffic_model=' + traffic_model + '&departure_time=' + str(dep_time) + '&key=AIzaSyAYtY6mU5yzSCIror1uX16u-mNQJESHr8I'
    dirs_dict_pes = requests.get(dirs_url_pes).json()  
    print("Done all pess lookups")

    print("Done all current lookups")
 
    #place markers on the map to store in the JPG  
    marker_src = '&markers=color:blue%7Clabel:S%7C' + str(src_lat) +',' + str(src_long) 
    marker_dst = '&markers=color:red%7Clabel:D%7C' + str(dst_lat) +',' + str(dst_long) 
    marker_via = '&markers=color:green%7Clabel:V%7C' + str(via_lat) +',' + str(via_long) 

    #This is the URL we do the directions lookup on with all the fields polulated
    polyurl = 'https://maps.googleapis.com/maps/api/staticmap?size=640x400&scale=2&key=AIzaSyAYtY6mU5yzSCIror1uX16u-mNQJESHr8I' + marker_src + marker_dst + marker_via +'&path=weight:8%7Ccolor:blue%7Cenc:' + encd1
    
    #Print the map info for debug

    #Create the filename based on the map code
    filename = ('map_' + str(src_code) + '_' + str(dst_code) + '_' + str(via_code) + '.jpg')
    map_filename = os.path.join(dir_path, filename)  
    
    #Occasionally the lookup can fail, we ensure we only store data that succeeds in the request
    try:
        urllib.request.urlretrieve(polyurl, map_filename)
        valid_map = 1
  
    except Exception:
        print ("Malformed URL")

    #if we have a valid map keep the data
    if valid_map == 1:
        maps_found += 1

        #get directions for various times and dates out of the JSON response

        dur1_traffic_bes = dirs_dict_bes['routes'][0]['legs'][0]['duration_in_traffic']['value']
        dur1_traffic_txt_bes = dirs_dict_bes['routes'][0]['legs'][0]['duration_in_traffic']['text']
        dist1_bes = dirs_dict_bes['routes'][0]['legs'][0]['distance']['value']
        
        dur1_traffic_opt = dirs_dict_opt['routes'][0]['legs'][0]['duration_in_traffic']['value']
        dur1_traffic_txt_opt = dirs_dict_opt['routes'][0]['legs'][0]['duration_in_traffic']['text']
        dist1_opt = dirs_dict_opt['routes'][0]['legs'][0]['distance']['value']

        dur1_traffic_pes = dirs_dict_pes['routes'][0]['legs'][0]['duration_in_traffic']['value']
        dur1_traffic_txt_pes = dirs_dict_pes['routes'][0]['legs'][0]['duration_in_traffic']['text']
        dist1_pes = dirs_dict_pes['routes'][0]['legs'][0]['distance']['value']
        
        #Two rows that allow for more verbose data in the CSV dump
        row_all = pd.Series([src_code,dst_code,encd1, dist1_bes, dur1_traffic_bes, dist1_opt, dur1_traffic_opt, dist1_pes, dur1_traffic_pes  ])
        row_lim = pd.Series([src_name, dst_name, via_name, src_code,dst_code, via_code, src_lat, src_long, dst_lat, dst_long, via_lat, via_long, dist1_bes, dur1_traffic_bes, dist1_opt, dur1_traffic_opt, dist1_pes, dur1_traffic_pes  ])

        map_df_nohead = map_df_nohead.append(row_lim,ignore_index=True) 
        map_df_head = map_df_head.append(row_lim,ignore_index=True) 

#name the columns, handy for the CSV
map_df_head.columns = ['src_name', ' dst_name', ' via_name', ' src_code', 'dst_code', ' via_code', ' src_lat', ' src_long', ' dst_lat', ' dst_long', ' via_lat', ' via_long', ' dist1_bes', ' dur1_traffic_bes', ' dist1_opt', ' dur1_traffic_opt', ' dist1_pes', ' dur1_traffic_pes']

#Convert the dataframes to CSV files
print("Found {} maps".format(maps_found))
map_df_nohead.to_csv('times.csv', index=False, header=False) 
map_df_head.to_csv('times_head.csv', index=False, header=True) 

print("Uploading game to www.paulmcevoy.ie")
#open an FTP session and upload the CSV and HTML
session = FTP('ftp.paulmcevoy.ie','p565545','Qxpr39b2B0')
file1 = open('times.csv','rb')                  # file to send
file2 = open('urouter.html','rb')                  # file to send

session.cwd('www')
pwd_dir = session.pwd()
session.storbinary('STOR times.csv', file1)     # send the file
session.storbinary('STOR urouter.html', file2)  # send the file

file1.close()                                   # close file and FTP
file2.close()                                   # close file and FTP

session.quit()

#get_maps()
   
    #And we're done!
