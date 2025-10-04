import os
import pickle
from rapidfuzz import process, fuzz
import time
from .logger import logger

class FootprintFinder:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FootprintFinder, cls).__new__(cls)
        return cls._instance

    def __init__(self, footprint_dir="/usr/share/kicad/footprints", cache_ttl_seconds=86400): # 24 hours
        if hasattr(self, 'initialized') and self.initialized:
            return

        self.footprint_dir = footprint_dir
        self.cache_ttl = cache_ttl_seconds
        self.cache_dir = os.path.expanduser("~/.cache/spec_to_symbol")
        self.cache_path = os.path.join(self.cache_dir, "footprints.pkl")
        self.footprints = []
        self.initialized = False

    def _ensure_cache_dir_exists(self):
        os.makedirs(self.cache_dir, exist_ok=True)

    def _load_from_cache(self):
        if not os.path.exists(self.cache_path):
            logger.info("Footprint cache not found.")
            return False
        
        cache_age = time.time() - os.path.getmtime(self.cache_path)
        if cache_age > self.cache_ttl:
            logger.info(f"Footprint cache is stale (age: {cache_age:.0f}s).")
            return False
            
        try:
            logger.info(f"Loading footprints from cache: {self.cache_path}")
            with open(self.cache_path, "rb") as f:
                self.footprints = pickle.load(f)
            logger.info(f"Loaded {len(self.footprints)} footprints from cache.")
            return True
        except (pickle.UnpicklingError, EOFError, IOError) as e:
            logger.warning(f"Could not load footprint cache: {e}")
            return False

    def _save_to_cache(self):
        try:
            self._ensure_cache_dir_exists()
            logger.info(f"Saving {len(self.footprints)} footprints to cache: {self.cache_path}")
            with open(self.cache_path, "wb") as f:
                pickle.dump(self.footprints, f)
            logger.info("Cache saved successfully.")
        except IOError as e:
            logger.error(f"Failed to save footprint cache: {e}")

    def scan(self, force_rescan=False):
        if not force_rescan and self._load_from_cache():
            self.initialized = True
            return

        logger.info("No valid cache found. Starting new footprint scan.")
        new_footprints = []
        if not os.path.isdir(self.footprint_dir):
            self.footprints = []
            self.initialized = True
            logger.warning(f"Footprint directory not found: {self.footprint_dir}")
            return

        for root, dirs, files in os.walk(self.footprint_dir):
            dirs[:] = [d for d in dirs if d != 'plugins']
            for file in files:
                if file.endswith(".kicad_mod"):
                    rel_path = os.path.relpath(os.path.join(root, file), self.footprint_dir)
                    lib_name = os.path.basename(os.path.dirname(rel_path)).replace('.pretty', '')
                    fp_name = os.path.splitext(os.path.basename(rel_path))[0]
                    new_footprints.append(f"{lib_name}:{fp_name}")
        
        self.footprints = new_footprints
        self._save_to_cache()
        self.initialized = True
        logger.info(f"Footprint scan complete. Found {len(self.footprints)} footprints.")

    def find(self, query: str, limit=20):
        if not self.initialized:
            self.scan()
        if not query or not self.footprints:
            return []
        results = process.extract(query, self.footprints, scorer=fuzz.WRatio, limit=limit)
        return [result[0] for result in results]

footprint_finder = FootprintFinder()
