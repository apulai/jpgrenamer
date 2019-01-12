import glob
import exifread
import googlemaps
import re
import pickle
import json


# Google Geocoding API key
GOOGLE_API_KEY = ""
GOOGLE_API_KEY_FILE = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\keyfile.txt"

JPG_DIR = "C:\\Users\\PatrikJelinko\\PycharmProjects\\kepatnevezo\\kepek"
EXIF_DB_FILE = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\exif_db.db"
# based on https://gist.github.com/erans/983821


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
                d[ key] = item[key]
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
    date = item["EXIF DateTimeOriginal"].printable[:10]
    # Remove : from date
    date = re.sub(":","",date)
    # I think level 2 address was ok
    address=item["formatted_address_list"][2]
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
                item["myaddress"] = item["formatted_address_list"][2]
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


def filter_processed_files(file_list, db_file):
    """ Removes the items from file_list which have been processed already. """

    processed_list = read_list_from_file(EXIF_DB_FILE)

    # TODO: finish this method


#
# main
#
if __name__ == "__main__":
    read_api_key_from_file()
    filelist = findjpg(JPG_DIR)
    number_of_files_found = len(filelist)
    print("Found {} files to scan".format(number_of_files_found))

    filter_processed_files(filelist, EXIF_DB_FILE)
    print("Number of files to process after filtering: {}".format(len(filelist)))

    #Collect EXIF info from all JPG images
    taglist = gettags(filelist)

    #Filter down this list a bit, since I do not need this many
    # info
    # Might want to skip this step
    smalllist = filtertags(taglist)

    #Add decimal GPS info to the list items
    #the new tags will be mylat and mylon
    add_decimal_GPS(smalllist)

    add_google_maps_info(smalllist, GOOGLE_API_KEY)

    printtags(smalllist)

    # save_list_to_file(smalllist, EXIF_DB_FILE)

    # new_small_list = read_list_from_file(EXIF_DB_FILE)
    # printtags(new_small_list)
