#!/bin/bash

#get param from command line
tag="$1"

cd ~/domains/

#Verify directory vino_$tag exists
newdir="vino_${tag}"

if [ ! -d $newdir ]; then
    echo "Error: directory $newdir does not exist"
    exit 1
fi
#verify version
version="v"$(grep -oP '__version__ = "\K\S+' ${newdir}/WijnProject/__init__.py | tr -d '"' )
if [ "$version" != "${tag}" ]; then
    echo "Error: directory ${newdir} does not contain version ${tag}"
    exit 1
else 
    echo "Found version, ${tag} in ${newdir}"
fi


# Stop the current application
echo "Stopping the current application..."
output=$(cloudlinux-selector stop --json --interpreter python --app-root domains/vino.vdwaal.net)
#expected = {"result": "success", "timestamp": 1715533882.345499}
# Check if the result is "success"
if [[ "$output" != *"result": "success"* ]]; then
    echo "Error: Failed to stop the current application."
    exit 1
fi

cd ~
#get version information from  domains/vino.vdwaal.net/WijnProject/__init__.py
old_version="v"$(grep -oP '__version__ = "\K\S+' domains/vino.vdwaal.net/WijnProject/__init__.py | tr -d '"' )
echo "Found current version ${old_version}"

#let user confirm continue
echo "Moving vino.vdwaal.net to vino_${old_version}"
read -p "Are you sure you want to continue? (y/n) " -n 1 -r answer
if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
   echo
   echo "Aborting"
   exit 1
fi
echo
echo "continueing..."
# Move the old application
echo "Moving the old application..."
mv domains/vino.vdwaal.net "domains/vino_${old_version}"


# Copy the new application
echo "Copying the new application..."
mv "domains/${newdir}" "domains/vino.vdwaal.net"

# Copy the database
if [ -f "domains/vino.vdwaal.net/db.sqlite3"]; then
    echo "Moving existing database to filestamped copy of the database...
    today=$(date +%Y%m%d%H%M%S) 
    mv "domains/vino.vdwaal.net/db.sqlite3" "db.sqlite3.$today"
fi
	 
echo "Copying the database..."
cp "domains/vino_${old_version}/db.sqlite3" domains/vino.vdwaal.net

# Activate the virtual environment
echo "Activating the virtual environment..."
source /home/vdwanet/virtualenv/domains/vino.vdwaal.net/3.8/bin/activate

# Zet virtual env: source setenv.sh 
source ~/domains/setenv.sh 

echo "Migration & collect static not part of this yet"
read -p "Do you van to start the server? (y/n) " -n 1 -r answer
if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
   echo
   echo "Aborting"
   exit 1
fi

# Start the server
echo "Starting the server..."
output=$(cloudlinux-selector start --json --interpreter python --app-root domains/vino.vdwaal.net)
# Check if the result is "success"
if [[ "$output" != *"result": "success"* ]]; then
    echo "Error: Failed to stop the current application."
    exit 1
fi


exit 1


# Migrate the database
echo "Migrating the database..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic

