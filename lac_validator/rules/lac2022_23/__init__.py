from pathlib import Path

__all__ = [p.stem for p in Path(__file__).parent.glob("*.py") if p.stem != "__init__"]

# TODO now this line has to be commented for tests to run and uncommented for validation to run.
# else it loads the registry twice and says that the rules are duplicates.
# from . import *