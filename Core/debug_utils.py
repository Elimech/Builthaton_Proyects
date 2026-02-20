import json
from datetime import datetime

class DebugManager:

    @staticmethod
    def log(stage, data, pretty=True):
        print(f"\n=== DEBUG: {stage} ===")
        
        if isinstance(data, (dict, list)):
            if pretty:
                print(json.dumps(data, indent=2, default=str))
            else:
                print(data)
        else:
            print(data)

    @staticmethod
    def separator():
        print("\n" + "=" * 50 + "\n")
