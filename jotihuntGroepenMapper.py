""" Author: Lex Bosch
    Date: 14-10-2019
    Version: 1.1
    Function: Script that gahters the information about all the groups that participate in the jotihunt
            go to https://www.google.com/maps/d/u/0/?hl=en to create a map for the csv file
"""

import urllib.request
import json
import xml.etree.ElementTree as ET


class create_kml_file:
    def __init__(self):
        self.colorlist = ["501400FF", "5014F0FF", "5000FF14", "507800F0", "501478E6", "50FFFFFF", "50000000"]
        self.colorcounter = 0
        self.style_list = []
        self.full = ET.Element('kml')
        self.full.set("xmlns", "http://www.opengis.net/kml/2.2")
        self.docu = ET.SubElement(self.full, 'Document')
        naam = ET.SubElement(self.docu, "name")
        naam.text = "Jotihunt 2019 - Deelnemende Groepen"

    def get_xml(self):
        return ET.tostring(self.full)


    def add_group(self, group_name, group_lon, group_lan, district):
        group_mark = ET.SubElement(self.docu, "Placemark")
        group_name_el = ET.SubElement(group_mark, "name")
        group_name_el.text = group_name
        group_style_el = ET.SubElement(group_mark, "styleUrl")
        group_style_el.text = "#"+district.replace(".","") + "_style"
        group_point_el = ET.SubElement(group_mark, "Point")
        group_coord_el = ET.SubElement(group_point_el, "coordinates")
        group_coord_el.text = "{0},{1},0".format(group_lon, group_lan)


    def add_style(self, district):
        if not district in self.style_list:
            main_style = ET.SubElement(self.docu, "Style")
            main_style.set("id",district.replace(".","")+"_style")
            icon_style = ET.SubElement(main_style, "IconStyle")
            ET.SubElement(icon_style, "color").text = self.colorlist[self.colorcounter]
            self.colorcounter += 1
            ET.SubElement(icon_style, "scale").text = "1"
            subicon_style = ET.SubElement(icon_style, "Icon")
            ET.SubElement(subicon_style, "href").text = "http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png"
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

    def get_location_info(self):
        """Gathers information regarding the creation of the csv file

        :return: returns a csv string containing the lon, lan and name of a group
        """
        export_info = "{},{},{}".format(self.longtitute, self.latitute, self.group_name)
        return export_info

    def get_better_location_info(self):
        return self.group_name, self.longtitute, self.latitute, self.area


    def get_district(self):
        """Getting for group area

        :return: group district
        """
        return self.area.lower()


def main():
    """Main for the application

    :return: Creates csv
    """
    information_dictionary = gather_online_info()
    group_list = create_group_objects(information_dictionary)
    csv_string = create_csv(group_list)
    write_csv(csv_string)


def gather_online_info():
    """Uses the Jotihunt api to gather information about the participating groups of the jotihunt

    :return: dictionary containing information of the groups
    """
    contents = urllib.request.urlopen("https://jotihunt.net/api/1.0/deelnemers").read()
    return json.loads(contents)


def create_group_objects(input_dictionary):
    """ Creates list with objects of the participating groups

    :param input_dictionary: dictionary gathered from the jotihunt api
    :return: returns list with group objects
    """
    group_list = []
    for group in input_dictionary["data"]:
        if group["naam"] != "naam":
            group_list.append(Groups(group))
    return group_list


def create_csv(group_list):
    """Creates string in csv format. Checks for area to parse.

    :param group_list: List containing group objects
    :return: returns string in csv format
    """
#    group_list = choose_district(group_list)
    csv_file = "lon, lat, title\n"
    kml_file = create_kml_file()
    for group in group_list:
        var1, var2, var3, var4 = group.get_better_location_info()
        kml_file.add_group(var1, var2, var3, var4)
        kml_file.add_style(var4)



    return kml_file.get_xml().decode("utf-8")


def choose_district(group_list):
    """Creates a list of all distinct districts. If mulitple districts are present, a prompt is given to choose which
    district to export.

    :param group_list: List containing group objects
    :return: returns a possibly updated list of group objects
    """
    possible_districts = {group.get_district for group in group_list}
    if len(possible_districts) <= 1:
        return group_list
    else:
        print("Mulitple districts have been found. Please enter the name of the disctrict you would like"
              "to process, leave blank to parse every district. possible districts are;")
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
    chosen_district = input("please write the name of the district")
    if chosen_district.lower() not in possible_districts and not "":
        print("\nDistrict not given correctly. Please try agian")
        input_district(possible_districts)
    else:
        return chosen_district


def write_csv(csv_string):
    """write csv file

    :param csv_string: string in csv format
    :return: csv file
    """
    with open("jotihunt_location.kml", "w") as export_file:
        export_file.write(csv_string)


if __name__ == '__main__':
    main()
