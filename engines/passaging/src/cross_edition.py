"""§4.B.4 — Cross-Edition Passage Correspondence. [NOT YET IMPLEMENTED]

When multiple editions of the same work exist in the library,
aligns passages between editions using character n-gram overlap,
division tree matching, and sequential DTW.

Output: CrossEditionMap written to
    library/sources/{source_id}/passages/cross_edition_map.json
"""

from __future__ import annotations
