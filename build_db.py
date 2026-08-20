from pathlib import Path
import argparse
from evidence_engine.database import seed_database, counts
from evidence_engine.ingest import refresh_all

ROOT=Path(__file__).resolve().parent
DB=ROOT/"data"/"solar_claim_evidence.db"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--refresh",action="store_true")
    args=parser.parse_args()
    seed_database(DB,ROOT/"data/source_registry.json",ROOT/"data/seed_evidence.json")
    print("Database:",counts(DB))
    if args.refresh:
        results=refresh_all(DB)
        ok=sum(x["status"]=="ok" for x in results)
        print(f"Refreshed {ok}/{len(results)} sources")
        for result in results:
            if result["status"]!="ok": print("ERROR:",result)

if __name__=="__main__":
    main()
