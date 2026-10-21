"""Launch the local Stock Photo Scout 0.07 human-review dashboard."""
from pathlib import Path
import argparse
import sys

PROJECT_ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT_ROOT/"src"))
from stock_photo_scout.review_server import serve_review_dashboard

def main():
    p=argparse.ArgumentParser(description="Serve Stock Photo Scout 0.07 human review on localhost only.")
    p.add_argument("source_root",type=Path,help="Read-only source-photo root; photos are never served by this dashboard.")
    p.add_argument("--review-directory",type=Path,default=Path("local_review"),help="External local directory for review JSON.")
    p.add_argument("--port",type=int,default=8766)
    a=p.parse_args()
    serve_review_dashboard(a.source_root,a.review_directory,a.port)

if __name__=="__main__":main()
