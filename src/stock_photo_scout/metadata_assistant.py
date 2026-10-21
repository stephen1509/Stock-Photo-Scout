"""0.08 deterministic metadata assistance from human-supplied facts.

This module does not inspect image pixels, invent facts, generate marketplace
claims, or auto-approve metadata. It reports omissions, duplicates and simple
human-review prompts from already-entered factual text.
"""
from __future__ import annotations
from dataclasses import dataclass
import re
from .preparation import PreparationRecord
_WORD=re.compile(r"[\w'-]+",re.UNICODE)
@dataclass(frozen=True)
class MetadataObservation:
 code:str
 explanation:str
@dataclass(frozen=True)
class MetadataReview:
 observations:tuple[MetadataObservation,...]
 normalized_keyword_suggestions:tuple[str,...]

def review_metadata(record:PreparationRecord)->MetadataReview:
 if not isinstance(record,PreparationRecord):raise ValueError("record must be PreparationRecord")
 observations=[];suggestions=[];seen=set()
 title=record.title.strip();description=record.description.strip()
 if title and description and title.casefold()==description.casefold():observations.append(MetadataObservation("title-description-identical","Title and description are identical; review whether the description can add factual context."))
 for raw in record.keywords:
  clean=" ".join(raw.split())
  if not clean:continue
  key=clean.casefold()
  if key in seen:continue
  seen.add(key);suggestions.append(clean)
 if len(suggestions)!=len([x for x in record.keywords if x.strip()]):observations.append(MetadataObservation("keyword-duplicates","Duplicate or whitespace-equivalent keywords are present."))
 factual=(title+" "+description).casefold()
 uncovered=[]
 for token in _WORD.findall(title):
  t=token.casefold()
  if len(t)>=4 and not any(t in k.casefold().split() for k in suggestions):uncovered.append(token)
 if uncovered:observations.append(MetadataObservation("title-terms-not-keywords","Some meaningful title terms are not represented as exact keyword words: "+", ".join(dict.fromkeys(uncovered))+". Review manually; do not add irrelevant keywords."))
 if record.route=="undecided":observations.append(MetadataObservation("route-undecided","Commercial/editorial route is undecided; metadata wording should not be finalized as marketplace-ready."))
 if not factual.strip():observations.append(MetadataObservation("facts-missing","No title/description facts are available for metadata review."))
 return MetadataReview(tuple(observations),tuple(suggestions))
