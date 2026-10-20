"""Compatibility entry point; regression tests live in tests/.

Unconverged steady iteration averages are not accepted physical polar data.
"""
from integrate_cfd_polars import main

if __name__ == "__main__":
    main()
