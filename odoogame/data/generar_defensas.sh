#!/bin/bash
	echo '<odoo><data>'

for i in ./defensas/*
do

  	img=$(base64 "$i")
  	
  name=$(basename "$i" | sed 's/\(.*\)\..*/\1/')


	echo '<record id="odoogame.defense_type_'$name'" model="odoogame.defense_type">'
	echo '<field name="name">'$name'</field>'
	echo '<field name="icon">'"$img"'</field>'
	echo '</record>'
done
	echo '</data></odoo>'
