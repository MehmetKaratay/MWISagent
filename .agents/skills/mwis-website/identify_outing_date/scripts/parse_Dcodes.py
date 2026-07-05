# Copyright (c) 2026 Mehmet Rahmi Karatay
# Licensed under the MIT License.

"""Resolve a target date to its MWIS forecast coverage code."""

import datetime
import os
from typing import Optional


def _get_reference_date() -> datetime.date:
    """Determine the reference date for all calculations, defaulting to today.

    Returns:
        datetime.date: The reference date.
    """
    ref_env = os.environ.get("MWIS_REFERENCE_DATE")
    if ref_env:
        try:
            return datetime.datetime.strptime(ref_env.strip(), "%Y-%m-%d").date()
        except ValueError:
            pass
    return datetime.date.today()


def get_d_code_for_date(
    target: datetime.date, ref_date: Optional[datetime.date] = None
) -> str:
    """Resolve a target date to its MWIS forecast coverage code.

    Args:
        target: The target calendar date to resolve.
        ref_date: The reference date to calculate offsets against. Defaults to today or MWIS_REFERENCE_DATE.

    Returns:
        The matching coverage code string (e.g. 'D0', 'D1', 'Doutlook').
    """
    if ref_date is None:
        ref_date = _get_reference_date()

    delta = (target - ref_date).days
    if delta < 0:
        return "Dold"
    elif delta == 0:
        return "D0"
    elif delta == 1:
        return "D1"
    elif delta == 2:
        return "D2"
    elif delta == 3:
        return "D3"
    elif 4 <= delta <= 7:
        return "Doutlook"
    return "Dfuture"
