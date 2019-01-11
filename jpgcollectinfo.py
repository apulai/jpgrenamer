import glob
import exifread
import googlemaps
import re
import json

#Google Geocoding API key
KEY = ''
KEY_FILE = "D:\\temp\\keyfile.txt"

# based on https://gist.github.com/erans/983821


def read_api_key_from_file():
    if KEY_FILE != "":
        try:
            f = open(KEY_FILE, "r")
        except IOError:
            print("IOError opening key file: " + KEY_FILE + ". Using script's KEY variable.")
        else:
            global KEY
            KEY = f.readline().rstrip()
            f.close()


def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
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
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon

    return lat, lon


def gettags(filelist):
    "input: list of files"
    "return: list of EXIF tags as dictionaries"

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
    "input: list of tags"
    "return: none"

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
    "input: list of tags"
    "return: only the list of location related tags"

    smalllist = list ()
    for item in taglist:
        d = dict()
        for key in item.keys():
            # Collect important tags
            if key in ('Image Model', 'Image Make', 'myfilename', 'EXIF DateTimeOriginal'):
                d[ key ] = item[key]
            # Collect all GPS related tags
            if "GPS" in key:
                d[ key] = item[key]
        smalllist.append(d)

    return smalllist


def add_decimal_GPS(taglist):
    "Funcion we need to convert the strange EXIF Coordinates to decimals values"
    "so we can use them with google"
    "if we find the cooridnates we will add mylat and mylon to the item"
    "input list of EXIF tags"
    for item in taglist:
        if "GPS GPSLongitude" in item.keys():
            if "GPS GPSLatitude" in item.keys():
                lat,lon = get_exif_location(item)
                item["mylat"]=lat
                item["mylon"]=lon
    # TODO: miert modositja az eredeti listat a fuggveny?
    return


def findjpg(folder):
    # List all jpg
    filelist = glob.glob(folder + '/**/*.jpg', recursive=True)
    return filelist


def propose_name(item):
    date = item["EXIF DateTimeOriginal"].printable[:10]
    # Remove : from date
    date = re.sub(":","",date)
    # I think level 2 address was ok
    address=item["formatted_address_list"][2]
    return date+"_"+address

#
# main
#

read_api_key_from_file()
filelist = findjpg("C:\\Users\\PatrikJelinko\\PycharmProjects\\kepatnevezo\\kepek")
number_of_files_found = len(filelist)
print("Found {} files to scan".format(number_of_files_found))

#Collect EXIF info from all JPG images
taglist=gettags(filelist)

#Filter down this list a bit, since I do not need this many
# info
# Might want to skip this step
smalllist=filtertags(taglist)

#Add decimal GPS info to the list items
#the new tags will be mylat and mylon
add_decimal_GPS(smalllist)

#
# Query google for info
gmaps = googlemaps.Client(key=KEY)
for item in smalllist:
    if "mylat" in item.keys() and "mylon" in item.keys():
        mylat=item["mylat"]
        mylon=item["mylon"]
        reverse_geocode_result = gmaps.reverse_geocode((mylat, mylon))
        if( len(reverse_geocode_result) > 0):
            item["reverse_geocode"] = reverse_geocode_result
            item["formatted_address_list"] = list()
            for resultitem in reverse_geocode_result:
                item["formatted_address_list"].append(resultitem["formatted_address"])
            # I think level 2 address was ok
            item["myaddress"]=item["formatted_address_list"][2]
            item["rename_to"]=propose_name(item)

printtags(smalllist)

import pickle
""" A pickle.dumps serializalja a dict objecttet, most eppen egy string-be (.dump file-ba)"""
x = pickle.dumps(smalllist[0]) #`, pickle.HIGHEST_PROTOCOL)

""" A pickle.loads meg visszaalakitja, es igy nez ki hogy megratja az ifdtag-eket"""
y = pickle.loads(x)

"""

Python's parameter passing acts a bit different than the languages you're probably used to. Instead of having explicit 
pass by value and pass by reference semantics, python has pass by name. You are essentially always passing the object 
itself, and the object's mutability determines whether or not it can be modified. Lists and Dicts are mutable objects. 
Numbers, Strings, and Tuples are not.

You are passing the dictionary to the function, not a copy. Thus when you modify it, you are also modifying the original 
copy.
"""