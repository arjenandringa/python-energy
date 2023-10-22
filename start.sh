#!/bin/bash

###################################################################################
#   What if we just test the stuff we've built in a disposable, replayable way?   #
###################################################################################

# Build & run
sudo docker build . --file Dockerfile --tag energy
sudo docker run --rm -d -p 5432:5432 --name postgres energy && sleep 20

# Run scheduler
python3 scheduler.py

# Wait 65 seconds for some results + leeway
sleep 65

# Run psql and get a quick overview
psql -h localhost -U docker -d energy -c 'SELECT * FROM energydb;'

# Ask next step, to keep running or to kill environment
echo -n "Done, destroy env? (Y/N)"
read DECISION
if [ "$DECISION" = "Y" ]
then
sudo docker stop energyv1
else
echo "Stop the environment yourself anytime using docker stop energyv1, exiting"
fi
