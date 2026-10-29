"""Figure 4 orange line: retain largest connected orange trace, discard detached markers."""
import cv2,json,numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
im=cv2.imread(str(p/'figure4.png'));hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
m=cv2.inRange(hsv,np.array([8,120,110]),np.array([25,255,255]));m[:27,:]=0;m[279:,:]=0;m[:,:112]=0;m[:,375:]=0
n,labels,stats,c=cv2.connectedComponentsWithStats(m)
i=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);out=np.full_like(im,255);out[labels==i]=im[labels==i]
cv2.imwrite(str(p/'figure4-orange-trace.png'),out)
print(stats[i].tolist())
