"""Human-approved metadata and editor-handoff records for Stock Photo Scout."""
from __future__ import annotations
from dataclasses import asdict,dataclass,replace
import json,os,tempfile
from pathlib import Path,PureWindowsPath
from typing import Final,Literal
PREPARATION_SCHEMA_VERSION:Final[int]=1
SubmissionRoute=Literal["undecided","commercial","editorial"]
EditorTarget=Literal["none","darktable","rawtherapee","gimp","other"]
_ROUTES=frozenset({"undecided","commercial","editorial"});_EDITORS=frozenset({"none","darktable","rawtherapee","gimp","other"})
_PREPARATION_FIELDS=frozenset({"relative_path","title","description","keywords","categories","category_pairs","route","editor_target","working_export_relative_path","notes"})
@dataclass(frozen=True)
class CategoryPair:
 category:str;subcategory:str=""
 def __post_init__(self):
  if not isinstance(self.category,str) or not self.category.strip():raise ValueError("Category pair requires a category.")
  if not isinstance(self.subcategory,str):raise TypeError("Category-pair subcategory must be text.")
@dataclass(frozen=True)
class PreparationRecord:
 relative_path:str;title:str="";description:str="";keywords:tuple[str,...]=();categories:tuple[str,...]=();category_pairs:tuple[CategoryPair,...]=();route:SubmissionRoute="undecided";editor_target:EditorTarget="none";working_export_relative_path:str="";notes:str=""
 def __post_init__(self):
  _validate_relative_path(self.relative_path,"relative_path")
  if self.working_export_relative_path:_validate_relative_path(self.working_export_relative_path,"working_export_relative_path")
  if self.route not in _ROUTES:raise ValueError("route must use a supported human choice.")
  if self.editor_target not in _EDITORS:raise ValueError("editor_target must use a supported value.")
  for value,label in ((self.title,"title"),(self.description,"description"),(self.notes,"notes")):
   if not isinstance(value,str):raise TypeError(f"{label} must be text.")
  for values,label in ((self.keywords,"keywords"),(self.categories,"categories")):
   if not isinstance(values,tuple) or any(not isinstance(value,str) for value in values):raise TypeError(f"{label} must be a tuple of text values.")
  if not isinstance(self.category_pairs,tuple) or any(not isinstance(value,CategoryPair) for value in self.category_pairs):raise TypeError("category_pairs must contain CategoryPair values.")
  if len(self.category_pairs)>3:raise ValueError("Dreamstime preparation supports at most three category pairs.")
@dataclass(frozen=True)
class PreparationPrompt:code:str;explanation:str
@dataclass(frozen=True)
class PreparationReport:relative_path:str;prompts:tuple[PreparationPrompt,...]
def edit_preparation(record:PreparationRecord,**changes)->PreparationRecord:return replace(record,**changes)
def evaluate_preparation(record:PreparationRecord)->PreparationReport:
 prompts=[]
 if not record.title.strip():prompts.append(PreparationPrompt("title_missing","Add a factual human-approved title."))
 if not record.description.strip():prompts.append(PreparationPrompt("description_missing","Add a factual human-approved description."))
 clean_keywords=[v.strip() for v in record.keywords if v.strip()]
 if not clean_keywords:prompts.append(PreparationPrompt("keywords_missing","Add human-reviewed descriptive keywords."))
 if any(not v.strip() for v in record.keywords):prompts.append(PreparationPrompt("blank_keywords","Remove blank keyword entries."))
 if any(not v.strip() for v in record.categories):prompts.append(PreparationPrompt("blank_categories","Remove blank category entries."))
 if record.route=="undecided":prompts.append(PreparationPrompt("route_undecided","Choose commercial or editorial manually using current marketplace requirements and the image context."))
 if record.editor_target!="none" and not record.working_export_relative_path:prompts.append(PreparationPrompt("working_export_missing","An editor is selected but no derived working-export path has been recorded."))
 if len({v.casefold() for v in clean_keywords})!=len(clean_keywords):prompts.append(PreparationPrompt("duplicate_keywords","Remove duplicate keywords after human review."))
 return PreparationReport(record.relative_path,tuple(prompts))
def preparation_to_json(record:PreparationRecord)->str:
 return json.dumps({"schema_version":PREPARATION_SCHEMA_VERSION,"preparation":asdict(record)},ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def preparation_from_json(serialized:str)->PreparationRecord:
 payload=json.loads(serialized)
 if not isinstance(payload,dict) or set(payload)!={"schema_version","preparation"} or payload.get("schema_version")!=PREPARATION_SCHEMA_VERSION or not isinstance(payload.get("preparation"),dict):raise ValueError("Preparation JSON does not match the supported schema.")
 item=payload["preparation"]
 if set(item)-_PREPARATION_FIELDS:raise ValueError("Preparation JSON contains unsupported fields.")
 if "relative_path" not in item:raise ValueError("Preparation JSON requires relative_path.")
 keywords=item.get("keywords",[]);categories=item.get("categories",[]);pairs=item.get("category_pairs",[])
 if not isinstance(keywords,list) or not all(isinstance(x,str) for x in keywords):raise ValueError("Preparation keywords must be a list of strings.")
 if not isinstance(categories,list) or not all(isinstance(x,str) for x in categories):raise ValueError("Preparation categories must be a list of strings.")
 if not isinstance(pairs,list) or not all(isinstance(x,dict) for x in pairs):raise ValueError("Preparation category pairs must be objects.")
 parsed=[]
 for pair in pairs:
  if set(pair)-{"category","subcategory"} or "category" not in pair:raise ValueError("Preparation category pairs contain unsupported or missing fields.")
  try:parsed.append(CategoryPair(pair["category"],pair.get("subcategory","")))
  except (TypeError,ValueError) as exc:raise ValueError("Preparation category pairs must contain category and optional subcategory text.") from exc
 try:return PreparationRecord(relative_path=item["relative_path"],title=item.get("title",""),description=item.get("description",""),keywords=tuple(keywords),categories=tuple(categories),category_pairs=tuple(parsed),route=item.get("route","undecided"),editor_target=item.get("editor_target","none"),working_export_relative_path=item.get("working_export_relative_path",""),notes=item.get("notes",""))
 except (TypeError,ValueError) as exc:raise ValueError("Preparation JSON fields are invalid.") from exc
def category_pair_from_text(value:str)->CategoryPair:
 if not isinstance(value,str):raise TypeError("Category pair must be text.")
 category,separator,subcategory=value.partition("::")
 if not category.strip():raise ValueError("Category pair must start with a category before '::'.")
 return CategoryPair(category.strip(),subcategory.strip() if separator else "")
def save_preparation_json(record:PreparationRecord,destination:str|Path,source_root:str|Path,*,overwrite:bool=False)->Path:
 root=Path(source_root).expanduser().resolve(strict=True);target=Path(destination).expanduser().resolve(strict=False)
 if target.suffix.lower()!=".json":raise ValueError("Preparation destination must use a .json suffix.")
 if target.is_relative_to(root):raise ValueError("Refusing to write preparation state inside the selected source-photo folder.")
 target.parent.mkdir(parents=True,exist_ok=True);serialized=preparation_to_json(record)
 if not overwrite:
  with target.open("x",encoding="utf-8",newline="\n") as output:output.write(serialized);output.flush();os.fsync(output.fileno())
  return target
 if target.is_symlink() or not target.is_file():raise FileNotFoundError("Existing regular preparation file not found.")
 temp=None
 try:
  with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",dir=target.parent,prefix=f".{target.stem}.",suffix=".tmp",delete=False) as output:output.write(serialized);output.flush();os.fsync(output.fileno());temp=Path(output.name)
  os.replace(temp,target)
 finally:
  if temp is not None and temp.exists():temp.unlink()
 return target
def _validate_relative_path(value:str,label:str)->None:
 if not isinstance(value,str):raise TypeError(f"{label} must be text.")
 native=Path(value);windows=PureWindowsPath(value)
 if not value or native.is_absolute() or native.drive or windows.is_absolute() or windows.drive or ".." in native.parts or ".." in windows.parts:raise ValueError(f"{label} must be a safe relative path.")
