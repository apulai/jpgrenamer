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
google_api_key_file = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\keyfile.txt"
#google_api_key_file = "D:\\temp\\keyfile.txt"

JPG_DIR = "C:\\Users\\PatrikJelinko\\PycharmProjects\\kepatnevezo\\kepek"
#JPG_DIR = "D:\\temp\\kepek"

EXIF_DB_FILE = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\exif_db.db"
#EXIF_DB_FILE = "D:\\temp\\kepek\\exif_db.db"

class exiflist:
    def __init__(self, jpg_dir, exif_dbfile, google_api_key_file):
        """
        Setup a processed_tag_list and an unprocessed_tag_list
        Typical next step is to clear the unprocessed_tag_list by asking google data

        :param jpg_dir: scan this folder for jpg files
        :param exif_dbfile: load this pickle db
        :param google_api_key_file: load this file for Google API requests
        """

        self.processed_tag_list = None
        self.unprocessed_tag_list = None
        self.google_api_key = None
        self.google_api_key_file = google_api_key_file

        self.exif_dbfile = exif_dbfile
        self.google_api_key = self._read_api_key_from_file()

        # List the files in JPG_DIR
        filelist = self._findjpg(jpg_dir)
        number_of_files_found = len(filelist)
        print("Found {} files to scan".format(number_of_files_found))

        # Load the database file
        # We have data in this DB from the files scanned
        # earlier
        self.processed_tag_list = self._read_list_from_file(exif_dbfile)

        # We will narrow down the list of files
        # so we will check only new files not found in our DB
        self._remove_processed_files(filelist, self.processed_tag_list)
        print("Number of files to process after filtering: {}".format(len(filelist)))

        # Collect EXIF info from all JPG images
        self.unprocessed_tag_list = self._collecttagsfromfile(filelist)

        # Filter down this list a bit, since I do not need this many info
        # Might want to skip this step
        self.unprocessed_tag_list = self._filtertags(self.unprocessed_tag_list)

        # Add decimal GPS info to the list items
        # the new tags will be mylat and mylon
        self._add_decimal_GPS(self.unprocessed_tag_list)

    def __iter__(self):
        """
        This class is iterable.
        We will iterate the processed tag list
        :return:
        """
        return iter(self.processed_tag_list)

    def add_google_map_info_for_unprocessedtags(self):
        """
        Collect info for the unprocessed part of the exif tags
        Once read join processed and unprocessed list
        Clear unprocessed list
        :return:
        """
        # Log on to google geomap API
        # to collect "address" information based on GPS coordinates
        self._add_google_maps_info(self.unprocessed_tag_list, self.google_api_key)

        # We will have to concatenate
        # the list of fresh files
        # with the list of already processed files
        if len(self.processed_tag_list) == 0:
            new_processed_list = self.unprocessed_tag_list
        else:
            new_processed_list = self.processed_tag_list + self.unprocessed_tag_list

        # quick sort by date
        self._sort_tags_byexifdate(new_processed_list)

        # Practically this is the return value
        self.processed_tag_list = new_processed_list
        self.unprocessed_tag_list=[]

    def get_processed_tag(self, nth):
        """
        Return the nth item of the processed list
        :param idx:
        :return:
        """
        try:
            tag = self.processed_tag_list[nth]
        except IndexError:
            tag = None
        return tag

    def get_unprocessed_tag(self, nth):
        """
        Return the nth item of the processed list
        :param idx:
        :return:
        """
        try:
            tag = self.unprocessed_tag_list[nth]
        except IndexError:
            tag = None
        return tag

    def _read_api_key_from_file(self):
        if self.google_api_key_file != "":
            try:
                f = open(self.google_api_key_file, "r")
            except IOError:
                print("IOError opening key file: " + self.google_api_key_file + ". Using script's google_api_key variable.")
            else:
                self.google_api_key = f.readline().rstrip()
                f.close()
                return self.google_api_key

    # Few functions to interpret exif data
    # based on https://gist.github.com/erans/983821
    def _get_if_exist(self, data, key):
        if key in data:
            return data[key]

        return None

    def _convert_exif_raw_gps_to_degrees(self, value):
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

    def _get_exif_location(self, exif_data):
        """
        Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
        """
        lat = None
        lon = None

        gps_latitude = self._get_if_exist(exif_data, 'GPS GPSLatitude')
        gps_latitude_ref = self._get_if_exist(exif_data, 'GPS GPSLatitudeRef')
        gps_longitude = self._get_if_exist(exif_data, 'GPS GPSLongitude')
        gps_longitude_ref = self._get_if_exist(exif_data, 'GPS GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = self._convert_exif_raw_gps_to_degrees(gps_latitude)
            if gps_latitude_ref.values[0] != 'N':
                lat = 0 - lat

            lon = self._convert_exif_raw_gps_to_degrees(gps_longitude)
            if gps_longitude_ref.values[0] != 'E':
                lon = 0 - lon

        return lat, lon

    def _printabledatatime(self, tag):
        try:
            return tag["EXIF DateTimeOriginal"].printable
        except KeyError:
            return "1970:01:01 01:01:01"

    def sort_tags_byexifdate(self):
        """
        public to sort list by exifdate
        :return:
        """
        self._sort_tags_byexifdate(self.processed_tag_list)

    def _sort_tags_byexifdate(self, taglist):
        """
        Sort list of exif tags by EXIF attribute Original Date Time
        :param taglist:
        :return: modifies original list
        """
        taglist.sort(key=self._printabledatatime)
        return

    #TODO: Ez itt még nagyon szar
    def timedifference(self, tag1, tag2):
        """
        Return the timedelta of 2 tags
        :param tag1:
        :param tag2:
        :return: a timedelta object

        """
        a_date1 = self._printabledatatime(tag1)
        a_date2 = self._printabledatatime(tag2)

        a_date1 = re.sub(" ",":", a_date1)
        a_date2 = re.sub(" ",":", a_date2)
        l_date1 = re.split(":", a_date1)
        l_date2 = re.split(":", a_date2)

        date1 = datetime.datetime(int(l_date1[0]),int(l_date1[1]),int(l_date1[2]),int(l_date1[3]),int(l_date1[4]),int(l_date1[5]))
        date2 = datetime.datetime(int(l_date2[0]),int(l_date2[1]),int(l_date2[2]),int(l_date2[3]),int(l_date2[4]),int(l_date2[5]))
        timedelta = date1 - date2

        #return timedelta.total_seconds()
        return timedelta

    def _collecttagsfromfile(self, filelist):
        """input: list of files
        return: list of EXIF tags as dictionaries"""

        taglist = list()
        for filename in filelist:
            try:
                f = open(filename, "rb")
                tags = exifread.process_file(f)
                f.close()
                tags["myfilename"] = filename
                taglist.append(tags)
            except Exception as e:
                print("Warning: file cannot be opened. Exception: {}".format(filelist["filename"], e))
        return taglist

    def printtags(self):
        self.printtags(self.processed_tag_list)

    def printtags(self, taglist):
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

    def get_processed_tags(self):
        return self.processed_tag_list

    def get_unprocessed_tags(self):
        return self.unprocessed_tag_list

    def put_processed_tags(self,taglist):
        self.processed_tag_list=taglist

    def put_unprocessed_tags(self,taglist):
        self.unprocessed_tag_list=taglist

    def _filtertags(self, taglist):
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

    def _add_decimal_GPS(self, taglist):
        """Funcion we need to convert the strange EXIF Coordinates to decimals values
        so we can use them with google
        if we find the cooridnates we will add mylat and mylon to the item
        input list of EXIF tags"""
        for item in taglist:
            if "GPS GPSLongitude" in item.keys():
                if "GPS GPSLatitude" in item.keys():
                    lat,lon = self._get_exif_location(item)
                    item["mylat"]=lat
                    item["mylon"]=lon
        return

    def _findjpg(self, folder):
        # List all jpg
        filelist = glob.glob(folder + '/**/*.jpg', recursive=True)
        return filelist

    def propose_name(self, item):
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

    def _add_google_maps_info(self, my_list, google_api_key):
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
                    item["rename_to"] = self.propose_name(item)

    def save_db(self):
        self.save_list_to_file(self.processed_tag_list,self.exif_dbfile)

    def save_list_to_file(self, my_list, my_file):
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

    def load_db(self):
        self._read_list_from_file(self.exif_dbfile)

    def _read_list_from_file(self, my_file):
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

    def join_pickle_dump_files(self, out_file, in_file1, in_file2):
        """ Copies the content of two pickle dump files into a single file. Returns True on success.
        TODO: This method requires heaps of memory, but lazy programmers don't care about memory consumption. Fix it!"""

        my_list1 = self._read_list_from_file(in_file1)
        my_list2 = self._read_list_from_file(in_file2)

        return self._save_list_to_file(my_list1+my_list2, out_file)

    def _remove_processed_files(self, file_list, processed_tag_list):
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

    def _save_list_to_file(self):
        self._save_list_to_file(self.processed_tag_list, self.exif_dbfile)
#
#
# Not in class
# These do not really fit well into my class

# So they remain in module


def get_distance(lat1, lon1, lat2, lon2):
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

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


#
# main
#
if __name__ == "__main__":

    workingset1 = exiflist(JPG_DIR, EXIF_DB_FILE, google_api_key_file)

    workingset1.printtags(workingset1.unprocessed_tag_list)

    #Add google part
    workingset1.add_google_map_info_for_unprocessedtags()

    #Check
    print("Unprocessed tags")
    workingset1.printtags(workingset1.unprocessed_tag_list)

    print("Processed tags")
    workingset1.printtags(workingset1.processed_tag_list)

    # quick sort by date
    workingset1.sort_tags_byexifdate()

    # And we will save info back to
    # the database
    workingset1.save_db()

    exit()
    #
    # Test for computing time delta
    #
    #TODO: bele kéne tenni valami iterálhatót, ami visszaadja a dolgokat
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