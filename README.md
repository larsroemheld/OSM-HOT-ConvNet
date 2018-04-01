# OSM-HOT-ConvNet
Using convolutional neural networks to pre-classify images for the humanitarian openstreetmap team (HOT &amp; mapgive).

This project uses satellite imagery to support map creation in the developing world. I gather my own dataset by downloading imagery released through the U.S. State Department’s MapGive project and using map data provided by the Humanitarian OpenStreetMap Team. Using this data, I train several Convolutional Neural Network models designed after the SegNet architecture to perform semantic image segmentation. The output of these models are map-like images that may in a later step be used to reconstruct map data, accelerating the work of online remote mapping volunteers. This paper details progress made towards this goal; my best model’s pixel-average test accuracy of about 69% does not allow production use yet. I conclude on notes for future work.

See the pdf-report for details.

I recommend this later report for more sophisticated approaches to classifying buildings specifically:
https://medium.com/the-downlinq/object-detection-on-spacenet-5e691961d257
https://devblogs.nvidia.com/parallelforall/exploring-spacenet-dataset-using-digits/
