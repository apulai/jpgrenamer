import glob
import exifread
import googlemaps
import re
import pickle
import time
from datetime import date
import datetime
import json


# Google Geocoding API key
GOOGLE_API_KEY = ""
#GOOGLE_API_KEY_FILE = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\keyfile.txt"
GOOGLE_API_KEY_FILE = "D:\\temp\\keyfile.txt"

#JPG_DIR = "C:\\Users\\PatrikJelinko\\PycharmProjects\\kepatnevezo\\kepek"
JPG_DIR = "D:\\temp\\kepek"

#EXIF_DB_FILE = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\exif_db.db"
EXIF_DB_FILE = "D:\\temp\\kepek\\exif_db.db"


def read_api_key_from_file():
    if GOOGLE_API_KEY_FILE != "":
        try:
            f = open(GOOGLE_API_KEY_FILE, "r")
        except IOError:
            print("IOError opening key file: " + GOOGLE_API_KEY_FILE + ". Using script's GOOGLE_API_KEY variable.")
        else:
            global GOOGLE_API_KEY
            GOOGLE_API_KEY = f.readline().rstrip()
            f.close()
            return GOOGLE_API_KEY

# Few functions to interpret exif data
# based on https://gist.github.com/erans/983821
def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


def _convert_to_degrees(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degrees in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)


def get_exif_location(exif_data):
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    """
    lat = None
    lon = None

    gps_latitude = _get_if_exist(exif_data, 'GPS GPSLatitude')
    gps_latitude_ref = _get_if_exist(exif_data, 'GPS GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data, 'GPS GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data, 'GPS GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degrees(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degrees(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon

    return lat, lon


#
# My code again
#

def distance(lat1,lon1,lat2,lon2):
    """
    :param lat1: Make sure it is in decimal format (not in radians)
    :param lon1: 
    :param lat2: 
    :param lon2: 
    :return: Returns the great circle distance between 2 points 
    """

    from math import sin, cos, sqrt, atan2, radians

    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return( distance )

def printabledatatime(tag):
    try:
        return tag["EXIF DateTimeOriginal"].printable
    except KeyError:
        return "1970:01:01 01:01:01"

def sort_tags_byexifdate(taglist):
    """
    Sort list of exif tags by EXIF attribute Original Date Time
    :param taglist:
    :return: modifies original list
    """
    taglist.sort(key=printabledatatime)
    return

def timedifference(tag1,tag2):
    """
    Return the timedelta of 2 tags
    :param tag1:
    :param tag2:
    :return: a timedelta object

    """
    a_date1 = printabledatatime(tag1)
    a_date2 = printabledatatime(tag2)

    a_date1 = re.sub(" ",":", a_date1)
    a_date2 = re.sub(" ",":", a_date2)
    l_date1 = re.split(":", a_date1)
    l_date2 = re.split(":", a_date2)

    date1 = datetime.datetime(int(l_date1[0]),int(l_date1[1]),int(l_date1[2]),int(l_date1[3]),int(l_date1[4]),int(l_date1[5]))
    date2 = datetime.datetime(int(l_date2[0]),int(l_date2[1]),int(l_date2[2]),int(l_date2[3]),int(l_date2[4]),int(l_date2[5]))
    timedelta = date1 - date2

    #return timedelta.total_seconds()
    return timedelta

def gettags(filelist):
    """input: list of files
    return: list of EXIF tags as dictionaries"""

    taglist = list()
    for filename in filelist:
        try:
            f = open(filename,"rb")
            tags = exifread.process_file(f)
            f.close()
            tags["myfilename"]=filename
            taglist.append(tags)
        except Exception as e:
            print("Warning: file cannot be opened. Exception: {}".format(filelist["filename"], e))
    return taglist


def printtags(taglist):
    """input: list of tags
    return: none"""

    #print(json.dumps(taglist, indent=4, ensure_ascii=False))
    #return

    for item in taglist:
        print("------")
        print("filename: {}".format(item["myfilename"]))
        print("------")
        for tag in item.keys():
            # if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote'):
                print("Key: {} , value: {}".format(tag, item[tag]))
            #if tag == "reverse_geocode":
            #    print(json.dumps(item["reverse_geocode"],indent=4, ensure_ascii=False))


def filtertags(taglist):
    """input: list of tags
    return: only the list of location related tags"""

    smalllist = list ()
    for item in taglist:
        d = dict()
        for key in item.keys():
            # Collect important tags
            if key in ('Image Model', 'Image Make', 'myfilename', 'EXIF DateTimeOriginal'):
                d[ key ] = item[key]
            # Collect all GPS related tags
            if "GPS" in key:
                d[ key ] = item[key]
        smalllist.append(d)

    return smalllist


def add_decimal_GPS(taglist):
    """Funcion we need to convert the strange EXIF Coordinates to decimals values
    so we can use them with google
    if we find the cooridnates we will add mylat and mylon to the item
    input list of EXIF tags"""
    for item in taglist:
        if "GPS GPSLongitude" in item.keys():
            if "GPS GPSLatitude" in item.keys():
                lat,lon = get_exif_location(item)
                item["mylat"]=lat
                item["mylon"]=lon
    return


def findjpg(folder):
    # List all jpg
    filelist = glob.glob(folder + '/**/*.jpg', recursive=True)
    return filelist


def propose_name(item):
    """
    Should propose a nice name
    Not working yet
    :param item: item from the taglist
    :return: a nice name, currently date_formattedaddress
    """
    try:
        date = item["EXIF DateTimeOriginal"].printable[:10]
        # Remove : from date
        date = re.sub(":","",date)
        # I think level 2 address was ok
    except KeyError:
        date = "19700101"

    try:
        address=item["formatted_address_list"][2]
    except KeyError:
        address=item["formatted_address_list"][0]

    return date+"_"+address


def add_google_maps_info(my_list, google_api_key):
    """ Enhances a list of EXIF info with the Google Maps API location information """

    gmaps = googlemaps.Client(key=google_api_key)
    for item in my_list:
        if "mylat" in item.keys() and "mylon" in item.keys():
            mylat = item["mylat"]
            mylon = item["mylon"]
            reverse_geocode_result = gmaps.reverse_geocode((mylat, mylon))
            if len(reverse_geocode_result) > 0:
                item["reverse_geocode"] = reverse_geocode_result
                item["formatted_address_list"] = list()
                for resultitem in reverse_geocode_result:
                    item["formatted_address_list"].append(resultitem["formatted_address"])
                # I think level 2 address was ok
                # Let's see that exists...
                try:
                    item["myaddress"] = item["formatted_address_list"][2]
                except KeyError:
                    item["myaddress"] = item["formatted_address_list"][0]
                item["rename_to"] = propose_name(item)


def save_list_to_file(my_list, my_file):
    """ Saves a list to file with the pickle module. Returns False if file can't be open for writing, True otherwise"""

    try:
        f = open(my_file, "wb")
    except IOError:
        print("Can't open file: {} for writing.".format(my_file))
        return False
    for i in my_list:
        pickle.dump(i, f, pickle.HIGHEST_PROTOCOL)
    f.close()
    return True


def read_list_from_file(my_file):
    """ Returns a list where items are read from a file with the pickle module. """

    my_list = []
    try:
        f = open(my_file, "rb")
    except IOError:
        print("Can't open file: {} for reading.".format(my_file))
        return []
    while True:
        try:
            i = pickle.load(f)
        except pickle.PickleError:
            print("Invalid file format, cannot read data.")
            break
        except EOFError:
            break
        else:
            my_list.append(i)
    f.close()
    return my_list


def join_pickle_dump_files(out_file, in_file1, in_file2):
    """ Copies the content of two pickle dump files into a single file. Returns True on success.
    TODO: This method requires heaps of memory, but lazy programmers don't care about memory consumption. Fix it!"""

    my_list1 = read_list_from_file(in_file1)
    my_list2 = read_list_from_file(in_file2)

    return save_list_to_file(my_list1+my_list2, out_file)


def remove_processed_files(file_list, processed_tag_list):
    """ Removes the items from file_list which have been processed already. """


    files_in_processed_list = list()
    for item in processed_tag_list:
        files_in_processed_list.append(item["myfilename"])

    for filename in files_in_processed_list:
        if filename in file_list:
            file_list.remove(filename)

    # TODO: Discuss this: https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
    # What are they speaking about?
    #for filename in file_list:
    #    for item in processed_tag_list:
    #        if filename == item["myfilename"]:
    #            file_list.remove(filename)

    return

#
# main
#
if __name__ == "__main__":

    read_api_key_from_file()

    # List the files in JPG_DIR
    filelist = findjpg(JPG_DIR)
    number_of_files_found = len(filelist)
    print("Found {} files to scan".format(number_of_files_found))

    # Load the database file
    # We have data in this DB from the files scanned
    # earlier
    processed_tag_list = read_list_from_file(EXIF_DB_FILE)

    # We will narrow down the list of files
    # so we will check only new files not found in our DB
    remove_processed_files(filelist, processed_tag_list)
    print("Number of files to process after filtering: {}".format(len(filelist)))

    #Collect EXIF info from all JPG images
    taglist = gettags(filelist)

    #Filter down this list a bit, since I do not need this many info
    # Might want to skip this step
    smalllist = filtertags(taglist)

    #Add decimal GPS info to the list items
    #the new tags will be mylat and mylon
    add_decimal_GPS(smalllist)
    # Log on to google geomap API
    # to collect "address" information based on GPS coordinates
    add_google_maps_info(smalllist, GOOGLE_API_KEY)

    #Check
    printtags(smalllist)

    # We will have to concatenate
    # the list of fresh files
    # with the list of already processed files
    if( len(processed_tag_list) == 0):
        new_processed_list = smalllist
    else:
        new_processed_list = processed_tag_list + smalllist

    # quick sort by date
    sort_tags_byexifdate(new_processed_list)

    # And we will save info back to
    # the database
    save_list_to_file(new_processed_list, EXIF_DB_FILE)

    #
    # Test for computing time delta
    #
    tag0 = new_processed_list[1]
    for tag in new_processed_list:
        delta=timedifference(tag0,tag)
        print(" Difference is {}(s)".format(delta))

    exit(0)
    printtags(new_processed_list)

    #
    # Test for computing distance of 2 coordintates delta
    #
    print("Distance: {} km".format(distance(-33.84266944444445,151.17260833333333,47.63259166666667,19.142563888888887)))