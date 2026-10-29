"""Figure 4 model lines: explicit marker masks and independent guide checks."""
from pathlib import Path
import csv,json,hashlib
import cv2,numpy as np
P=Path(__file__).resolve().parent
im=cv2.imread(str(P/'source-figure4.png'));hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
# Manually inspected center guides follow model strokes, never marker centers.
series={
313:dict(guide=[[306,264],[321,239],[339,211],[357,183],[377,153],[397,123],[416,99],[432,85]],markers=[[340,233],[351,202],[367,156],[387,113],[396,99],[413,76],[418,69],[432,53]],color='black'),
333:dict(guide=[[285,231],[302,209],[323,181],[343,155],[363,129],[385,105],[405,82],[418,69]],markers=[[285,260],[322,207],[343,169],[353,146],[371,113],[381,95],[418,46]],color='gray'),
373:dict(guide=[[184,274],[205,242],[226,211],[247,182],[270,151],[295,121],[320,93],[345,69],[371,46]],markers=[[183,228],[235,182],[276,144],[309,110],[312,103],[324,95],[345,73],[369,49],[371,44]],color='orange'),
393:dict(guide=[[162,244],[182,209],[205,170],[233,130],[257,109],[279,90],[310,64],[325,53],[351,32]],markers=[[161,198],[203,158],[233,130],[279,90],[325,53],[351,32]],color='green')}
rows=[];qa=[];overlay=im.copy();maskim=np.zeros(im.shape[:2],np.uint8)
for T,s in series.items():
 g=np.array(s['guide']);lo,hi=int(g[0,0]),int(g[-1,0]);mask=np.zeros(im.shape[:2],np.uint8)
 for q in series.values():
  for x,y in q['markers']:cv2.circle(mask,(x,y),8,255,-1);cv2.circle(overlay,(x,y),8,(255,0,255),1)
 maskim|=mask
 if T==373:color=cv2.inRange(hsv,np.array([8,100,90]),np.array([25,255,255]))>0
 elif T==393:color=cv2.inRange(hsv,np.array([30,80,70]),np.array([85,255,255]))>0
 elif T==313:color=(im.max(axis=2)<115)
 else:color=(im.max(axis=2)-im.min(axis=2)<15)&(im.mean(axis=2)>80)&(im.mean(axis=2)<210)
 xs=[];ys=[]
 for x in range(lo,hi+1):
  y=np.interp(x,g[:,0],g[:,1]);width=20 if T==333 else 9;iy=np.arange(max(2,int(y)-width),min(280,int(y)+width+1));v=iy[color[iy,x]&(mask[iy,x]==0)]
  if len(v):xs.append(x);ys.append(float(np.median(v)))
 xs=np.array(xs);ys=np.array(ys)
 # Interpolate only the intervals where symbols obscure the line. No extrapolation.
 checks=[]
 for x,y in s['markers']:
  if xs[0]<=x<=xs[-1]:
   actual=np.interp(x,xs,ys)
   near=np.argsort(abs(xs-x))[:24];poly=np.polyfit(xs[near]-x,ys[near],2);independent=float(poly[-1])
   checks.append(dict(marker_x=x,marker_y=y,line_y=actual,local_quadratic_y=independent,difference_pixels=actual-independent))
 # 5 pixels includes stroke/axis and crossing interpolation error; x uncertainty 1 pixel (reported separately).
 for x in range(int(xs[0]),int(xs[-1])+1):
  y=float(np.interp(x,xs,ys));loading=(x-108)*1.5/374;bar=10**((281-y)/148)
  rows.append(dict(T_K=T,x_pixel=x,y_pixel=y,loading=loading,pressure_bar=bar,pressure_lower_bar=bar/10**(5/148),pressure_upper_bar=bar*10**(5/148),masked_interpolation=bool(mask[round(y),x])))
  cv2.circle(overlay,(x,round(y)),1,(255,0,0),-1)
 qa.append(dict(T_K=T,guide=s['guide'],marker_centers=s['markers'],mask_radius_pixels=8,unmasked_columns=len(xs),crossing_checks=checks,max_crossing_lane_difference_pixels=max([abs(c['difference_pixels']) for c in checks],default=0),classification='review',reason='Masked line pixels; linear gap interpolation checked against local quadratic fit to nearest 24 unmasked columns. Guides only restrict search; uncertainty is a conservative image-reading bound, not statistical confidence'))
with (P/'figure4-lines.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
cv2.imwrite(str(P/'figure4-overlay.png'),overlay);cv2.imwrite(str(P/'figure4-marker-mask.png'),maskim)
(P/'figure4-metadata.json').write_text(json.dumps(dict(source='Bülow 2021 E48WQBPB printed p.6332 Fig.4 embedded image xref281 500x364; source hash in ../sources.json',source_image_sha256=hashlib.sha256((P/'source-figure4.png').read_bytes()).hexdigest(),calibration=dict(x_pixels=[108,482],loading=[0,1.5],y_pixels=[281,133],pressure_bar=[1,10],y_scale='log10'),uncertainty=dict(y_pixels=5,pressure_relative_upper=10**(5/148)-1,x_pixels=1,loading=.004011),curves=qa,caption_text_conflict='Axis and caption CO2 partial pressure; adjacent prose system pressure. Compare both observables; do not relabel.'),indent=2)+'\n')
print(qa)
