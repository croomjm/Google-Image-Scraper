
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import json
import requests
import sys
import time
import shutil

class ImageScraper(object):
    def __init__(self, searchterms, folder, filters = {}):
        #max images per class
        self.classDownloadLimit = 500
        self.classLimit = 20
        self.maxImageFileSize = 500*10**3 #in bytes
        self.byteDownloadLimit = 1*10**9 #max bytes to download in single scrape

        #maximum number of images downloaded in total
        self.totalDownloadLimit = self.classDownloadLimit*self.classLimit

        self.searchterms = self.formatTerms(searchterms)
        self.parent_folder = folder
        self.extensions = ('jpg', 'jpeg', 'png', 'tiff', 'tif', 'gif')
        self.headers = {}
        self.filters = filters

        os.environ["PATH"] += os.pathsep + os.getcwd()

        self.driver = self.initDriver()

    def getURL(self, searchterm, filters = {}):
        #get search URL based on searchterms and optional filters
        filter_dict = {'face':{True: 'itp:face'},
                       'size':{'Large':'isz:l',
                               'Medium':'isz:m',
                               'Icon':'isz:i'}}

        filter_string = []
        for key in filters:
            key2 = filters[key]
            try:
                attr = filter_dict[key][key2]
            except:
                attr = None

            if attr is not None:
                filter_string.append(attr)

        url = 'https://www.google.com/search?q=' + searchterm + '&hl=en&source=lnms&tbm=isch&'

        if len(filter_string)>0:
            url += '&tbs=' + ','.join(filter_string)

        return url

    def getImageElements(self, url, n_results):
        n_scrolls = n_results // 40 + 1
        elements = []

        self.driver.get(url)

        for i in range(n_scrolls):
            for j in range(10):
                self.driver.execute_script('window.scroll(0, 1000000)')
                time.sleep(0.2)

            time.sleep(1.0)

            try:
                self.driver.find_element_by_xpath("//input[@value='Show more results']").click()
            except Exception as e:
                print('Fewer images found than requested: {}'.format(e))
                break

        images = self.driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')

        return images

    def initDriver(self):
        #initialize selenium driver
        driver = webdriver.Chrome()
        return driver

    def downloadImage(self, img, folder, index):
        url = json.loads(img.get_attribute('innerHTML'))['ou']
        fileType = json.loads(img.get_attribute('innerHTML'))['ity']

        #print('Attempting to download image at url: {}'.format(url))
        
        try:
            if fileType not in self.extensions:
                fileType = 'jpg'

            req = requests.get(url, stream = True)
            #req = urllib.Request(url, headers = self.headers)
            #stream = urllib.urlopen(req).read()

            filename = folder + '/' + str(index) + '.' + fileType

            fileSize = int(req.headers['content-length'])
            if fileSize > self.maxImageFileSize:
                print('File size ({0}) exceeds limit of {1} bytes. '
                      'Aborting download.'.format(fileSize, self.maxImageFileSize))
                return 0, None

            if req.status_code == 200:
                with open(filename, 'wb') as f:
                    #f.write(stream)
                    req.raw.decode_content = True

                    shutil.copyfileobj(req.raw, f)
            else:
                print('Bad request status code: {}'.format(req.status_code))


        except Exception as e:
            print(e)
            return 0, None

        return 1, fileSize

    def formatTerms(self, searchterms):
        #return dict with original search term as key
        #containing dict of number of results per class
        #and url-friendly search term

        formatted = {}

        for st in searchterms:
            url_term = str(st[0])
            url_term = url_term.replace(' ', '+')

            formatted[st[0]] = {'url_term': url_term,
                             'n_results': min(self.classDownloadLimit, st[1])}

        return formatted

    def sanitizeFolderName(self,folder):
        replaced = {'.': '_', ' ':'_'}

        for r in replaced:
            folder = folder.replace(r, replaced[r])

        return folder

    def scrape(self):
        n_downloaded = 0
        bytes_downloaded = 0
        for i, key in enumerate(self.searchterms):
            class_downloaded = 0

            subfolder = self.sanitizeFolderName(key)
            path = self.parent_folder + '/' + subfolder
            
            if not os.path.exists(path):
                os.makedirs(path)

            st = self.searchterms[key]

            #check termination criteria
            if i > self.classLimit:
                print('Max number of classes ({0}) exceeded. Terminating loop.'.format(self.classLimit))
                break

            if n_downloaded >= self.totalDownloadLimit:
                print('Max number of images ({0}) downloaded. Terminating loop.'.format(self.totalDownloadLimit))
                break

            if bytes_downloaded >= self.byteDownloadLimit:
                print('Max bytes ({0}) allowable downloaded. Terminating loop.'.format(self.byteDownloadLimit))
                break

            if n_downloaded + st['n_results'] > self.totalDownloadLimit:
                st['n_results'] = self.totalDownloadLimit - n_downloaded
                print('Reducing number of results for class {0} to meet'
                      'max total downloads limit of {1}'.format(key, self.totalDownloadLimit))
            #end termination criteria checks

            searchURL = self.getURL(st['url_term'], self.filters)

            imageElements = self.getImageElements(searchURL, st['n_results'])

            for j,img in enumerate(imageElements):
                if j > st['n_results']:
                    print('Max number of results for class {0} ({1}) exceeded.'.format(key, st['n_results']))
                    break

                img = imageElements[j]

                print('Downloading image {0} of {1}'
                      ' for class {2}...'.format(class_downloaded, st['n_results'], key))

                status, fileSize = self.downloadImage(img, path, class_downloaded)

                #if successfully downloaded the image
                if status == 1:
                    bytes_downloaded += fileSize
                    n_downloaded += 1
                    class_downloaded += 1

            print('Downloaded total of {0} images for class {1}.'.format(class_downloaded, key))

        print('Downloaded a total of {0} images for {1} classes.'.format(n_downloaded, min(len(self.searchterms), self.classLimit)))

        self.driver.quit()

def main():
    searchterms = [['Doggo', 50],
                   ['Doge',100],
                   ['Cat!',10]]


    folder = '/Users/croomjm1/version-control/FaceNet/scraped'

    scraper = ImageScraper(searchterms, folder)#, 'size': 'Small'})

    try:
        scraper.scrape()
    except Exception as e:
        print('Exception: {}'.format(e))
        scraper.driver.quit()


if __name__ == '__main__':
    main()


