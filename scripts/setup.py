# scripts/setup.py
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import SessionLocal
from src.database.models import Xasida, Version
from src.database.qdrant import get_client, ensure_collection
from src.services.indexer import index_version

db = SessionLocal()
client = get_client()
ensure_collection(client)

# Créer les xasidas
jeuzbou = Xasida(og_name="Jëzbul Xuluub", aka_name="Jëzbu", author="Cheikh Ahmadou Bamba")
mawahibou = Xasida(og_name="Mawahibun Naafih", aka_name="Mawahibu", author="Cheikh Ahmadou Bamba")
db.add_all([jeuzbou, mawahibou])
db.commit()

# Créer les versions + indexer
for xasida, path in [(jeuzbou, "data/jezbu/jezbu_78.mp3"), (mawahibou, "data/mawahibu/mawahibu_serigne_mayib.mp3")]:
    v = Version(xasida_id=xasida.id, audio_path=path)
    db.add(v)
    db.commit()
    n = index_version(client, db, v)
    print(f"{xasida.aka_name} → {n} segments indexés")

db.close()
