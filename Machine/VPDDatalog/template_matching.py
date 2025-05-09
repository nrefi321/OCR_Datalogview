import cv2 as cv
import cv2
import numpy as np

class Matching:
    def __init__(self,minimumPoint = None):
        self.minimumPoint = 30
        if(minimumPoint is not None):
            self.minimumPoint = minimumPoint
        pass
    
    def drawPoint(self,img,point_start,point_End,point_bt):
        cv.rectangle(img, point_start,point_End, (0, 255, 0), 2)
        bpass,bfail = point_bt[0],point_bt[1]
        cv.circle(img,point_start, 20, (255,0,0), 3)
        cv.circle(img,bpass, 20, (0,255,0), 3)
        cv.circle(img,bfail, 20, (0,0,255), 3)
        return img

    def cropTemplateImg(self,img):
        R1 = 481
        R2 = 490
        C1 = 0
        C2 = 1920
        return img[R1:R2,C1:C2]

    def findTemplateMatching(self,imagefind,imageMat):
        try:
            
            imMat = cv.cvtColor(imageMat,cv.COLOR_BGR2GRAY)
            imFind = cv.cvtColor(imagefind,cv.COLOR_BGR2GRAY)
            w, h = imMat.shape[::-1]
            res = cv.matchTemplate(imFind, imMat, cv.TM_CCOEFF_NORMED)
            treshole = 0.9
            #cv.imshow('imgMat',imMat)
            #cv.imshow('imgFind',imFind)
            loc = np.where(res >= treshole)
            print(loc)
            for pt in zip(*loc[::-1]):
                #print(pt)
                if len(pt) == 2:
                    print('Is matching')
                    # cv.imshow('img',imagefind)
                    # cv.imshow('imgMat',cv.rectangle(imagefind, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 3))
                    # cv.waitKey(0)
                    return True ,cv.rectangle(imagefind, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 3)
            return False
        except:
            return False
    
    def matchTamplate(self,imgscr,imgtemplate):
        try:
            img = self.cropTemplateImg(cv.imread(imgscr))
            cv.imshow('crop',img)
            cv.waitKey(0)
            template = cv.imread(imgtemplate)
            # return self.findTemplateMatching(img,imgtemplate)
            return self.findTemplateMatching(img,template)
        except:
            return False






if __name__ == '__main__':

    proc = Matching(1)

    templateName = r"F:\VR20_TNR_Verify\config\model.png"
    imgName = r"F:\VR20_TNR_Verify\config\pic.png"

 
    find = proc.matchTamplate(imgName,templateName)
    cv.imshow('imgMat',find[1])
    cv.waitKey(0)
  

