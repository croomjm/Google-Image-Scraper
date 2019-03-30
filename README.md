[//]: # (Image References)
[Clinton_Punk]:https://pixel.nymag.com/imgs/fashion/daily/2017/12/12/12-hillary-painting.w330.h412.jpg "Example Politician Art Used to Test CNN Generalization"
[scraper]: /scraper.gif "ImageScraper() in action!"
[review]: /image_review.gif "ReviewImages() in action!"

# Google-Image-Scraper
To assist with [my Udacity Robotics Software Degree](https://confirm.udacity.com/AQCTW57M) Neural Network Inference project, I wrote a couple of classes to systematically pull training images from Google image search then scale and crop them to the required size for the neural network. I accomplished this using a few primary libraries:
* [Selenium](https://www.seleniumhq.org/projects/webdriver/)
* [OpenCV2](https://opencv.org/)
* [Numpy](http://www.numpy.org/)

## ImageScraper()
The `ImageScraper()` class allows not only customization of keywords but also of results filter fields typical of google search (currently only extended to faces only or image size filters, but could easily add others). Using Selenium, `ImageScraper()` interacts with Google via a web browser of your choice (I chose Chrome), scrolls down to the bottom of the search results, and downloads all images (up to max images limits) for the list of search terms to a specified location directly from the source address. This makes it easy to bootstrap a machine learning image training set (for well-known subjects, of course) without having to manually source a bunch of images yourself.

![ImageScraper() in action][scraper]

## ReviewImages()
The `ReviewImages()` class leverages Numpy and OpenCV to resize and crop the images to a specified size (e.g. as required by readily available neural network types) or deletes images based on user input, all within a simple graphical UI.

![ReviewImages() in action][review]

## Example Results
For my Udacity Robotics Software Engineer Nanodegree machine learning inference project, I scraped Google for images of a number of well-known politicians' faces to build up a training set. I then used Nvidia's digits platform (thanks for the freebie!) to train a built-in GoogLeNet CNN to recognize the politicians. Turns out, GoogLeNet works pretty well (`¯\_(ツ)_/¯`). It was even able to generalize to recognize artwork depicting various politicians (e.g. the picture of HRC below). See my full results in a pdf report [here](politician-facenet_report.pdf).

[![Punk Hilary Clinton][Clinton_Punk]](https://www.thecut.com/2017/12/hillary-clinton-painting-causes-bomb-scare-at-art-miami.html)

## Installing
Install is pretty straightforward. Just make sure you have the required modules installed or use the included environment.yaml file to source your environment using Anaconda. Options including the file location to download images, image filtering options, etc. are still manually manipulated in the python files.
