"""Definitions shared by build_component_tables_from_api.py and check_component_tables.py."""
import csv
import html
import json
import re

# API report section -> section name in field_map.csv
SEG = {
    "field_foia_requests_va": "ProcessedRequestSection",
    "field_foia_requests_vb1": "RequestDispositionSection",
    "field_foia_requests_vb2": "RequestDenialOtherReasonSection",
    "field_foia_requests_vb3": "RequestDispositionAppliedExemptionsSection",
    "field_statute_iv": "Exemption3StatuteSection",
    "field_admin_app_via": "ProcessedAppealSection",
    "field_admin_app_vib": "AppealDispositionSection",
    "field_admin_app_vic1": "AppealDispositionAppliedExemptionsSection",
    "field_admin_app_vic2": "AppealNonExemptionDenialSection",
    "field_admin_app_vic3": "AppealDenialOtherReasonSection",
    "field_admin_app_vic4": "AppealResponseTimeSection",
    "field_admin_app_vic5": "OldestPendingAppealSection",
    "field_proc_req_viia": "ProcessedResponseTimeSection",
    "field_proc_req_viib": "InformationGrantedResponseTimeSection",
    "field_proc_req_viic1": "SimpleResponseTimeIncrementsSection",
    "field_proc_req_viic2": "ComplexResponseTimeIncrementsSection",
    "field_proc_req_viic3": "ExpeditedResponseTimeIncrementsSection",
    "field_pending_requests_vii_d_": "PendingPerfectedRequestsSection",
    "field_admin_app_viie": "OldestPendingRequestSection",
    "field_req_viiia": "ExpeditedProcessingSection",
    "field_req_viiib": "FeeWaiverSection",
    "field_foia_pers_costs_ix": "PersonnelAndCostSection",
    "field_fees_x": "FeesCollectedSection",
    "field_sub_xia": "SubsectionUsedSection",
    "field_sub_xib": "SubsectionPostSection",
    "field_foia_xiia": "BacklogSection",
    "field_foia_xiib": "ProcessedConsultationSection",
    "field_foia_xiic": "OldestPendingConsultationSection",
    "field_foia_xiid1": "ProcessedRequestComparisonSection",
    "field_foia_xiid2": "BackloggedRequestComparisonSection",
    "field_foia_xiie1": "ProcessedAppealComparisonSection",
    "field_foia_xiie2": "BackloggedAppealComparisonSection",
}

# the two "other reasons" sections keep their records one level deeper
NESTED = {"field_foia_requests_vb2": "field_foia_req_vb2_info", "field_admin_app_vic3": "field_admin_app_vic3_info"}

# section -> data type number and short name, as in the column names (e.g. 01_Requests__...)
SECTIONS = [
    ("ProcessedRequestSection", "01", "Requests"),
    ("RequestDispositionSection", "02", "Disposition"),
    ("RequestDenialOtherReasonSection", "03", "DispositionOtherReasons"),
    ("ExpeditedProcessingSection", "04", "ExpeditedProcessing"),
    ("RequestDispositionAppliedExemptionsSection", "05", "Exemptions"),
    ("ProcessedAppealSection", "07", "Appeals"),
    ("AppealDispositionSection", "08", "AppealsDisposition"),
    ("AppealDispositionAppliedExemptionsSection", "09", "AppealsExemptions"),
    ("AppealNonExemptionDenialSection", "10", "AppealsOtherThanExemptions"),
    ("AppealDenialOtherReasonSection", "11", "AppealsOtherReasons"),
    ("AppealResponseTimeSection", "12", "AppealsResponseTime"),
    ("OldestPendingAppealSection", "13", "AppealsTenOldest"),
    ("ProcessedResponseTimeSection", "14", "ProcessingTime"),
    ("InformationGrantedResponseTimeSection", "15", "ProcessingTimeGranted"),
    ("SimpleResponseTimeIncrementsSection", "16", "SimpleRequests"),
    ("ComplexResponseTimeIncrementsSection", "17", "ComplexRequests"),
    ("ExpeditedResponseTimeIncrementsSection", "18", "ExpeditedRequests"),
    ("PendingPerfectedRequestsSection", "19", "PendingRequests"),
    ("OldestPendingRequestSection", "20", "TenOldestRequests"),
    ("FeeWaiverSection", "21", "FeeWaiver"),
    ("PersonnelAndCostSection", None, None),  # its columns belong to 22 (personnel) or 23 (costs)
    ("FeesCollectedSection", "23", "Costs"),
    ("SubsectionUsedSection", "24", "Exclusions"),
    ("SubsectionPostSection", "25", "ProactiveDisclosures"),
    ("BacklogSection", "26", "Backlog"),
    ("ProcessedConsultationSection", "27", "Consultations"),
    ("OldestPendingConsultationSection", "28", "ConsultationsTenOldest"),
    ("ProcessedRequestComparisonSection", "29", "Comparisons"),
    ("BackloggedRequestComparisonSection", "30", "ComparisonsRequestsBacklogged"),
    ("ProcessedAppealComparisonSection", "31", "ComparisonsAppeals"),
    ("BackloggedAppealComparisonSection", "32", "ComparisonsAppealsBacklogged"),
]

ws = lambda s: re.sub(r"\s+", " ", (s or "")).strip()  # one space between words


def val(v):
    """A record value as text ("" when missing)."""
    if isinstance(v, dict):
        v = v.get("value")
    return "" if v is None else ws(str(v))


def load_maps(field_map, data_map):
    """(section, API field) -> column field, and (section, column field) -> the API field of the agency total."""
    fmap = {(r["section"], r["api_field"]): r["field"] for r in csv.DictReader(open(field_map, newline=""))}
    overall = {}
    for g in json.load(open(data_map)):
        for f in g["fields"]:
            if not f.get("overall_field") or "." not in f["id"]:
                continue
            seg, fld = f["id"].split(".", 1)
            sec = SEG.get(seg)
            if sec and (sec, fld) in fmap:
                overall[(sec, fmap[(sec, fld)])] = f["overall_field"]
    return fmap, overall


def _kind(col):
    col = col.split("[")[0]  # coded columns such as OtherDenialReasonQuantity[...]: the part before the bracket
    if col.endswith("Date"):
        return "date"
    if col.endswith("Text"):
        return "text"
    if col.endswith("DaysValue") or col.endswith("PendingDaysQuantity"):
        return "days"  # AdjudicationWithinTenDaysQuantity is a count
    if col.endswith("Percent"):
        return "percent"
    if col.endswith("Amount"):
        return "money"
    if "FullTime" in col:
        return "fte"
    if col.endswith("Quantity") or "Quantity[" in col:
        return "count"
    return "text"


def summable(col):
    """Can the column be added up across components? Counts, dollars and staff yes; days and percents no."""
    return _kind(col) in ("count", "money", "fte")


# text of the 03/11 reasons and 06 statutes: formatting only, never the content
ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);")
QUOTES = str.maketrans({"“": '"', "”": '"', "„": '"', "″": '"',
                        "‘": "'", "’": "'", "‚": "'", "′": "'"})
NA_SPELLINGS = {"n/a", "na", "n\\a", "n.a."}


def clean_text(v, max_rounds=3):
    """HTML codes (some escaped two or three times), curly quotes, whitespace, and N/A spelling."""
    if v is None:
        return ""
    s = str(v)
    for _ in range(max_rounds):
        if not ENTITY.search(s):
            break
        s = html.unescape(s)
    s = s.translate(QUOTES)
    s = re.sub(r"\s+", " ", s).strip()
    if s.lower() in NA_SPELLINGS:
        s = "N/A"
    return s
