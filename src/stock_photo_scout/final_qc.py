"""Final-export QC facts and deterministic actual-pixel crop planning."""
from dataclasses import dataclass
@dataclass(frozen=True)
class InspectionCrop: label:str; left:int; top:int; width:int; height:int
@dataclass(frozen=True)
class FinalExportFacts:
    width_pixels:int; height_pixels:int; format_name:str; color_space:str="unknown"
    @property
    def pixel_count(self): return self.width_pixels*self.height_pixels
def plan_100_percent_crops(width:int,height:int,*,crop_size:int=1024)->tuple[InspectionCrop,...]:
    for value,name in ((width,"width"),(height,"height"),(crop_size,"crop_size")):
        if not isinstance(value,int) or isinstance(value,bool) or value<1: raise ValueError(f"{name} must be a positive integer")
    cw,ch=min(crop_size,width),min(crop_size,height)
    positions=(("top-left",0,0),("top-right",width-cw,0),("centre",max(0,(width-cw)//2),max(0,(height-ch)//2)),("bottom-left",0,height-ch),("bottom-right",width-cw,height-ch))
    seen=set(); out=[]
    for label,left,top in positions:
        key=(left,top,cw,ch)
        if key not in seen: seen.add(key); out.append(InspectionCrop(label,left,top,cw,ch))
    return tuple(out)
def validate_final_export_facts(f:FinalExportFacts)->None:
    if not isinstance(f.width_pixels,int) or isinstance(f.width_pixels,bool) or f.width_pixels<1: raise ValueError("width_pixels must be positive")
    if not isinstance(f.height_pixels,int) or isinstance(f.height_pixels,bool) or f.height_pixels<1: raise ValueError("height_pixels must be positive")
    if not f.format_name.strip(): raise ValueError("format_name is required")
