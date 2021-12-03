#!/bin/bash
while [ true ];
do
	sleep 5
	
	echo start_script
	sudo git fetch --all
	sudo git reset --hard origin/master && sudo jupyter nbconvert --to script server/*.ipynb src/france/*.ipynb src/world/*.ipynb --to python
	sudo python3 server/script_update_data.py

	sleep 60
done
