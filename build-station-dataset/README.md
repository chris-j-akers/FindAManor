## Contents <!-- omit in toc -->

- [Introduction](#introduction)
- [An Origin File](#an-origin-file)
- [Generate Initial DataSet](#generate-initial-dataset)
- [Filter on distance](#filter-on-distance)
- [Set Google Place\_Id](#set-google-place_id)
- [Setting travel times](#setting-travel-times)
- [Filtering travel times](#filtering-travel-times)
- [Export to CSV](#export-to-csv)
- [Import into google maps](#import-into-google-maps)


## Introduction

This README.md walks through an example of using the scripts to find all stations less than an hour's train journey from Charing Cross.

## An Origin File

In order to work out where everything is in relation to your starting point, you need to establish the starting point.

This example starts from Charing Cross, so we need an origin file with Charing Cross Station details.

```json
{
    "name": "Charing Cross Station",
    "geometry": {
        "latitude": "51.50821289947005",
        "longitude": "-0.12436157975242443"
    },
    "place_id": "ChIJ9033RhYFdkgR6i08EtbBeHk"
}
```
The values are easy to get manually from the Google Maps GUI at [maps.google.com](maps.google.com). Latitude and Longitude can be found by right-clicking on your place and copying them to clipboard.

![Charing Cross Longitude and Latitude](/readme-assets/charing-cross-coords.png)

The place_id can be found by visiting [https://developers.google.com/maps/documentation/places/web-service/place-id#find-id](https://developers.google.com/maps/documentation/places/web-service/place-id#find-id) and searching for the place.

![Charing Cross Station Place_Id](/build-station-dataset/readme-assets/charing-cross-station-place-id.png)

## Generate Initial DataSet

We want to get an initial dataset of all stations available in out station files and their distance from the station in our origin file.

The script `_build-initial-dataset.py` takes a single parameter `--origin-file` which is the path to the file we created, above.

```bash
FindAManor/build-station-dataset on  main [?] via 🅒 OurNewHome 
➜ python ./_build-initial-dataset.py --origin-file ./origin-files/charing-cross.json --output-file ./out/charing-cross.json
- Initialising stations dataset
warning: no tfl fare-zone match for station [Bromley-By-Bow Station]
warning: no tfl fare-zone match for station [Crossharbour & London Arena Station]
warning: no tfl fare-zone match for station [Custom House Station]
warning: no tfl fare-zone match for station [Cutty Sark Station]
warning: no tfl fare-zone match for station [Edgware Road Bakerloo Station]
warning: no tfl fare-zone match for station [Edgware Road Circle Station]
warning: no tfl fare-zone match for station [Hammersmith (D & P) Station]
warning: no tfl fare-zone match for station [Harrow on the Hill Station]
warning: no tfl fare-zone match for station [Heathrow Terminals 1, 2, 3 Station]
warning: no tfl fare-zone match for station [King's Cross St. Pancras Station]
warning: no tfl fare-zone match for station [Shepherd's Bush Central Station]
warning: no tfl fare-zone match for station [Shepherd's Bush Hammersmith & City Station]
warning: no tfl fare-zone match for station [St. James's Park Station]
warning: no tfl fare-zone match for station [St. John's Wood Station]
warning: no tfl fare-zone match for station [St. Paul's Station]
[3092] stations found
- Setting distances from origin
- Writing to file [./out/charing-cross.json]
➜ 
```
It seems that we were unable to match a few stations in our list and enter their fare-zone. 

This is because we need to use two different TFL files to get station information. One is a `KML` file and contains station names along with Longitude/Latitude and the other contains their zones. Problem is we try and join across the files on station name and their *slightly* different. E.g. for St James's Park, one file uses a period (.) at the 'St.', the other doesn't.

Not too much trouble to update in manually, though. As below, we just add the zone in the relevant field. NOTE: The zone is a list because some stations cross zones, so are valid for more than one.

```json
        {
            "name": "St. James's Park Station",
            "type": "tfl",
            "zone": [1],
            "geometry": {
                "latitude": "51.499345456140375000",
                "longitude": "-.134183744115531720"
            },
            "distance_km": 1.199354113453225
        },
```

Note also that our origin station has been put at the top of the output file, along with the number of stations in the file. We don't need to use this origin file again.

```json
{
    "count": 3092,
    "origin": {
        "name": "Charing Cross Station",
        "geometry": {
            "latitude": "51.50821289947005",
            "longitude": "-0.12436157975242443"
        },
        "place_id": "ChIJ9033RhYFdkgR6i08EtbBeHk"
    },
    "stations": {
        ...
        ...
        ...
    }
}
```

## Filter on distance

I'm not going to commute to Edinburgh and back every day, as nice as it is, so lets start by taking out stations so far away they're pointless. Do this now and we reduce the number of API calls to Google later and save a bit of cash.

The `GeoPy` library allows us to calculate distances based on the co-ordinates of our stations.

I reckon if we limit our search to stations less than 80 km away, that would narrow down the calls to Google quite a bit, but give us some decent room to further filter.

`_filter-on-radius.py` takes an `--input-file` parameter which is a JSON file in the format generated by the `_build-initial-dataset.py` script, above. It removes stations more than the `--radius` (km) parameter away from our origin station. If an `--output-file` parameter is included, it will write the results to that file otherwise it will overwrite the `--input-file`.

```bash
➜ python ./_filter-on-radius.py --input-file ./out/charing-cross.json --radius 80
- Filtering stations to those [80km] from origin
        - [969] stations left
FindAManor/build-station-dataset on  main [?] via 🅒 OurNewHome took 1m 43s 
➜ 
```
Ok, so we've gone from 3092 stations to 969.

## Set Google Place_Id

We will be making 969 calls to google in the next section as we want to set each station's place id. This is not entirely necessary as we could find station travel time using the co-ordinates but Google recommends place_id and it's actually not too much hassle in the grand scheme of things. Just in case, though, there is an additional script called `_set-travel-times-from-coords.py` which means this section can be skipped.

Note the warning when the script runs.

```bash
➜ python ./_set-google-place-id.py --input-file ./out/charing-cross.json 
This command uses the Google Maps Geo Matrix API which can incur cost. Are you sure you want to continue? Y/N: Y
- Trying to find google place id for [969] stations
FindAManor/build-station-dataset on  main [?] via 🅒 OurNewHome took 1m 43s 
➜ 
```
This can take a few minutes.

Similarly to the above script that identifies fare-zones, this will print to stdout any stations it can't find a `place_id` for. You can add them manually (it shouldn't be too many).

So, now we have place_ids in our station data.

```json
...
...
{
    "name": "Apsley Station",
    "type": "national_rail",
    "geometry": {
        "latitude": "51.732712",
        "longitude": "-0.463568"
    },
    "distance_km": 34.28970492007989,
    "place_id": "ChIJV1e2gHBBdkgR64t1iR3xwr4"
},
{
    "name": "Arlesey Station",
    "type": "national_rail",
    "geometry": {
        "latitude": "52.025938",
        "longitude": "-0.266178"
    },
    "distance_km": 58.42960336040816,
    "place_id": "ChIJS65M0rXMd0gReyBijOmKsTQ"
},
...
...
```
## Setting travel times

Now we make the last of our set of calls to the Google Maps API to set travel times to each station.

Again, this will take a few minutes to run but we will be left with the time it takes in seconds and minutes from our origin station to every other station in the dataset using TFL or National Rail.

```bash
➜ python ./_set-travel-times_from_place_id.py --input-file ./out/charing-cross.json 
This command uses the Google Maps Distance Matrix API which can incur cost. Are you sure you want to continue? Y/N: Y
FindAManor/build-station-dataset on  main [?] via 🅒 OurNewHome took 1m 43s 
➜ 
```


```json
{
    "name": "Saunderton Station",
    "type": "national_rail",
    "geometry": {
        "latitude": "51.675751",
        "longitude": "-0.825626"
    },
    "distance_km": 52.05000377620459,
    "place_id": "ChIJw0qt9jOLdkgRhc073EBs5XI",
    "travel_time_secs": 4497,
    "travel_time_mins": 74.95
},
{
    "name": "Sevenoaks Station",
    "type": "national_rail",
    "geometry": {
        "latitude": "51.27734",
        "longitude": "0.182193"
    },
    "distance_km": 33.3922252223159,
    "place_id": "ChIJ-cy9vGdS30cRHclUHPj5EnQ",
    "travel_time_secs": 3223,
    "travel_time_mins": 53.71666666666667
},
```
## Filtering travel times

We now take out stations that take more than 50 minutes or less to get to.

```bash
➜ python ./_filter-on-travel-time.py --input-file ./out/charing-cross.json --operator lte --travel-time-secs 3300
- Filtering stations to those equal to or less than [3300 seconds] from origin
[500] stations left
FindAManor/build-station-dataset on  main [?] via 🅒 OurNewHome took 1m 43s 
➜ 
```
..But also, ones that take less than 15 minutes to get to. This is optional, but a bit tidier. As with fare zone 1, it's unlikely I can afford to live close to Charing Cross or, if I could, it would only be an apartment.

```bash
FindAManor/build-station-dataset on  main [?] via 🅒 OurNewHome 
➜ python ./_filter-on-travel-time.py --input-file ./out/charing-cross.json --operator gte --travel-time-secs 900 
- Filtering stations to those equal to or less than [900 seconds] from origin
[493] stations left
FindAManor/build-station-dataset on  main [?] via 🅒 OurNewHome took 1m 43s 
➜ 
```
Ok, only removed 7 but there we are now down to 493 stations left in our Dataset.

## Export to CSV

Now we use the last script to export this dataset to a CSV file so we can import it into Google Maps.

```bash
FindAManor/build-station-dataset on  main [?] via 🅒 OurNewHome 
➜ python ./_export_to_google_csv.py --input-file ./out/charing-cross.json 
done
FindAManor/build-station-dataset on  main [?] via 🅒 OurNewHome took 1m 43s 
➜ 
```

## Import into google maps

First, visit [mymaps.google.com](mymaps.google.com) and login.

Click 'Create New Map'.

![Create New Map](/build-station-dataset/readme-assets/create-new-map.png)

Underneath 'Untitled Layer', click 'Import'.

![Import Layer](/build-station-dataset/readme-assets/import-layer.png)

Click 'Browse' and navigate to the CSV file generated above.

Select the following options on the 'Placemark Selection' pop-up.

![Placemark Selection](/build-station-dataset/readme-assets/placemark-selection.png)

Select the following option on the 'Title Selection' pop-up.

![Title Selection](/build-station-dataset/readme-assets/title-selection.png)

Click finish.

You should see a bunch of markers appear against all the stations in the file.

I usually then split the colours based on whether the type of station is TFL or National Rail. You can do this by grouping them by 'Type'.

![Group Places by Type](/build-station-dataset/readme-assets/style-by-type.png)

And there is a nice map showing all the stations that are 50 minutes or less from our origin station of Charing Cross. Importantly, we've skimped on the Google API Requests and won't be billed for anything this month.

![Final Map](/build-station-dataset/readme-assets/final-map.png)
