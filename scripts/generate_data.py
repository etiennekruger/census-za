#!/usr/bin/env python

"""
Process xls files from the 2001 census and produce csvs
This process is individual to each indicator
"""

import sys
import json
import csv
import os
import xlrd

class Province(object):
    provinces = {}

    @classmethod
    def add_province(cls, province):
        if not province in cls.provinces:
            cls.provinces[province] = Province(province)
        return cls.provinces[province]

    def __init__(self, province):
        self._province = province

    def __str__(self):
        return self._province

class District(object):
    districts = {}
    @classmethod
    def add_district(cls, province, dc_code, dc_name):
        if not dc_code in cls.districts:
            cls.districts[dc_code] = District(province, dc_code, dc_name)
        return cls.districts[dc_code]

    def __init__(self, province, dc_code, dc_name):
        self._province = province
        self._dc_code = dc_code
        self._dc_name = dc_name

    def __str__(self):
        return self._dc_name

class Municipality(object):
    municipalities = {}
    @classmethod
    def add_municipality(cls, district, munic_code, munic_name):
        if not munic_code in cls.municipalities:
            cls.municipalities[munic_code] = Municipality(district, munic_code, munic_name)
        return cls.municipalities[munic_code]

    def __init__(self, district, munic_code, munic_name):
        self._district = district
        self._munic_code = munic_code
        self._munic_name = munic_name

    def __str__(self):
        return self._munic_name

class MainPlace(object):
    mainplaces = {}
    @classmethod
    def add_mainplace(cls, municipality, mp_code, mp_place):
        if not mp_code in cls.mainplaces:
            cls.mainplaces[mp_code] = MainPlace(municipality, mp_code, mp_place)
        return cls.mainplaces[mp_code]

    def __init__(self, municipality, mp_code, mp_place):
        self._municipality = municipality
        self._mp_code = mp_code
        self._mp_place = mp_place

    def __str__(self):
        return self._mp_place

class SubPlace(object):
    subplaces = {}
    @classmethod
    def add_subplace(cls, mainplace, sp_code, sp_place):
        if not sp_code in cls.subplaces:
            cls.subplaces[sp_code] = SubPlace(mainplace, sp_code, sp_place)
        return cls.subplaces[sp_code]

    def __init__(self, mainplace, sp_code, sp_place):
        self._mainplace = mainplace
        self._sp_code = int(sp_code)
        self._sp_place = sp_place

    def __str__(self):
        return self._sp_place

class FileReader(object):
    @staticmethod
    def xls2val(arr):
        return [x.value for x in arr]

    def __init__(self, filename):
        book = xlrd.open_workbook(filename)
        self._sheet = book.sheet_by_index(0)
        self._headers = FileReader.xls2val(self._sheet.row(4))

    @property
    def rows(self):
        for row_num in range(5, self._sheet.nrows):
            row = FileReader.xls2val(self._sheet.row(row_num))
            datum = dict(zip(self._headers, row))
            # Stop processing when we reach a blank line. 
            # The files contain explanatory text at the bottom
            if datum["Province"] == "":
                break
            yield datum

def dump_indicator(indicator):
    fp = open(os.path.join("output", indicator) + ".csv", "w")
    writer = csv.writer(fp)
    for subplace in SubPlace.subplaces.values():
        val = getattr(subplace, indicator) if hasattr(subplace, indicator) else 0
        writer.writerow([subplace._sp_code, val])
    fp.close()

def dump_indicator_and_stats(indicator, stats_indicator):
    dump_indicator(indicator)

    fp = open(os.path.join("output", indicator) + ".json", "w")
    count = 0
    values = []
    for subplace in SubPlace.subplaces.values():
        count += 0
        val = getattr(subplace, stats_indicator) if hasattr(subplace, stats_indicator) else 0
        values.append(val)
    stats = {
        "name" : stats_indicator,
        "min" : min(values),
        "max" : max(values),
        "mean" : sum(values) / len(values),
    }

    fp.write(json.dumps(stats, indent=4))
    fp.close()
    

def init_database():
    filename = os.path.join("data", "Census 01_Sub Place_Density.xls")
    fr = FileReader(filename)
    for datum in fr.rows:
        province = Province.add_province(datum["Province"])
        district = District.add_district(province, datum["DC_Code"], datum["DC_Name"])
        municipality = Municipality.add_municipality(district, datum["Munic_Code"], datum["Munic_Name"])
        mainplace = MainPlace.add_mainplace(municipality, datum["MP_Code"], datum["Main_Place"])
        subplace = SubPlace.add_subplace(mainplace, datum["SP_Code"], datum["Sub_Place"])

        subplace.num_people = datum["Number of people in sub-place"]
        subplace.num_households = datum["Number of households in sub-place"]
        subplace.area = datum["Sub-place Area (km2)"]
        

def func_density(filename):
    """
    Population density by household and by person
    """
    fr = FileReader(os.path.join("data", filename))

    hh_densities = []
    pr_densities = []
    
    for datum in fr.rows:
        hh_densities.append(datum["Density (households  per km2)"])
        pr_densities.append(datum["Density (people per km2)"])
        subplace = SubPlace.subplaces[datum["SP_Code"]]
        subplace.hh_density = datum["Density (households  per km2)"]
        subplace.pr_density = datum["Density (people per km2)"]

    max_hh = max(hh_densities)
    max_pr = max(pr_densities)

    for subplace in SubPlace.subplaces.values():
        subplace.norm_hh_density = subplace.hh_density / max_hh
        subplace.norm_pr_density = subplace.pr_density / max_pr

    dump_indicator_and_stats("norm_hh_density", "hh_density")
    dump_indicator_and_stats("norm_pr_density", "pr_density")


def func_toilet(filename):
    """
    """
    fr = FileReader(os.path.join("data", filename))

    for datum in fr.rows:
        subplace = SubPlace.subplaces[datum["SP_Code"]]
        subplace.toilet_flush = datum["Flush toilet (connected to sewerage system)"] 
        subplace.toilet_septic = datum["Flush toilet (with septic tank)"] 
        subplace.toilet_chemical = datum["Chemical toilet"] 
        subplace.toilet_pitlatrine_ventilation = datum["Pit latrine with ventilation (VIP)"] 
        subplace.toilet_pitlatrine_no_ventilation = datum["Pit latrine without ventilation"] 
        subplace.toilet_bucket = datum["Bucket latrine"] 
        subplace.toilet_none = datum["None"] 

        as_perc = lambda x : x / subplace.num_households

        try:
            subplace.perc_toilet_flush = as_perc(subplace.toilet_flush)
            subplace.perc_toilet_septic = as_perc(subplace.toilet_septic)
            subplace.perc_toilet_chemical = as_perc(subplace.toilet_chemical)
            subplace.perc_toilet_pitlatrine_ventilation = as_perc(subplace.toilet_pitlatrine_ventilation)
            subplace.perc_toilet_pitlatrine_no_ventilation = as_perc(subplace.toilet_pitlatrine_no_ventilation)
            subplace.perc_toilet_bucket = as_perc(subplace.toilet_bucket)
            subplace.perc_toilet_none = as_perc(subplace.toilet_none)
        except ZeroDivisionError:
            pass

    dump_indicator_and_stats("perc_toilet_flush", "toilet_flush")
    dump_indicator_and_stats("perc_toilet_septic", "toilet_septic")
    dump_indicator_and_stats("perc_toilet_chemical", "toilet_chemical")
    dump_indicator_and_stats("perc_toilet_pitlatrine_ventilation", "toilet_pitlatrine_ventilation")
    dump_indicator_and_stats("perc_toilet_pitlatrine_no_ventilation", "toilet_pitlatrine_no_ventilation")
    dump_indicator_and_stats("perc_toilet_bucket", "toilet_bucket")
    dump_indicator_and_stats("perc_toilet_none", "toilet_none")

def func_telephone(filename):
    """
    """
    fr = FileReader(os.path.join("data", filename))

    for datum in fr.rows:
        subplace = SubPlace.subplaces[datum["SP_Code"]]
        subplace.phone_and_cell = datum["Telephone in dwelling and cell-phone"] 
        subplace.phone_only = datum["Telephone in dwelling only"] 
        subplace.phone_cell_only = datum["Cell-phone only"] 
        subplace.phone_neighbour = datum["At a neighbour nearby"] 
        subplace.phone_public = datum["At a public telephone nearby"] 
        subplace.phone_nearby = datum["At another location nearby"] 
        subplace.phone_not_nearby = datum["At another location; not nearby"] 
        subplace.phone_none = datum["No access to a telephone"] 

        as_perc = lambda x : x / subplace.num_households

        try:
            subplace.perc_phone_and_cell = as_perc(subplace.phone_and_cell)
            subplace.perc_phone_only = as_perc(subplace.phone_only)
            subplace.perc_phone_cell_only = as_perc(subplace.phone_cell_only)
            subplace.perc_phone_neighbour = as_perc(subplace.phone_neighbour)
            subplace.perc_phone_public = as_perc(subplace.phone_public)
            subplace.perc_phone_nearby = as_perc(subplace.phone_nearby)
            subplace.perc_phone_not_nearby = as_perc(subplace.phone_not_nearby)
            subplace.perc_phone_none = as_perc(subplace.phone_none)
        except ZeroDivisionError:
            pass

    dump_indicator_and_stats("perc_phone_and_cell", "phone_and_cell")
    dump_indicator_and_stats("perc_phone_only", "phone_only")
    dump_indicator_and_stats("perc_phone_cell_only", "phone_cell_only")
    dump_indicator_and_stats("perc_phone_neighbour", "phone_neighbour")
    dump_indicator_and_stats("perc_phone_public", "phone_public")
    dump_indicator_and_stats("perc_phone_nearby", "phone_nearby")
    dump_indicator_and_stats("perc_phone_not_nearby", "phone_not_nearby")
    dump_indicator_and_stats("perc_phone_none", "phone_none")

func_map = {
    "Census 01_Sub Place_Density.xls" : func_density,
    "Census 01_Sub Place_Household_Toilet.xls" : func_toilet,
    "Census 01_Sub Place_Household_Telephone.xls" : func_telephone,
}

def main():
    if not os.path.exists("output"):
        os.mkdir("output")

    init_database()
    for _, _, c in os.walk("data"):
        for filename in c:
            if filename in func_map:
                func_map[filename](filename)

if __name__ == "__main__":
    main()
