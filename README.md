[![Build Status](https://travis-ci.org/righettod/robots-disallowed-dict-builder.svg?branch=master)](https://travis-ci.org/righettod/robots-disallowed-dict-builder)

[![Requirements Status](https://requires.io/github/righettod/robots-disallowed-dict-builder/requirements.svg?branch=master)](https://requires.io/github/righettod/robots-disallowed-dict-builder/requirements/?branch=master)

# Objective

This project provide a simple script highly inspired from [this project](https://github.com/danielmiessler/RobotsDisallowed).

As [ALEXA list is not freely provided anymore](https://twitter.com/paul_pearce/status/800780539204538370), the [CISCO Umbrella Popularity List](http://s3-us-west-1.amazonaws.com/umbrella-static/index.html) is used (information is also provided to use the [MAJESTIC Million CSV](https://blog.majestic.com/development/majestic-million-csv-daily/)).

Python portage has been created in order to be able to build the dictionary on Windows/Linux/Mac.

To resume, the script generate a dictionary containing the most common **DISALLOW** clauses from [robots.txt](https://moz.com/learn/seo/robotstxt) file found on CISCO Top 1 million sites.

The built dictionary can then be used used with this [discovery tool](https://github.com/maurosoria/dirsearch) to find hidden content on a target web site.

# Requirements

## Python

The script need **Python** version **>= 3.5.3**.

```shell
$ python --version
Python 3.5.3
```

## Python dependencies

Install dependencies packages using the following command:

```shell
$ pip install -r requirements.txt
```

# Build a dictionary

Run the following command to get the command line options:

```
$ python dict_builder.py -h
usage: dict_builder.py [-h] -f SITE_FILE_PATH [-n SITE_LIMIT]
                       [-t WORKER_THREAD_MAX]
                       [-m DISALLOW_ENTRY_MIN_OCCURRENCE]

optional arguments:
  -h, --help            show this help message and exit
  -f SITE_FILE_PATH     
                        Location to the CSV file of the CISCO Top 1 million sites.
  -n SITE_LIMIT         
                        Maximum number of sites to process of the CISCO sites list.
  -t WORKER_THREAD_MAX  
                        Maximum number of parallel threads to use to process the CISCO sites list.
  -m DISALLOW_ENTRY_MIN_OCCURRENCE
                        Minimum number of occurrence for a DISALLOW entry to be kept in the built dictionary.
```

Run the following command to build a dictionary:

```shell
# Download the CISCO Top 1 million sites archive
$ wget http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip
# Uncompress it to have access to the CSV file
$ unzip top-1m.csv.zip
# Run a generation using the CSV file
$ python dict_builder.py -n 100 -t 5 -f top-1m.csv -m 3
[*] Initialization...
[*] Process the first 100 sites available from the CISCO sites using 5 threads en parallel...
................................................................
[*] Gather the information and build the final dictionary...
[!] Dictionary built in file 'disallowed_entries_dict.txt' (217 entries).
```

# Use MAJESTIC sites list instead of the CISCO one

Run the following command to build a dictionary using the [MAJESTIC Top 1 million sites list](https://blog.majestic.com/development/majestic-million-csv-daily/):

```shell
# Download the MAJESTIC Top 1 million sites CSV file
$ wget http://downloads.majestic.com/majestic_million.csv
# Transform the downloaded file to an input source that use the same format 
# than the CISCO Top 1 million sites CSV file
$ cat majestic_million.csv | awk -F  "," 'NR>1 {print $1 "," $3}' > input.csv
# Run a generation using the CSV file
$ python dict_builder.py -n 100 -t 5 -f input.csv -m 3
...
```

# References

* https://blog.majestic.com/development/alexa-top-1-million-sites-retired-heres-majestic-million/
* http://s3-us-west-1.amazonaws.com/umbrella-static/index.html