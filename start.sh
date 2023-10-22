#!/bin/bash

###################################################################################
#   What if we just test the stuff we've built in a disposable, replayable way?   #
###################################################################################

# Build & run
docker build . --file Dockerfile --tag python-energy:$(date +%Y%m%d)
docker run --rm -d -p 5434:5432 --name energyv1 python-energy:$(date +%Y%m%d)

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
docker stop energyv1
else
echo "Stop the environment yourself anytime using docker stop energyv1, exiting"
fi