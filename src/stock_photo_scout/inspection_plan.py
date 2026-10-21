"""Subject-aware actual-pixel inspection planning for 0.07.

Coordinates are normalized observations supplied/confirmed by a human. This
module plans inspection; it does not infer a subject or decide image quality.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class SubjectRegion:
 x:float
 y:float
 width:float
 height:float
 label:str=""

@dataclass(frozen=True)
class InspectionRegion:
 name:str
 left:int
 top:int
 right:int
 bottom:int

def _positive_int(v,name):
 if isinstance(v,bool) or not isinstance(v,int) or v<1:raise ValueError(name+" must be a positive integer")

def validate_subject_region(r:SubjectRegion)->None:
 if not isinstance(r,SubjectRegion):raise ValueError("subject must be SubjectRegion")
 for name,v in (("x",r.x),("y",r.y),("width",r.width),("height",r.height)):
  if isinstance(v,bool) or not isinstance(v,(int,float)) or not 0<=v<=1:raise ValueError(name+" must be between 0 and 1")
 if r.width<=0 or r.height<=0 or r.x+r.width>1 or r.y+r.height>1:raise ValueError("subject region must have positive size and remain inside image")
 if not isinstance(r.label,str):raise ValueError("label must be a string")

def subject_inspection_region(image_width:int,image_height:int,subject:SubjectRegion,*,minimum_crop:int=512,padding_ratio:float=.25)->InspectionRegion:
 _positive_int(image_width,"image_width");_positive_int(image_height,"image_height");_positive_int(minimum_crop,"minimum_crop");validate_subject_region(subject)
 if isinstance(padding_ratio,bool) or not isinstance(padding_ratio,(int,float)) or padding_ratio<0 or padding_ratio>2:raise ValueError("padding_ratio must be between 0 and 2")
 cx=(subject.x+subject.width/2)*image_width;cy=(subject.y+subject.height/2)*image_height
 target_w=max(minimum_crop,subject.width*image_width*(1+2*padding_ratio));target_h=max(minimum_crop,subject.height*image_height*(1+2*padding_ratio))
 target_w=min(image_width,int(round(target_w)));target_h=min(image_height,int(round(target_h)))
 left=max(0,min(image_width-target_w,int(round(cx-target_w/2))));top=max(0,min(image_height-target_h,int(round(cy-target_h/2))))
 return InspectionRegion("subject-focus",left,top,left+target_w,top+target_h)
