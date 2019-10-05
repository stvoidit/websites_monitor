from app import manager
from ren_run import *


# 1) dbmig init
# 2) dbmig migrate
# 3) dbmig upgrade
if __name__ == "__main__":
    manager.run()