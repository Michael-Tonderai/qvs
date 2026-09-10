# qualifications/forms.py
#
# REQ-F-003 - the input surface for registering a qualification record.
#
# The assignment brief asks for validation rules as a distinct piece of evidence
# alongside test cases and quality gates, so the rules here are deliberately explicit
# and each one is tested.

from datetime import timedelta

from django import forms
from django.utils import timezone

from qualifications.models import Qualification

# One day of tolerance on the future-date check, and the reason is not laziness.
#
# TIME_ZONE is UTC by decision - REQ-F-007 needs an audit trail whose timestamps do not
# shift with a server's local zone. Harare is UTC+2, so between midnight and 02:00
# local the UTC date is still yesterday. A registrar working late who enters today's
# date would be told it is in the future, which is both wrong and baffling.
#
# The check exists to catch a mistyped year, and it still does that with a day of slack.
# Tightening it to the exact UTC date would trade a real class of false rejection for
# no additional protection against the error it is actually for.
AWARD_DATE_FUTURE_TOLERANCE = timedelta(days=1)


class QualificationForm(forms.ModelForm):
    """Collects the four facts a registrar supplies about a qualification.

    certificate_id, issued_at, issued_by and signature are absent by construction, not
    by omission - they are `editable=False` on the model, so ModelForm will not build
    fields for them whatever is listed here. A future edit to this class cannot
    accidentally expose them.
    """

    class Meta:
        model = Qualification
        fields = [
            "holder_name",
            "institution",
            "qualification_title",
            "award_date",
        ]
        widgets = {
            # type="date" gives the browser's native date picker and, more usefully,
            # guarantees the submitted value is ISO 8601 rather than whatever the
            # user's locale suggests. 03/04/2026 is two different dates depending on
            # which side of the Atlantic typed it, and a qualification record is not a
            # place to guess.
            "award_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def clean_award_date(self):
        """Reject award dates that cannot have happened yet.

        The cheapest possible check against the most likely data-entry error, a
        mistyped year, and a validation rule the technical report can point at.

        Deliberately not a range check with a lower bound. Institutions issue
        qualifications with historical award dates, and a system that refuses to
        register a 1974 degree because someone picked an arbitrary floor is wrong in a
        way that is harder to notice than the error it prevents.
        """
        award_date = self.cleaned_data["award_date"]
        latest_plausible = timezone.localdate() + AWARD_DATE_FUTURE_TOLERANCE
        if award_date > latest_plausible:
            raise forms.ValidationError(
                "The award date cannot be in the future.",
                code="award_date_in_future",
            )
        return award_date
