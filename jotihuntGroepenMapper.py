""" Author: Lex Bosch
    Date: 14-10-2019
    Version: 1.2
    Function: Script that gathers the information about all the groups that participate in the jotihunt
            go to https://www.google.com/maps/d/u/0/?hl=en to create a map for the kml file
"""

import urllib.request
import json
import xml.etree.ElementTree as EleTree


class CreateKmlFile:
    """Builds an KML Object containing all information needed to create elements on the maps    
    """
    def __init__(self):
        """ Initiates object
            colorlist contains a few colors that are pretty. Each style gets it's own pretty color
        
        """
        self.colorlist = ["501400FF", "5014F0FF", "5000FF14", "507800F0", "501478E6", "50FFFFFF", "50000000"]
        self.colorcounter = 0
        self.style_list = []
        self.full = EleTree.Element('kml')
        self.full.set("xmlns", "http://www.opengis.net/kml/2.2")
        self.docu = EleTree.SubElement(self.full, 'Document')
        naam = EleTree.SubElement(self.docu, "name")
        naam.text = "Jotihunt 2019 - Deelnemende Groepen"

    def get_xml(self):
        """Return String of the KML
        
        :return: KML in string format
        """
        return EleTree.tostring(self.full).decode("utf-8")

    def add_group(self, group_name, group_lon, group_lan, district):
        """ Adds a group to the markup. Gives it its style depending on the district given by the api
        
        :param group_name: Name of the group, used as the elements title
        :param group_lon: used for gps calculation
        :param group_lan: also used for gps calculation
        :param district: District the group is in, used for its style
        :return: returns NOTHING. Just adds a few sub elements
        """
        group_mark = EleTree.SubElement(self.docu, "Placemark")
        group_name_el = EleTree.SubElement(group_mark, "name")
        group_name_el.text = group_name
        group_style_el = EleTree.SubElement(group_mark, "styleUrl")
        group_style_el.text = "#" + district.replace(".", "") + "_style"
        group_point_el = EleTree.SubElement(group_mark, "Point")
        group_coord_el = EleTree.SubElement(group_point_el, "coordinates")
        group_coord_el.text = "{0},{1},0".format(group_lon, group_lan)

    def add_style(self, district):
        """ Adds a style to the given district if the given district doesn't already have a have a style.
            The district is assigned a color depending on the list at the __init__ and the counter. 
        
        :param district: District name of the group
        :return: returns NOTTHING
        """
        if district not in self.style_list:
            main_style = EleTree.SubElement(self.docu, "Style")
            main_style.set("id", district.replace(".", "") + "_style")
            icon_style = EleTree.SubElement(main_style, "IconStyle")
            EleTree.SubElement(icon_style, "color").text = self.colorlist[self.colorcounter]
            self.colorcounter += 1
            EleTree.SubElement(icon_style, "scale").text = "1"
            subicon_style = EleTree.SubElement(icon_style, "Icon")
            EleTree.SubElement(subicon_style, "href").text \
                = "http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png"
            self.style_list.append(district)


class Groups:
    def __init__(self, group_dictionary):
        """Class containing the information regarding groups participating the JotiHunt

        :param group_dictionary: dictionary containing all information about groups participating
        """
        self.group_id = group_dictionary["id"]
        self.group_name = group_dictionary["naam"]
        self.team_name = group_dictionary["teamnaam"]
        self.latitute = group_dictionary["lat"]
        self.longtitute = group_dictionary["long"]
        self.area = group_dictionary["deelgebied"]

    def get_better_location_info(self):
        """ Returns some information about the object.

        :return: Look at the variable names, it's not hard
        """
        return self.group_name, self.longtitute, self.latitute, self.area

    def get_district(self):
        """Getting for group area

        :return: group district
        """
        return self.area.lower()


def main():
    """Main for the application

    :return: Creates kml
    """
    try:
        information_dictionary = gather_online_info()
        group_list = create_group_objects(information_dictionary)
        kml_string = create_kml(group_list)
        write_kml(kml_string)
        print("The process has compoleted succesfully.\nA file has been created in the same folder as this script")
        input("Press enter to leave to program")
    except urllib.error.URLError:  # it's not a error, pycharm
        print("Make sure you have an stable internet connection")
        input("Press enter to leave to program")


def gather_online_info():
    """Uses the Jotihunt api to gather information about the participating groups of the jotihunt

    :return: dictionary containing information of the groups
    """
    print("Featching data.\n")
    contents = urllib.request.urlopen("https://jotihunt.net/api/1.0/deelnemers").read()
    print("Data gathered.\n")
    return json.loads(contents)


def create_group_objects(input_dictionary):
    """ Creates list with objects of the participating groups

    :param input_dictionary: dictionary gathered from the jotihunt api
    :return: returns list with group objects
    """
    group_list = [Groups(group) for group in input_dictionary["data"] if group["naam"] != "naam"]
    return group_list


def create_kml(group_list):
    """Creates string in kml format. Checks for area to parse.

    :param group_list: List containing group objects
    :return: returns string in kml format
    """
    group_list = choose_district(group_list)
    kml_file = CreateKmlFile()
    for group in group_list:
        group_name, lon, lan, district = group.get_better_location_info()
        kml_file.add_group(group_name, lon, lan, district)
        kml_file.add_style(district)
    return kml_file.get_xml()


def choose_district(group_list):
    """Creates a list of all distinct districts. If mulitple districts are present, a prompt is given to choose which
    district to export.

    :param group_list: List containing group objects
    :return: returns a possibly updated list of group objects
    """
    possible_districts = set([group.get_district() for group in group_list])
    if len(possible_districts) <= 1:
        return group_list
    else:
        print("Mulitple districts have been found. Please enter the name of the disctrict you would like\n"
              "to process, leave blank to parse every district. possible districts are;\n")
        chosen_district = input_district(possible_districts)
        if chosen_district != "":
            group_list = [group for group in group_list if group.get_district() == chosen_district]
        return group_list


def input_district(possible_districts):
    """Allow the user to choose which district to export. When the input isnt found within the choices, it promps agian.

    :param possible_districts: list of possible districts
    :return: returns the chosen district
    """
    print(", ".join(possible_districts))
    chosen_district = input("please write the name of the district\n")

    if chosen_district.lower() not in possible_districts and chosen_district != "":
        print("\nDistrict not given correctly. Please try agian")
        input_district(possible_districts)
    else:
        return chosen_district


def write_kml(kml_string):
    """Writes kml file

    :param kml_string: string in kml format
    :return: klm file
    """
    with open("jotihunt_location.kml", "w") as export_file:
        export_file.write(kml_string)


if __name__ == '__main__':
    main()
