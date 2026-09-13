# qualifications/search.py
#
# REQ-F-009 - an authenticated user can search records by certificate ID, holder name
# or institution.
#
# The matching rule lives here rather than in the view, for the reason verification.py
# gives for the same shape: a view can only be tested through a request cycle, and
# "which records match this query" is a question worth answering without one. It also
# means the unit and integration split the assignment assesses separately is a real
# split rather than a label - the matching rules are unit tests, the access control and
# rendering are integration tests.
#
# This module is public-facing in its consequences even though the view above it is not.
# D-040 put both REQ-F-009 and REQ-F-010 behind authentication, so nothing here is
# reachable anonymously; the care taken over what it matches is about not surprising a
# signed-in registrar, not about protecting the index from strangers.

from django.db.models import Q, QuerySet

from qualifications.models import Qualification
from qualifications.verification import normalise_certificate_id

# The most rows a single search will return.
#
# Not pagination. Pagination is a control surface, a page-number parameter to validate
# and a set of edge cases around an empty last page, and no requirement asks for it on
# a demonstration dataset. A cap is one integer and it closes the failure that actually
# matters: a query of a single common letter matching every record in the table and
# rendering all of them into one page.
#
# The view fetches one row beyond this so it can tell a full page from a truncated one
# without a second COUNT query, and says so on screen when the cap is reached. A
# truncated result set that does not admit it is worse than no search at all, because
# the absence of a record then reads as proof it does not exist.
MAX_RESULTS = 50


def find(query: str) -> QuerySet[Qualification]:
    """Return the records matching `query`, newest first.

    One box, three columns. REQ-F-009 says "certificate ID, holder name or institution"
    and the "or" is doing real work: a registrar looking for a record has one string in
    their hand and does not necessarily know which field it belongs to. Three separate
    inputs would make them decide before they are able to.

    The certificate ID arm matches against the normalised query rather than the raw one,
    reusing verification.normalise_certificate_id so that the search box and the
    verification box treat a typed ID identically. Someone who pastes `qvs-test-case`
    out of an email should not get a different answer here than they would there.

    `icontains` on all three arms, deliberately, including the certificate ID. An exact
    match would be the stricter choice and the less useful one - the realistic case is a
    registrar who can read the last group of characters off a damaged or photographed
    document, and a substring finds it. Nothing is exposed by a partial match that a
    full match would not expose, because the caller is authenticated either way.

    A blank query returns nothing rather than everything. An empty box is a question
    nobody has asked yet, which is the same position views.verify takes on an empty
    certificate ID field, and answering it with the entire table would turn the search
    page into the record directory D-040 exists to refuse.

    Ordering comes from Qualification.Meta, which is `-issued_at`: most recently
    registered first. Stated here because it is a property callers depend on and a
    future edit to the model would change it silently.
    """
    query = query.strip()
    if not query:
        return Qualification.objects.none()

    return Qualification.objects.filter(
        Q(certificate_id__icontains=normalise_certificate_id(query))
        | Q(holder_name__icontains=query)
        | Q(institution__icontains=query)
    )
