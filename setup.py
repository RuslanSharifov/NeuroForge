"""Interactive NeuroForge first-run setup. Always requests permission to install."""
from doctor import main
import sys
if __name__=="__main__":
    sys.argv=[sys.argv[0],"--install","--check-updates"]
    raise SystemExit(main())
