from email.mime import image
from PIL import Image, ImageChops
from numpy import asanyarray, asarray
import urllib.request as req

Mem = {}


## Image comparator recieves 2 images of the same size and calculates the proximity between them 
# @param im1        image one 
# @param im2        image tow 
# @returns          proximity factor 
# @note             the proximity factor is between 0 and 1 
#                   - 1 if it is the same image
#                   - 0 if it is completly diferent
def compare(im1:Image, im2:image)->float:

    dif = ImageChops.difference(im1, im2)

    dif = asarray(dif)

    # dif = asanyarray(Image.open('General/image.png'))
    acumulator = 0
    counter = 0
    for line in dif:
        for pixel in line:
            ccounter = 0
            pacumulator = 0

            for cord in pixel: 
                ccounter += 1
                pacumulator += cord
            
            acumulator += pacumulator/ccounter
            counter += 1

        
    val = (250 - acumulator/counter)/250

    return val


## Compare an image from a given public
# @param link       online link of the image 
# @param path2      path of the local image to compare
# @returns          proximity factor 
# @note             the proximity factor is between 0 and 1 
#                   - 1 if it is the same image
#                   - 0 if it is completly diferent 
# @see comapre
def compareFromLink(link, path2):
    buffer = req.urlopen(link)
    im1 = Image.open(buffer)
    im2 = Image.open(path2)

    return compare(im1,im2)


def RecgnReact(link):
    nameList = ['like', 'love', 'care', 'haha', 'wow', 'sad', 'angry']
    dir = 'ReactImages'

    res = 0

    ans = ''

    buffer = req.urlopen(link)
    im1 = Image.open(buffer)

    for react in nameList:
        reactpath =  dir + '/' + react + '.png'
        im2 = Image.open(reactpath)
        sim = compare(im1, im2)

        if sim > res :
            res = sim
            ans = react
    
    return ans


def getReact(link):

    val = Mem.get(link)

    if val :
        return val
    else : 
        val = RecgnReact(link)

        Mem[link] = val

        return val
