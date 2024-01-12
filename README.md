# APK Updater

This python script downloads all new APKs for your local f-droid repo from apkcombo.
## ATTENTION: THIS REPOSITORY IS A COPY AND WILL NOT BE UPDATED ON REGULAR BASIS. PLEASE GO TO [https://git.kmpr.at/kamp/TCS2FHEM](https://git.kmpr.at/kamp/apk-updater-fdroid-apkcombo) TO SEE THE LATEST CODE AND/OR SUBMIT PULL REQUESTS OR ISSUES!

## Prerequisites

Use Ubuntu 22.04 server (headless) with at least 1 GB RAM   
Install python 3.10 and PIP   
`apt install python3 python-pip3`   
Install selenium   
`pip install selenium`   
Install MySQL Connector   
`pip install mysql-connector-python`   
Download latest firefox binary (do not use apt install!) from: https://www.mozilla.org/de/firefox/linux/ and extract into /opt   
`tar xjf firefox-*.tar.bz2 && mv firefox /opt`   
`ln -s /opt/firefox/firefox /usr/bin/firefox`   
Download latest geckodriver from https://github.com/mozilla/geckodriver/releases and extract into /opt   
`tar -zxvf geckodriver-*.tar.gz && mv geckodriver /opt/`   
`ln -s /opt/geckodriver /usr/bin/`    

## Installation

Download python-script and edit values for paths (regaring your f-droid config) and mysql connection details.   
Execute db.sql file in your database to set up the working database.   
Execute the python-file for the first test run and watch console outputs.   
`python3 updater.py`   
If everything went well, configure crontab to run the script hourly (this is the refresh interval of the apkcombo RSS feed).   
`crontab -e`   
`30 * * * * /usr/bin/python3 /mnt/data/updater/updater.py > /dev/null 2>&1`   
In case you want to have a logfile, use this line:   
`30 * * * * /usr/bin/python3 /mnt/data/updater/updater.py >> /mnt/data/updater/updater.log`   

## Remarks
I am not affiliated with any APK developer, nor f-droid or apkcombo. All rights belong to their owner.
