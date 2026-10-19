"""Offline tests for scripts/edgar.py parsers.  python3 -m unittest discover -s tests"""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import edgar

INDEX = """<div class="formGrouping">
         <div class="infoHead">Filing Date</div>
         <div class="info">2026-10-16</div>
         <div class="infoHead">Accepted</div>
         <div class="info">2026-10-16 16:06:27</div>
         <div class="infoHead">Documents</div>
         <div class="info">14</div>
      </div>
      <div class="formGrouping">
         <div class="infoHead">Period of Report</div>
         <div class="info">2026-10-15</div>
      </div>
      <div class="formGrouping">
         <div class="infoHead">Items</div>
         <div class="info">Item 2.02: Results of Operations and Financial Condition<br />Item 5.02: Departure of Directors &amp; Officers<br />Item 9.01: Financial Statements and Exhibits<br /></div>
      </div>"""

SUBMISSIONS = {"accessionNumber": ["0001424929-26-000061", "0001839849-26-000002"], "filingDate": ["2026-10-16", "2026-05-12"],
               "reportDate": ["2026-10-15", "2026-05-08"], "acceptanceDateTime": ["2026-10-17T00:06:27.000Z", "2026-05-13T00:05:20.000Z"],
               "form": ["8-K", "4"], "items": ["2.02,5.02,9.01", ""],
               "primaryDocument": ["foxf-20261015.htm", "xslF345X06/wk-form4_1778616317.xml"], "primaryDocDescription": ["8-K", "FORM 4"]}

FTS = {"hits": {"total": {"value": 1}, "hits": [{"_id": "0001424929-26-000061:exhibit991pressreleasedate.htm", "_source": {
    "ciks": ["0001424929"], "period_ending": "2026-10-15", "display_names": ["FOX FACTORY HOLDING CORP  (FOXF)  (CIK 0001424929)"],
    "root_forms": ["8-K"], "file_date": "2026-10-16", "form": "8-K", "adsh": "0001424929-26-000061", "file_type": "EX-99.1"}}]}}

FORM4 = """<?xml version="1.0"?>
<ownershipDocument>
    <documentType>4</documentType>
    <issuer><issuerCik>0001045810</issuerCik><issuerTradingSymbol>NVDA</issuerTradingSymbol></issuer>
    <reportingOwner>
        <reportingOwnerId><rptOwnerCik>0001197649</rptOwnerCik><rptOwnerName>HUANG JEN HSUN</rptOwnerName></reportingOwnerId>
        <reportingOwnerRelationship><isDirector>1</isDirector><isOfficer>1</isOfficer><officerTitle>President and CEO</officerTitle></reportingOwnerRelationship>
    </reportingOwner>
    <aff10b5One>0</aff10b5One>
    <nonDerivativeTable>
        <nonDerivativeTransaction>
            <securityTitle><value>Common Stock</value></securityTitle>
            <transactionDate><value>2025-08-29</value></transactionDate>
            <transactionCoding><transactionFormType>4</transactionFormType><transactionCode>S</transactionCode><footnoteId id="F1"/></transactionCoding>
            <transactionAmounts>
                <transactionShares><value>32488</value></transactionShares>
                <transactionPricePerShare><value>173.8729</value><footnoteId id="F2"/></transactionPricePerShare>
                <transactionAcquiredDisposedCode><value>D</value></transactionAcquiredDisposedCode>
            </transactionAmounts>
            <postTransactionAmounts><sharesOwnedFollowingTransaction><value>72815878</value></sharesOwnedFollowingTransaction></postTransactionAmounts>
            <ownershipNature><directOrIndirectOwnership><value>D</value></directOrIndirectOwnership></ownershipNature>
        </nonDerivativeTransaction>
        <nonDerivativeTransaction>
            <securityTitle><value>Common Stock</value></securityTitle>
            <transactionDate><value>2025-08-29</value></transactionDate>
            <transactionCoding><transactionCode>G</transactionCode></transactionCoding>
            <transactionAmounts>
                <transactionShares><value>1000</value></transactionShares>
                <transactionPricePerShare><value>0</value></transactionPricePerShare>
                <transactionAcquiredDisposedCode><value>D</value></transactionAcquiredDisposedCode>
            </transactionAmounts>
            <postTransactionAmounts><sharesOwnedFollowingTransaction><value>72814878</value></sharesOwnedFollowingTransaction></postTransactionAmounts>
            <ownershipNature><directOrIndirectOwnership><value>I</value></directOrIndirectOwnership></ownershipNature>
        </nonDerivativeTransaction>
    </nonDerivativeTable>
    <footnotes>
        <footnote id="F1">The reported transaction was effected pursuant to a Rule 10b5-1 trading plan adopted by the Reporting Person on March 20, 2025.</footnote>
        <footnote id="F2">Weighted average price; prices ranged from $173.32 to $174.31.</footnote>
    </footnotes>
</ownershipDocument>"""

EXHIBIT = """<DOCUMENT>
<TYPE>EX-99.1
<SEQUENCE>3
<FILENAME>exhibit991.htm
<TEXT>
<html><head><title>Document</title><style>p{color:red}</style></head><body>
<div><font>Exhibit&#160;99.1</font></div><div><br></div>
<p>Third quarter results were below the Company&#8217;s   expectations,
primarily due to lower sales &amp; margin.</p>
<table><tr><td>Net sales</td><td>$1.0</td></tr></table>
</body></html>
</TEXT>
</DOCUMENT>"""


class Parsers(unittest.TestCase):
    def test_index(self):
        ix = edgar.parse_index(INDEX)
        self.assertEqual(ix["accepted"], "2026-10-16 16:06:27")
        self.assertEqual(ix["filing_date"], "2026-10-16")
        self.assertEqual(ix["period"], "2026-10-15")
        self.assertEqual(len(ix["items_text"]), 3)
        self.assertEqual(ix["items_text"][1], "Item 5.02: Departure of Directors & Officers")

    def test_index_without_items(self):
        ix = edgar.parse_index('<div class="infoHead">Accepted</div>\n<div class="info">2026-08-06 17:51:15</div>')
        self.assertEqual((ix["accepted"], ix["period"], ix["items_text"]), ("2026-08-06 17:51:15", None, []))

    def test_session(self):
        self.assertEqual(edgar.session("2026-10-16 16:06:27"), ("2026-10-16T16:06:27-04:00", True, False))
        self.assertEqual(edgar.session("2026-02-26 08:20:06"), ("2026-02-26T08:20:06-05:00", False, True))
        self.assertEqual(edgar.session("2026-03-27 09:30:00"), ("2026-03-27T09:30:00-04:00", False, False))
        self.assertEqual(edgar.session("2026-03-27 15:59:59")[1:], (False, False))
        self.assertEqual(edgar.session("2026-03-27 16:00:00")[1:], (True, False))

    def test_submissions(self):
        rows = edgar.parse_submissions(SUBMISSIONS)
        self.assertEqual(rows[0]["accession"], "0001424929-26-000061")
        self.assertEqual(rows[0]["items"], "2.02,5.02,9.01")
        self.assertEqual(rows[1]["form"], "4")
        self.assertEqual(rows[1]["doc"], "xslF345X06/wk-form4_1778616317.xml")

    def test_find_cik(self):
        t = {"0": {"cik_str": 1424929, "ticker": "FOXF", "title": "Fox Factory"}, "1": {"cik_str": 1067983, "ticker": "BRK-B", "title": "Berkshire"}}
        self.assertEqual(edgar.find_cik(t, "foxf"), 1424929)
        self.assertEqual(edgar.find_cik(t, "BRK.B"), 1067983)
        self.assertIsNone(edgar.find_cik(t, "ZZZZ"))

    def test_fts(self):
        (h,) = edgar.parse_fts(FTS)
        self.assertEqual((h["form"], h["filed"], h["accession"], h["file"], h["file_type"]),
                         ("8-K", "2026-10-16", "0001424929-26-000061", "exhibit991pressreleasedate.htm", "EX-99.1"))
        self.assertEqual(h["url"], "https://www.sec.gov/Archives/edgar/data/1424929/000142492926000061/exhibit991pressreleasedate.htm")

    def test_form4(self):
        sale, gift = edgar.parse_form4(FORM4)
        self.assertEqual((sale["owner"], sale["role"]), ("HUANG JEN HSUN", "Director, President and CEO"))
        self.assertEqual((sale["date"], sale["code"], sale["shares"], sale["price"], sale["owned_after"], sale["direct"]),
                         ("2025-08-29", "S", "32488", "173.8729", "72815878", "D"))
        self.assertTrue(sale["plan_10b5_1"])
        self.assertEqual(sale["plan_adopted"], "March 20, 2025")
        self.assertEqual((gift["code"], gift["plan_10b5_1"], gift["plan_adopted"], gift["direct"]), ("G", False, None, "I"))

    def test_form4_checkbox_and_remarks(self):
        x = FORM4.replace("<aff10b5One>0</aff10b5One>", "<aff10b5One>1</aff10b5One>")
        self.assertTrue(edgar.parse_form4(x)[1]["plan_10b5_1"])
        x = FORM4.replace("pursuant to a Rule 10b5-1 trading plan adopted by the Reporting Person on March 20, 2025", "x") \
                 .replace("</footnotes>", "</footnotes><remarks>Sales under a 10b5-1 plan entered into on 11/15/2024.</remarks>")
        self.assertEqual(edgar.parse_form4(x)[0]["plan_adopted"], "11/15/2024")

    def test_plan_date_variants(self):
        self.assertEqual(edgar.plan_date("Shares sold under a Rule 10b5-1 plan adopted on Dec. 5, 2024 and amended later."), "Dec. 5, 2024")
        self.assertEqual(edgar.plan_date("Made pursuant to a 10b5-1 plan established 2025-01-02."), "2025-01-02")
        self.assertIsNone(edgar.plan_date("Made pursuant to a Rule 10b5-1 trading plan."))

    def test_html_to_text(self):
        t = edgar.html_to_text(EXHIBIT)
        self.assertTrue(t.startswith("Exhibit 99.1"))
        self.assertNotIn("<", t)
        self.assertNotIn("color:red", t)
        self.assertIn("Third quarter results were below the Company’s expectations,\nprimarily due to lower sales & margin.", t)
        self.assertIn("Net sales $1.0", t)
        self.assertNotIn("\n\n\n", t)

    def test_plain_text_passthrough(self):
        self.assertEqual(edgar.html_to_text("plain filing text\n\nsecond para"), "plain filing text\n\nsecond para")


if __name__ == "__main__":
    unittest.main()
