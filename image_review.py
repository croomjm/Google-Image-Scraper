import cv2
import os
import argparse
import numpy as np

class ReviewImages(object):
    def __init__(self,folder):
        self.filenames = self._find_all_images(folder)
        self.image = None
        self.copy = None
        self.corners = [(0,0), (0,0)]
        self.preview_corners = [(0,0), (0,0)]
        self.center = (0,0)
        self.preview_center = (0,0)

        self._reviewAllImages(self.filenames)

    def _isImage(self,filename):
        img_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.tif']

        for fmt in img_formats:
            if filename.endswith(fmt):
                return True

        return False

    def _find_all_images(self,folder):
        #create list of all images within folder and subfolders
        images = []

        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in [f for f in filenames if self._isImage(f)]:
                images.append(os.path.join(dirpath, filename))

        return images

    def _moveROI(self, event, x, y, flags, param):
        #print('X: {0}, Y:{1}'.format(x,y))
        corners = self.corners
        center = self.center

        if event == cv2.EVENT_LBUTTONDOWN:
            corners, center = self._getNewBounds(self.image, (x,y))

        preview_corners, preview_center = self._getNewBounds(self.image, (x,y))

        self.preview_corners = preview_corners
        self.preview_center = preview_center
        self.corners = corners
        self.center = center

    def _saveImg(self, img, filename, format = '.jpg'):
        #save the image to the filename
        new_filename = '.'.join(filename.split('.')[:-1]) + format
        self._deleteImg(filename)
        cv2.waitKey(10) #allow time to delete existing file before saving

        print('Saving {} to disk...'.format(new_filename))
        xmin, ymin = self.corners[0]
        xmax, ymax = self.corners[1]

        #print(xmin, xmax, ymin, ymax)
        #print(img.shape)
        #print(img[ymin:ymax, xmin:xmax])
        cv2.imwrite(new_filename, img[ymin:ymax, xmin:xmax])

    def _deleteImg(self,filename):
        #remove filename from disk
        print('Deleting {} from disk...'.format(filename))
        os.remove(filename)

    def _isSquare(self,image):
        if image.shape[0] == image.shape[1]:
            return True
        return False

    def _reviewAllImages(self, filenames):
        length = len(filenames)
        for i,f in enumerate(filenames):
            print('Reviewing image {0} of {1}: {2}'.format(i, length, f))
            status = self._reviewImage(f)

    def _getNewBounds(self, image, leftTopCorner):
        x,y = leftTopCorner
        ymax = image.shape[0]
        xmax = image.shape[1]
        if ymax > xmax:
            rectSize = xmax
            x = 0
            y = min(y, ymax - rectSize)
            y = max(y, 0)
        else:
            rectSize = ymax
            y = 0
            x = min(x, xmax - rectSize)
            x = max(x, 0)

        corners = [(x,y), (x + rectSize, y + rectSize)]
        center = (x + rectSize//2, y + rectSize//2)

        return [corners, center]

    def _reviewImage(self,filename):
        #open figure of image at normal scale
        #draw square box around middle of picture
        #user moves box by clicking center point
        #hit d to delete picture from dataset
        #hit s to save cropped image as original file name

        self.image = cv2.imread(filename)
        cv2.namedWindow('image')
        cv2.setMouseCallback('image',self._moveROI)

        if self._isSquare(self.image):
            print('Skipping {}. Already square.'.format(filename))
            return False #go to next image without cropping


        self.preview_corners, self.preview_center = self._getNewBounds(self.image, (0,0))
        self.center = self.preview_center
        self.corners = self.preview_corners

        while True:
            self.copy = np.copy(self.image)
            cv2.rectangle(self.copy, self.corners[0], self.corners[1], (255,0,0))
            cv2.rectangle(self.copy, self.preview_corners[0], self.preview_corners[1], (0,255,0))
            cv2.circle(self.copy, self.preview_center, 3, (0,255,0),-1)
            cv2.circle(self.copy, self.center, 3, (255,0,0),-1)
            cv2.imshow('image', self.copy)
            key = cv2.waitKey(5) & 0xFF

            if key == ord('s'):
                self._saveImg(self.image, filename)
                break

            elif key == ord('d'):
                self._deleteImg(filename)
                break

            elif key == ord('q'):
                break

        cv2.destroyAllWindows()

def main(folder = '/Users/croomjm1/version-control/FaceNet/scraped/'):
    review = ReviewImages(folder)

if __name__ == '__main__':
    main()


