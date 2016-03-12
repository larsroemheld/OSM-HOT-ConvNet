# This is probably a terrible idea. Rather loop over files in python.
for file in osm-hot-images-map/*.png; do 
	echo $file
	python convertMapImage.py $file
done