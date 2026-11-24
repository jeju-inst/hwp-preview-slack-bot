"""Guards issue #2: skip converting an HWP when the same message already has
a PDF with the same name (extension aside).

Names are compared after NFC normalization and casefolding, since Korean
filenames from macOS arrive in NFD and extensions vary in case.
"""

import unicodedata

from hwp_preview_slack_bot.__main__ import _has_sibling_pdf


def _files(*names):
    return [{"name": n} for n in names]


def test_same_name_pdf_detected():
    assert _has_sibling_pdf("문서.hwpx", _files("문서.hwpx", "문서.pdf")) is True


def test_nfd_pdf_matches_nfc_hwpx():
    nfd_pdf = unicodedata.normalize("NFD", "보고서 초안.pdf")
    nfc_hwp = unicodedata.normalize("NFC", "보고서 초안.hwpx")
    assert nfd_pdf != "보고서 초안.pdf"  # sanity: really decomposed
    assert _has_sibling_pdf(nfc_hwp, _files(nfc_hwp, nfd_pdf)) is True


def test_nfd_hwp_matches_nfc_pdf():
    nfd_hwp = unicodedata.normalize("NFD", "보고서.hwp")
    assert _has_sibling_pdf(nfd_hwp, _files(nfd_hwp, "보고서.pdf")) is True


def test_case_insensitive():
    assert _has_sibling_pdf("Report.HWPX", _files("Report.HWPX", "report.PDF")) is True


def test_differently_named_pdf_does_not_skip():
    assert _has_sibling_pdf("문서.hwpx", _files("문서.hwpx", "다른문서.pdf")) is False


def test_no_pdf_does_not_skip():
    assert _has_sibling_pdf("문서.hwpx", _files("문서.hwpx", "문서.docx", "문서.hwp")) is False


def test_empty_or_missing_files():
    assert _has_sibling_pdf("문서.hwpx", []) is False
    assert _has_sibling_pdf("문서.hwpx", None) is False
    assert _has_sibling_pdf("문서.hwpx", [{}]) is False


def test_stem_must_match_exactly():
    # A prefix/suffix overlap is not "the same name".
    assert _has_sibling_pdf("문서.hwpx", _files("문서_최종.pdf", "최종문서.pdf")) is False
