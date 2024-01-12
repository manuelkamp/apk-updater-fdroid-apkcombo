#APK Updater v1.2
#(C) 2024 by Manuel Kamper (kmpr.at)
#Do not remove copyright when distributing!
import feedparser, mysql.connector, os, glob, time, shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By

metadata_path = "/mnt/data/metadata"
repo_path = "/mnt/data/repo"
temp_path = "/tmp/apkdown"

mydb = mysql.connector.connect(
    host="localhost",
    user="appstore",
    password="<your-pwd>",
    database="appstore"
)

### NO EDITS BELOW NECESSARY ###

url = "https://apkcombo.com/latest-updates/feed"

def get_last_filename_and_rename(new_filename):
    global temp_path, repo_path
    files = glob.glob(temp_path + '/*')
    max_file = max(files, key=os.path.getctime)
    filename_stripped = max_file.replace("_apkcombo.com","")
    filename = filename_stripped.split("/")[-1].split("_")[-2]
    new_filename2 = max_file.replace(filename, new_filename)
    new_filename2 = new_filename2.replace("_apkcombo.com","")
    print(new_filename2)
    new_path = new_filename2.replace(temp_path, repo_path)
    shutil.move(max_file, new_path)
    return new_path

mycursor = mydb.cursor()

print("APK Updater started on " + datetime.now().strftime("%d.%m.%Y %H:%M:%S") + ".")
print("Clearing APK Database from previous updates...", end="", flush=True)
sql = "TRUNCATE appstore"
mycursor.execute(sql)
mydb.commit()
print(" DONE.")

#fetch updated apps from rss feed
print("Fetching updated APKs from RSS...", end="", flush=True)
feed = feedparser.parse(url)
print(" DONE")
updates = 0
print("Importing updated APK infos from RSS into Database...", end="", flush=True)
for entry in feed.entries:
    updates += 1
    appname = str(entry.link).split("/")[-2]
    sql = "INSERT INTO appstore (url, app_name, updated) VALUES (%s, %s, %s)"
    date_str = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
    val = (entry.link+"download/apk", appname, date_str)
    mycursor.execute(sql, val)
mydb.commit()
print(" DONE (" + str(updates) + " APK infos).")

#find local available apps from metadata directory (filename without .yml)
print("Searching for Apps in local Appstore...", end="", flush=True)
list_apps = ['.'.join(x.split('.')[:-1]) for x in os.listdir(metadata_path) if os.path.isfile(os.path.join(metadata_path, x))]
print(" Found " + str(len(list_apps)) + " Apps.")

#iterate throug local apps and query db to find matches. if match found, mark app for update
print("Finding Apps to update...")
real_updates = 0
for app in list_apps:
    sql = "SELECT * FROM appstore WHERE app_name='" + app + "'"
    mycursor.execute(sql)
    row = mycursor.fetchone()
    if row is not None:
        print("Local App " + app + " marked for update!")
        sql2 = "UPDATE appstore SET marked_for_update=1 WHERE id=" + str(row[0])
        mycursor.execute(sql2)
        real_updates +=1
mydb.commit()
print("Found " + str(real_updates) + " new updates for Apps in local Appstore.")

if real_updates > 0:
    print("Downloading app updates...")
    #select all marked_for_update entries from db and download apk from apk_url into repo_path
    #with filename: app_name_version.apk/.xapk
    #make dir temp_path if it does not exist
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    #load firefox selenium and download apk
    options=Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", temp_path)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1200, 700)

    #get download-url for every file marked for update
    sql = "SELECT * FROM appstore WHERE marked_for_update=1"
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    for row in rows:
        #make sure temp_path is empty
        for file in os.scandir(temp_path):
            if file.name.endswith(".apk") or file.name.endswith(".xapk"):
                os.unlink(file.path)
        driver.get(row[1])
        time.sleep(5)
        cookiebutton = driver.find_element(By.CSS_SELECTOR, 'svg.icon.ic-download-right')
        cookiebutton.click()
        print("APK " + row[2] + " downloaded...", end="", flush=True)
        time.sleep(30)
        #rename and move file to repo
        print(" moved to: " + get_last_filename_and_rename(row[2]) + ".")
    driver.close()
    driver.quit()

    print("Cleanig up...", end="", flush=True)
    #delete temp_path directory and all files in it
    shutil.rmtree(temp_path)

    #kill all running firefox processes to free RAM
    os.system("pkill -f firefox")
    print(" DONE.")

    print("Updating local Appstore...", end="", flush=True)
    #todo run updating f-droid appstore command
    os.system("cd /mnt/data && fdroid update -c && cp /mnt/data/icons/icon.png /mnt/data/repo/icons/icon.png")
    print(" DONE.")
print("Finished APK Updater on " + datetime.now().strftime("%d.%m.%Y %H:%M:%S") + ".")