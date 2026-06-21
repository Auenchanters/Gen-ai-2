"""Dataframe engine selection: CPU pandas vs GPU-accelerated cudf.pandas.

The whole pipeline is written in plain pandas. On a CUDA machine we transparently
accelerate it with RAPIDS ``cudf.pandas`` (a drop-in accelerator) so the *same code*
runs an order of magnitude faster on large data. Everywhere else it falls back to CPU
pandas, so the pipeline runs anywhere — including CI with no GPU.

``cudf.pandas`` must be installed before ``pandas`` is imported, so callers run
:func:`maybe_enable_cudf_pandas` at process start (see ``pipeline/accelerate.py``).
"""

from __future__ import annotations

import os


def gpu_available() -> bool:
    """Return ``True`` if the RAPIDS cuDF stack is importable in this process."""
    try:
        import cudf  # noqa: F401  # only present in the GPU environment
    except Exception:
        return False
    return True  # pragma: no cover - GPU only


def maybe_enable_cudf_pandas() -> bool:
    """Enable the cudf.pandas accelerator when ``USE_GPU=1`` and RAPIDS is available.

    Must be called *before* pandas is imported in the current process. Returns whether
    GPU acceleration was actually enabled, so callers can tag their output with the
    engine that ran (``"gpu"`` vs ``"cpu"``).
    """
    if os.environ.get("USE_GPU", "0") != "1":
        return False
    try:  # pragma: no cover - GPU only
        import cudf.pandas

        cudf.pandas.install()
    except Exception:  # pragma: no cover - GPU only
        return False
    return True  # pragma: no cover - GPU only
