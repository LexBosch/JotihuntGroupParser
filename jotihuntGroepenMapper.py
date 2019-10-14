""" Author: Lex Bosch
    Date: 14-10-2019
    Function: Script that gahters the information about all the groups that participate in the jotihunt
            go to https://www.google.com/maps/d/u/0/?hl=en to create a map for the csv file
"""

import urllib.request
import json


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

    def get_district(self):
        """Getting for group area

        :return: group district
        """
        return self.area


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
    group_list = choose_district(group_list)
    csv_file = "lon, lat, title\n"
    for group in group_list:
        csv_file += group.get_location_info() + "\n"
    return csv_file


def choose_district(group_list):
    """Creates a list of all distinct districts. If mulitple districts are present, a prompt is given to choose which
    district to export.

    :param group_list: List containing group objects
    :return: returns a possibly updated list of group objects
    """
    possible_districts = []
    for group in group_list:
        if group.get_district() not in possible_districts:
            possible_districts.append(group.get_district().lower())
    if len(possible_districts) <= 1:
        return group_list
    else:
        print("Mulitple districts have been found. Please enter the name of the disctrict you would like"
              "to process, leave blank to parse every district. possible districts are;")
        chosen_district = input_district(possible_districts)
        new_group_list = []
        if chosen_district == "":
            return group_list
        for group in group_list:
            if group.get_district() == chosen_district:
                new_group_list.append(group)
        return new_group_list


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
    with open("jotihunt_location.csv", "w") as export_file:
        export_file.write(csv_string)


if __name__ == '__main__':
    main()
