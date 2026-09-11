# qualifications/signing.py
#
# REQ-F-001 - unique, non-guessable certificate IDs.
# REQ-F-002 - HMAC-SHA256 signatures over a record's canonical fields at issue.
#
# Deliberately a plain module with no model import and no Django ORM dependency. It is
# pure functions over dictionaries, so it can be unit tested without a database and
# without a request cycle (D-004), and so the Qualification model in REQ-F-003 can call
# it rather than the two being entangled.

import hmac
import json
import secrets
from collections.abc import Mapping
from hashlib import sha256
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# --- Certificate identifiers (REQ-F-001) ------------------------------------------

# Crockford's base32 alphabet with the ambiguous characters removed: no I or L (read as
# 1), no O (read as 0), no U (turns some random strings into words nobody wants printed
# on a certificate), and no 0 or 1 for the same reason in reverse. Thirty symbols.
#
# The exclusions cost entropy and buy correctness. A certificate ID is not an internal
# key - REQ-F-005 has a human reading one off a document and typing it into a
# verification form, and a character pair that is routinely misread turns a VERIFIED
# record into a NOT FOUND, which is a false negative in the one place this system
# exists to be right about.
CERTIFICATE_ID_ALPHABET = "23456789ABCDEFGHJKMNPQRSTVWXYZ"

CERTIFICATE_ID_PREFIX = "QVS"
CERTIFICATE_ID_GROUP_SIZE = 4
CERTIFICATE_ID_GROUPS = 4

# 16 characters drawn from 30 symbols is log2(30) * 16, about 78 bits. Non-guessable in
# the sense REQ-F-001 needs: an attacker who knows the format and can make unlimited
# attempts still cannot enumerate the space, and knowing one issued ID reveals nothing
# about any other.
CERTIFICATE_ID_LENGTH = CERTIFICATE_ID_GROUP_SIZE * CERTIFICATE_ID_GROUPS


def new_certificate_id() -> str:
    """Return a fresh certificate ID, formatted QVS-XXXX-XXXX-XXXX-XXXX.

    Drawn from `secrets`, never from a counter, a timestamp or uuid1. A sequential or
    time-derived identifier tells anyone holding one certificate roughly where the
    others sit, which is precisely what "non-guessable" rules out.

    Uniqueness is a property of the entropy, not of a database check. The model in
    REQ-F-003 still carries a unique constraint, because a collision that does happen
    must fail loudly rather than silently overwrite a record.
    """
    characters = [
        secrets.choice(CERTIFICATE_ID_ALPHABET) for _ in range(CERTIFICATE_ID_LENGTH)
    ]
    groups = [
        "".join(characters[start : start + CERTIFICATE_ID_GROUP_SIZE])
        for start in range(0, CERTIFICATE_ID_LENGTH, CERTIFICATE_ID_GROUP_SIZE)
    ]
    return "-".join([CERTIFICATE_ID_PREFIX, *groups])


# --- Canonical serialisation and signing (REQ-F-002) ------------------------------


def canonical_payload(fields: Mapping[str, Any]) -> bytes:
    """Serialise a record's fields to the exact bytes that get signed.

    Two requirements pull on this function. REQ-F-002 needs the same fields to produce
    the same bytes every time, or a record fails to verify against its own signature.
    REQ-F-006 needs any alteration to produce different bytes, or tampering goes
    undetected.

    JSON with sorted keys satisfies both, and it does so for reasons worth stating:

    - `sort_keys=True` removes dictionary insertion order from the result, so a record
      rebuilt from the database in a different field order still verifies.
    - JSON escapes quotes, newlines and the separators themselves. A naive
      "key=value;key=value" format lets a holder name containing a semicolon serialise
      identically to a different record with different fields - a forgery that needs no
      key at all.
    - `ensure_ascii=True` keeps the output ASCII whatever the input, so the signed bytes
      never depend on how the surrounding system handles encoding (the same reasoning as
      D-018, applied to bytes that must be reproducible rather than merely readable).
    - `separators` without spaces makes the encoding minimal and fixed rather than
      dependent on a library default that could change.

    `default=str` gives dates and other non-JSON types a deterministic representation
    rather than raising. Callers should still pass values already normalised to strings
    where the exact form matters.
    """
    return json.dumps(
        dict(fields),
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    ).encode("ascii")


def _signing_key() -> bytes:
    """Return the HMAC key, or fail loudly.

    Read at call time rather than at import, which is what lets management commands
    unrelated to signing run without the key set - the behaviour config/settings.py
    already describes. There is deliberately no development fallback: a signature made
    under an ephemeral key would verify inside one process and fail in the next, which
    is worse than an error because it looks like tampering.
    """
    key = getattr(settings, "QVS_SIGNING_KEY", "")
    if not key:
        raise ImproperlyConfigured(
            "QVS_SIGNING_KEY must be set before qualification records can be signed "
            "or verified. See .env.example for the variables this project reads."
        )
    return key.encode("utf-8")


def sign(fields: Mapping[str, Any]) -> str:
    """Return the hex HMAC-SHA256 signature over the canonical form of `fields`."""
    return hmac.new(_signing_key(), canonical_payload(fields), sha256).hexdigest()


def verify_signature(fields: Mapping[str, Any], signature: str) -> bool:
    """Return True when `signature` is the signature this system would issue.

    `hmac.compare_digest` rather than `==`. String equality returns as soon as it finds
    a differing character, so the time it takes leaks how many leading characters were
    correct, and an attacker who can measure that can construct a valid signature one
    character at a time without ever knowing the key.

    An empty or absent signature is False rather than an error: REQ-F-005 answers
    VERIFIED, NOT FOUND or TAMPERED, and a record carrying no signature is tampered
    with, not malformed.
    """
    if not signature:
        return False
    return hmac.compare_digest(sign(fields), signature)
