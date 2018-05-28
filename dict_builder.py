"""
Simple script inspired from https://github.com/danielmiessler/RobotsDisallowed
As ALEXA list is not freely provided anymore, the CISCO Umbrella Popularity List is used.
Python portage has been created in order to be able to build the dictionary on Windows/Linux/Mac.

CISCO Umbrella Popularity List:
    http://s3-us-west-1.amazonaws.com/umbrella-static/index.html
    http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip

Dependencies:
    pip install requests termcolor colorama
"""

import requests
import colorama
import argparse
import hashlib
import collections
import shutil
import os
from termcolor import colored
from concurrent.futures.thread import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Constants
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Firefox/42.0"}
WORK_TEMP_FOLDER = "work"
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def process_site(url, work_folder):
    """
    Extract the disallow entries from robots.txt file of a site
    :param url: URL of the site to process
    :param work_folder: Working folder where create the data file for the processed site
    """
    robot_content = download_robots_file_content(url)
    selected_entries = ""
    if robot_content is not None:
        lines = robot_content.split("\n")
        for r_line in lines:
            r_line_tmp = r_line.strip()
            if r_line_tmp.startswith("Disallow:"):
                selected_entries += r_line_tmp.replace("Disallow:", "").strip() + "\n"
    if len(selected_entries) > 0:
        with open(work_folder + "/" + hashlib.md5(url.encode("utf-8")).hexdigest() + ".txt", "w") as r_file:
            r_file.write(selected_entries)
    print('.', end='')


def download_robots_file_content(base_url):
    """
    Get the content of the 'robots.txt' file from the specified site
    :param base_url: Base URL of the site like "google.com"
    :return: The robots.txt content for the site or NONE if the site cannot be contacted or do not have a 'robots.txt' file
    """
    robots_content = None
    try:
        target_url = "http://" + base_url + "/robots.txt"
        response = requests.get(target_url, headers=HEADERS, allow_redirects=False, verify=False, timeout=5)
        if response.status_code == 200:
            robots_content = response.text
    except:
        try:
            target_url = "https://" + base_url + "/robots.txt"
            response = requests.get(target_url, headers=HEADERS, allow_redirects=False, verify=False, timeout=5)
            if response.status_code == 200:
                robots_content = response.text
        except:
            robots_content = None

    return robots_content


if __name__ == "__main__":
    colorama.init()
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action="store", dest="site_file_path", default="top-1m.csv", help="Location to the CSV file of the CISCO Top 1 million sites.", required=True)
    parser.add_argument('-n', action="store", dest="site_limit", default=1000000, type=int, help="Maximum number of sites to process of the CISCO sites list.")
    parser.add_argument('-t', action="store", dest="worker_thread_max", default=5, type=int, help="Maximum number of parallel threads to use to process the CISCO sites list.")
    parser.add_argument('-m', action="store", dest="disallow_entry_min_occurrence", type=int, default=1, help="Minimum number of occurrence for a DISALLOW entry to be kept in the built dictionary.")
    args = parser.parse_args()
    print(colored("[*] Initialization...", "cyan", attrs=[]))
    if os.path.exists(WORK_TEMP_FOLDER):
        shutil.rmtree(WORK_TEMP_FOLDER)
    os.mkdir(WORK_TEMP_FOLDER)
    print(colored("[*] Process the first %s sites available from the CISCO sites using %s threads en parallel..." % (args.site_limit, args.worker_thread_max), "cyan", attrs=[]))
    with open(args.site_file_path, "r") as f:
        csv_lines = f.readlines()
    with ThreadPoolExecutor(max_workers=args.worker_thread_max) as executor:
        count = 0
        for csv_line in csv_lines:
            site_url_to_use = csv_line.split(",")[1].strip()
            executor.submit(process_site, site_url_to_use, WORK_TEMP_FOLDER)
            count += 1
            if count >= args.site_limit:
                break
    print()
    print(colored("[*] Gather the information and build the final dictionary...", "cyan", attrs=[]))
    entries = {}  # we build the dict by putting in the top of the list the top most DISALLOW entries found
    if len(os.listdir(WORK_TEMP_FOLDER)) == 0:
        print(colored("[!] Sites analyzed don't provides a 'robots.txt' file or it don't contains any DISALLOW entries.", "yellow", attrs=[]))
    else:
        for filename in os.listdir(WORK_TEMP_FOLDER):
            with open(WORK_TEMP_FOLDER + "/" + filename, "r") as f:
                content = f.readlines()
            for line in content:
                s_line = line.strip()
                if len(s_line) > 0:
                    if s_line not in entries:
                        entries[s_line] = 1
                    else:
                        tmp = entries[s_line]
                        entries[s_line] = tmp + 1
        sorted_entries = collections.OrderedDict(sorted(entries.items(), key=lambda t: t[1], reverse=True))
        with open("disallowed_entries_dict.txt", "w") as f:
            for se in sorted_entries:
                if sorted_entries[se] >= args.disallow_entry_min_occurrence:
                    f.write(se + "\n")
        with open("disallowed_entries_dict.txt", "r") as f:
            entries_count = len(f.readlines())
        print(colored("[!] Dictionary built in file 'disallowed_entries_dict.txt' (%s entries)." % entries_count, "green", attrs=[]))
