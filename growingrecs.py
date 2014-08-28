#!/usr/lib/python2.7

# MIT License.
# Copyright 2014 Frances Hocutt

# growingrecs.py is a command-line tool to help you plan your garden.
# Given a crop, it uses the Growstuff API to  finds the most common conditions
# that Growstuff users have used for that crop: how much sun, and whether they
# planted from seeds, seedlings, rootstock, etc.).

import requests
import string

def getcropinfo(crop):
    """Given a crop, gets the data available in Growstuff.

    crop - a string with the crop to get data on. Whitespace and capitalization
           are ok.
    """
    cropslug = slugify(crop)
    cropinfo = apirequest(cropslug)
    return cropinfo

def slugify(crop):
    """Creates a slug. Lowercases, trims whitespace, replaces " " with "-"."""
    crop = string.lower(crop)
    crop = string.strip(crop)
    crop = crop.replace(" ", "-")
    return crop

def apirequest(cropslug):
    """Given a slug, retrieves data from the Growstuff API. Returns a dict.

    If the API returns an error, the user is prompted to try again.
    """
    URI = "http://growstuff.org/crops/%s.json" % cropslug
    r = requests.get(URI)
    if r.status_code == 200:
        cropinfo = r.json()
        return cropinfo
    elif r.status_code == 404:
        #this gives NoneType not subscriptable errors, #FIXME
        print ("We couldn't find that crop. "
               "Please enter a crop that is in the Growstuff database.\n")
        run()
    else:
        print "API error, please try again.\n"
        run()

def parseplantings(cropinfo):
    """Counts how many plantings have the same (planted_from, sunniness) combo.

    Returns a dict with frequency of conditions and an int with the total
    number of plantings.

    cropinfo - a dict from the API's json output
    """
    planting_info = {}
    plantings_count = cropinfo["plantings_count"]
    for item in cropinfo["plantings"]:
        conditions = (item["planted_from"], item["sunniness"])
        if conditions in planting_info:
            planting_info[conditions] += 1
        else:
            planting_info[conditions] = 1
    return (planting_info, plantings_count)

def mostplantings(planting_info):
    """Returns a tuple with the most frequent conditions:
       (planted_from, sunniness)."""
    v = list(planting_info.values())
    k = list(planting_info.keys())
    return k[v.index(max(v))]

def run():
    crop = raw_input("What would you like to plant?\n")
    cropinfo = getcropinfo(crop)
    planting_info, plantings_count = parseplantings(cropinfo)
    if plantings_count > 0:
        planted_from, sunniness = mostplantings(planting_info)
        print "%s was planted %s times." % (crop, plantings_count)
        print "It was most often planted from %s in %s." % (planted_from, 
                                                            sunniness)
    else:
        print "%s has not been planted yet." % crop

if __name__ == "__main__":
    run()

def test(crop, cropinfo):
    """Same as run() but without the API call."""
    planting_info, plantings_count = parseplantings(cropinfo)
    if plantings_count > 0:
        planted_from, sunniness = mostplantings(planting_info)
        print "%s was planted %d times." % (crop, plantings_count)
        print "It was most often planted from %s in %s." % (planted_from,
                                                            sunniness)
    else:
        print "%s has not been planted yet." % crop

