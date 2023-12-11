#!/bin/bash
	echo '<odoo><data>'

for i in ./planets/*
do

  	img=$(base64 "$i")
  	
  name=$(basename "$i" | sed 's/\(.*\)\..*/\1/')


	echo '<record id="odoogame.planet_'$name'" model="odoogame.planet_img">'
	echo '<field name="name">'$name'</field>'
	echo '<field name="image">'"$img"'</field>'
	echo '</record>'
done
	echo '</data></odoo>'
