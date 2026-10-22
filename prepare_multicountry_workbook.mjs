#!/usr/bin/env node
/**
 * Build SurveyData_MultiCountry.xlsx from ISSP 2024 Digital Societies Release 2.0.0.
 *
 * See SurveyData_MultiCountry_Builder_README.md for prerequisites, configuration,
 * invocation examples, output safety, and validation details.
 *
 * Requires Python 3 with pandas. All source codes are preserved; no weights are
 * applied. The script refuses to overwrite an existing output workbook.
 */
import fs from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { FileBlob, SpreadsheetFile, Workbook } = require("@oai/artifact-tool");

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const EXPECTED_NS = {
  Germany: 1399,
  Austria: 1546,
  Switzerland: 3028,
  USA: 1590,
  Australia: 1015,
  Canada: 1342,
};
const COUNTRIES = [
  { name: "Germany", code: 276, group: "German prompt" },
  { name: "Austria", code: 40, group: "German prompt" },
  { name: "Switzerland", code: 756, group: "German prompt" },
  { name: "USA", code: 840, group: "English prompt" },
  { name: "Australia", code: 36, group: "English prompt" },
  { name: "Canada", code: 124, group: "English prompt" },
];
const ITEMS = [
  { id: "Q1", variable: "v1", sheet: "Q1 Internet Use", label: "Internet use frequency", substantive: [1, 2, 3, 4, 5, 6, 7] },
  { id: "Q10d", variable: "v26", sheet: "Q10d Software Skills", label: "Ability to learn new software/apps", substantive: [1, 2, 3, 4, 5] },
  { id: "Q17a", variable: "v42", sheet: "Q17a Tech Easier", label: "Technology makes life easier", substantive: [1, 2, 3, 4, 5] },
  { id: "Q20", variable: "v47", sheet: "Q20 Political News", label: "Most important source of political news", substantive: [1, 2, 3, 4, 5, 6] },
  { id: "Q23a", variable: "v54", sheet: "Q23a Petition", label: "Signed a petition in the last 12 months", substantive: [1, 2, 3, 4] },
  { id: "Q28a", variable: "v64", sheet: "Q28a Surveillance", label: "Government right to use video surveillance in public areas", substantive: [1, 2, 3, 4] },
  { id: "Q34", variable: "v72", sheet: "Q34 Digital Benefits", label: "Who benefits more from digital technology", substantive: [1, 2, 3, 4] },
  { id: "Q36a", variable: "v74", sheet: "Q36a Medical Robot", label: "Comfort with robot performing a medical operation", substantive: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] },
];
const expectedTables = [];

const CROSSWALK = {
  Q1: {
    DE: ["F1", "p. 4", "Wie oft, wenn überhaupt, haben Sie normalerweise in den letzten 12 Monaten das Internet – beruflich oder privat – auf einem beliebigen Gerät genutzt?", "German form has seven frequency choices; no explicit can’t-choose response on this item."],
    AT: ["Q1", "p. 2", "Wie oft, wenn überhaupt, haben Sie in den letzten 12 Monaten normalerweise das Internet für Ihre Arbeit oder für private Zwecke genutzt?", "German form; seven frequency choices; no substantive scale difference found."],
    CH: ["N1", "p. 4", "Wie oft haben Sie in den letzten 12 Monaten auf irgendeinem Gerät das Internet zu beruflichen oder privaten Zwecken genutzt?", "Swiss instrument contains German, French, and Italian versions; full sample is multilingual."],
    AU: ["A1", "p. 3", "During the last 12 months, how often, if at all, did you typically use the Internet on any device whether for work or personal use?", "“Never” routes to non-use questions; codes 1–6 continue to the user path."],
    US: ["INTRNETUSE", "p. 2", "During the last 12 months, how often, if at all, did you typically use the Internet on any device whether for work or personal use?", "US form additionally offers Don't know, refusal, and NA responses; harmonized DTA labels differ."],
    CA: ["Group A Q6", "p. 10", "During the last 12 months, how often, if at all, did you typically use the Internet on any device whether for work or personal use?", "Group A form: never goes to Q7; -9 continues to Q11; form prints -4 for filtered cases."],
  },
  Q10d: {
    DE: ["F10 row d", "p. 7", "Lernen, wie man eine neue Software oder App benutzt", "Internet-user skills battery. Germany has 67 Q1=7 cases but only 56 v26=-4; 11 have substantive answers."],
    AT: ["Q10 row d", "p. 8", "Lernen, wie man neue Software oder Apps benutzt", "Internet-user battery; paper route explicitly includes Q1=1–6 or missing (-9)."],
    CH: ["N10d", "p. 8", "Neue Software oder Apps zu nutzen", "Internet-user battery. The Swiss questionnaire prints -1 ‘Kann ich nicht sagen’; pooled DTA harmonizes this as -8 ‘Can't choose’."],
    AU: ["A10 row d", "p. 5", "Learning how to use new software or apps", "Skills battery follows the internet-use branch; preserve screen-missing records separately."],
    US: ["INTAPPS", "p. 8", "Learning how to use new software or apps?", "Internet-skills question in a separate user/non-user flow."],
    CA: ["Group A Q15 row d", "p. 14", "Learning how to use new software or apps", "Q6 codes 1–6 or -9 proceed to the skills battery; Q6=7 follows Q7."],
  },
  Q17a: {
    DE: ["F17 row a", "p. 9", "Technologien machen unser Leben einfacher.", "German form uses plural “Technologien”; five agree/disagree positions."],
    AT: ["Q17 row a", "p. 13", "Technologien machen unser Leben leichter.", "German translation; five agree/disagree positions."],
    CH: ["N17a", "p. 12", "Technologie macht unser Leben einfacher.", "The Swiss questionnaire prints -1 ‘Kann ich nicht sagen’; pooled DTA harmonizes this as -8. Full sample includes German-, French-, and Italian-interview cases."],
    AU: ["A17", "p. 7", "Technology makes our lives easier.", "Five-point agree/disagree scale; all respondents."],
    US: ["TECHESY", "p. 13", "Technology makes our lives easier.", "Five-point agree/disagree scale; all respondents."],
    CA: ["Group A Q22a", "p. 17", "Technology makes our lives easier.", "Group A; five-point agree/disagree scale."],
  },
  Q20: {
    DE: ["F20", "p. 10", "Woher beziehen Sie überwiegend Nachrichten zu politischen Themen? Bitte wählen Sie die wichtigste Quelle aus.", "Six categories; German social-media, TV, and website examples are country-specific."],
    AT: ["Q20", "p. 14", "Aus welcher Nachrichtenquelle beziehen Sie die meisten politischen Informationen? Bitte wählen Sie die wichtigste Quelle aus.", "Six categories; Austrian German wording and media examples."],
    CH: ["N20", "p. 13", "Wo informieren Sie sich hauptsächlich über das politische Geschehen? Bitte wählen Sie die für Sie wichtigste Informationsquelle.", "Six categories; Swiss platform examples differ. Questionnaire -1 ‘Kann ich nicht sagen’ is harmonized to DTA -8."],
    AU: ["A20", "p. 8", "Where do you get most of your news about political matters? Please select the most important source.", "Six categories; social-media platform examples differ by country."],
    US: ["POLNEWSFROM", "p. 15", "Where do you get most of your news about political matters? Please select the most important source.", "Six categories; US platform examples differ from other forms."],
    CA: ["Group A Q25", "p. 19", "Where do you get most of your news about political matters? Please select the most important source.", "Six categories; Canadian platform examples differ; Group A."],
  },
  Q23a: {
    DE: ["F23 row a", "p. 11", "Unterschriftensammlung/Petition unterschrieben", "Participation in the last 12 months; offline/online/both/neither."],
    AT: ["Q23 row a", "p. 16", "An einer Unterschriftenaktion teilgenommen", "Participation in the last 12 months; offline/online/both/neither."],
    CH: ["N23a", "p. 14", "Eine Petition unterzeichnet", "Same 12-month action and four substantive categories. Questionnaire -1 ‘Kann ich nicht sagen’ is harmonized to DTA -8."],
    AU: ["A23", "p. 9", "Signed a petition.", "Same 12-month action and four substantive categories."],
    US: ["MODEPET", "p. 17", "Signed a petition.", "Same 12-month action and four substantive categories."],
    CA: ["Group A Q28a", "p. 20", "Signed a petition", "Same 12-month action and four substantive categories; Group A."],
  },
  Q28a: {
    DE: ["F28 row a", "p. 12", "Sollte der deutsche Staat Ihrer Meinung nach das Recht zu Folgendem haben oder nicht? Videoüberwachung von Menschen im öffentlichen Raum.", "Actor is the German state; four-point right/no-right scale."],
    AT: ["Q28 row a", "p. 19", "Sollte der österreichische Staat Ihrer Meinung nach das Recht zu Folgendem haben oder nicht haben? Menschen im öffentlichen Bereich mit Videokameras zu überwachen.", "Actor is the Austrian state; four-point scale."],
    CH: ["N28a", "p. 17", "Finden Sie, dass die Behörden in der Schweiz das Recht haben sollten oder nicht, Folgendes zu tun? Menschen in der Öffentlichkeit per Video zu überwachen.", "Swiss form says “authorities in Switzerland,” not exactly “government.” Questionnaire -1 ‘Kann ich nicht sagen’ is harmonized to DTA -8."],
    AU: ["A28 row a", "p. 10", "Do you think that the Australian government should or should not have the right to do the following? Keep people under video surveillance in public areas?", "Actor is the Australian government."],
    US: ["CCTV", "p. 20", "Do you think that the American government should or should not have the right to do the following? Keep people under video surveillance in public areas?", "Actor is the American government."],
    CA: ["Group A Q33a", "p. 22", "Do you think that Canada’s government should or should not have the right to do the following?", "Actor is Canada’s government; Group A."],
  },
  Q34: {
    DE: ["F34", "p. 13", "Wer hat Ihrer Meinung nach in Deutschland mehr Vorteile durch die Nutzung des Internets und digitaler Technologien – Reiche oder Arme? Oder beide gleichermaßen? Oder keine der beiden Gruppen?", "Four categories rich/equal/poor/neither; explicitly names Germany."],
    AT: ["Q34", "p. 23", "Glauben Sie, dass in Österreich Reiche oder Arme mehr, beide gleichermaßen, oder keiner von beiden von der Nutzung des Internets und digitaler Technologien profitieren?", "Four categories; explicitly names Austria."],
    CH: ["N34", "p. 19", "Denken Sie, dass in der Schweiz reiche oder arme Menschen mehr von der Nutzung des Internets und der digitalen Technologien profitieren, dass sie beide gleich viel davon profitieren oder dass weder reiche noch arme Menschen davon profitieren?", "Four categories; explicitly names Switzerland. Questionnaire -1 ‘Kann ich nicht sagen’ is harmonized to DTA -8."],
    AU: ["A34", "p. 11", "Do you think that in Australia rich people or poor people are benefitting more, or both equally, or neither, from the use of the Internet and digital technology?", "Four categories; explicitly names Australia."],
    US: ["CLASSTECH", "p. 23", "Do you think that in America, rich people or poor people are benefitting more, or both equally, or neither, from the use of the Internet and digital technology?", "Four categories; explicitly names America."],
    CA: ["Group A Q39", "p. 25", "Do you think that in Canada rich people or poor people are benefitting more, or both equally, or neither, from the use of the Internet and digital technology?", "Four categories; explicitly names Canada; Group A."],
  },
  Q36a: {
    DE: ["F36 row a", "p. 14", "Wenn ein Roboter Sie operiert", "0–10 comfort scale; German endpoints vollkommen unwohl / vollkommen wohl."],
    AT: ["Q36 row a", "p. 24", "Eine medizinische Operation von einem Roboter durchführen zu lassen", "0–10 comfort scale; Austrian German endpoints völlig unwohl / völlig wohl."],
    CH: ["N36a", "p. 19", "Sich von einem Roboter operieren lassen.", "0–10 scale; questionnaire -1 ‘Kann ich nicht sagen’ is harmonized to DTA -8. Harmonized data store 0–10 values."],
    AU: ["A36 row a", "p. 12", "Having a medical operation performed on you by a robot", "0–10 comfort scale; 0 totally uncomfortable, 10 totally comfortable."],
    US: ["AIMED", "pp. 23–24", "Having a medical operation performed on you by a robot.", "0–10 comfort scale; 0 totally uncomfortable, 10 totally comfortable."],
    CA: ["Group A Q41a", "p. 26", "Having a medical operation performed on you by a robot", "0–10 comfort scale; Group A."],
  },
};

const ITEM_PAGES = {
  Q1: { DE: "p. 4", US: "p. 2", AT: "p. 2", CH: "p. 4", AU: "p. 3", CA: "p. 10" },
  Q10d: { DE: "p. 7", US: "p. 8", AT: "p. 8", CH: "p. 8", AU: "p. 5", CA: "p. 14" },
  Q17a: { DE: "p. 9", US: "p. 13", AT: "p. 13", CH: "p. 12", AU: "p. 7", CA: "p. 17" },
  Q20: { DE: "p. 10", US: "p. 15", AT: "p. 14", CH: "p. 13", AU: "p. 8", CA: "p. 19" },
  Q23a: { DE: "p. 11", US: "p. 17", AT: "p. 16", CH: "p. 14", AU: "p. 9", CA: "p. 20" },
  Q28a: { DE: "p. 12", US: "p. 20", AT: "p. 19", CH: "p. 17", AU: "p. 10", CA: "p. 22" },
  Q34: { DE: "p. 13", US: "p. 23", AT: "p. 23", CH: "p. 19", AU: "p. 11", CA: "p. 25" },
  Q36a: { DE: "p. 14", US: "pp. 23–24", AT: "p. 24–25", CH: "p. 19", AU: "p. 12", CA: "p. 26" },
};
const COUNTRY_DOCS = {
  Germany: { code: "DE", questionnaire: "ZA10020_q_de.pdf", background: "ZA10020_backgroundvar_de.pdf", questionPath: "Documents/LLMs_for_real_world_opinion/documentation/ZA10020_q_de.pdf", backgroundPath: "Documents/LLMs_for_real_world_opinion/documentation/ZA10020_backgroundvar_de.pdf", tech: "Downloads/ZA10020_TechnicalReport_all/ZA10020_TechnicalReport_de.pdf", chars: "Downloads/ZA10020_characteristics_all/ZA10020_characteristics_de.pdf", weight: "Background-variable p. 62: construction/weight statements conflict; no weight selected." },
  Austria: { code: "AT", questionnaire: "ZA10020_q_at.pdf", background: "ZA10020_backgroundvar_at.pdf", questionPath: "Downloads/ZA10020_q_at.pdf", backgroundPath: "Downloads/ZA10020_backgroundvar_at.pdf", tech: "Downloads/ZA10020_TechnicalReport_at.pdf", chars: "Downloads/ZA10020_characteristics_at.pdf", weight: "Background-variable p. 51 lists PSWEIGHT but construction text says no weighting; unresolved." },
  Switzerland: { code: "CH", questionnaire: "ZA10020_q_ch.pdf", background: "ZA10020_backgroundvar_ch.pdf", questionPath: "Downloads/ZA10020_q_ch.pdf", backgroundPath: "Downloads/ZA10020_backgroundvar_ch.pdf", tech: "Downloads/ZA10020_TechnicalReport_ch.pdf", chars: "Downloads/ZA10020_characteristics_ch.pdf", weight: "Background-variable pp. 87–88: equal selection probability and weights 1; matches observed constant-one fields." },
  USA: { code: "US", questionnaire: "ZA10020_q_us-en.pdf", background: "ZA10020_backgroundvar_us.pdf", questionPath: "Documents/LLMs_for_real_world_opinion/documentation/ZA10020_q_us-en.pdf", backgroundPath: "Documents/LLMs_for_real_world_opinion/documentation/ZA10020_backgroundvar_us.pdf", tech: "Downloads/ZA10020_TechnicalReport_all/ZA10020_TechnicalReport_us.pdf", chars: "Downloads/ZA10020_characteristics_all/ZA10020_characteristics_us.pdf", weight: "Background-variable pp. 63–64: weight fields and construction statements conflict; no weight selected." },
  Australia: { code: "AU", questionnaire: "ZA10020_q_au.pdf", background: "ZA10020_backgroundvar_au.pdf", questionPath: "Downloads/ZA10020_q_au.pdf", backgroundPath: "Downloads/ZA10020_backgroundvar_au.pdf", tech: "Downloads/ZA10020_TechnicalReport_au.pdf", chars: "Downloads/ZA10020_characteristics_au.pdf", weight: "Background-variable pp. 60–61 lists PSWEIGHT but construction text says no weighting; unresolved." },
  Canada: { code: "CA", questionnaire: "ZA10020_q_ca-en.pdf", background: "ZA10020_backgroundvar_ca.pdf", questionPath: "Downloads/ZA10020_q_ca-en.pdf", backgroundPath: "Downloads/ZA10020_backgroundvar_ca.pdf", tech: "Downloads/ZA10020_TechnicalReport_ca.pdf", chars: "Downloads/ZA10020_characteristics_ca.pdf", weight: "Background-variable pp. 61–62 recommends PSWEIGHT for the overall ten-province adult population; suitability for English interviews unresolved." },
};

const PY_EXTRACT = String.raw`
import json, sys
import pandas as pd
src = sys.argv[1]
def q10d_cross_counts(screen, response, screen_labels, response_labels):
    screen_codes = sorted(set(screen_labels) | {int(x) for x in screen.dropna().unique()})
    response_codes = sorted(set(response_labels) | {int(x) for x in response.dropna().unique()})
    if screen.isna().any(): screen_codes.append("SYSMIS")
    if response.isna().any(): response_codes.append("SYSMIS")
    screen_map = {str(x):screen_labels.get(x,"System missing" if x == "SYSMIS" else "Observed, unlabeled code") for x in screen_codes}
    response_map = {str(x):response_labels.get(x,"System missing" if x == "SYSMIS" else "Observed, unlabeled code") for x in response_codes}
    joint = []
    for screen_code in screen_codes:
        for response_code in response_codes:
            screen_match = screen.isna() if screen_code == "SYSMIS" else screen == screen_code
            response_match = response.isna() if response_code == "SYSMIS" else response == response_code
            joint.append({"screen_code":str(screen_code),"response_code":str(response_code),"count":int((screen_match & response_match).sum())})
    return screen_map, response_map, joint

# Exercise the joint-missing cell so a respondent missing both variables is counted once.
_test_screen = pd.Series([7,float("nan"),float("nan"),1])
_test_response = pd.Series([-4,1,float("nan"),float("nan")])
_, _, _test_joint = q10d_cross_counts(_test_screen,_test_response,{1:"Use",7:"Never"},{-4:"NAP",1:"Answer"})
if sum(x["count"] for x in _test_joint) != 4 or next(x["count"] for x in _test_joint if x["screen_code"] == "SYSMIS" and x["response_code"] == "SYSMIS") != 1:
    raise AssertionError("Q10d system-missing joint-count self-check failed")

countries = [
    {"name":"Germany","code":276,"group":"German prompt","expected":1399},
    {"name":"Austria","code":40,"group":"German prompt","expected":1546},
    {"name":"Switzerland","code":756,"group":"German prompt","expected":3028},
    {"name":"USA","code":840,"group":"English prompt","expected":1590},
    {"name":"Australia","code":36,"group":"English prompt","expected":1015},
    {"name":"Canada","code":124,"group":"English prompt","expected":1342},
]
items = [
    {"id":"Q1","variable":"v1","substantive":[1,2,3,4,5,6,7]},
    {"id":"Q10d","variable":"v26","substantive":[1,2,3,4,5]},
    {"id":"Q17a","variable":"v42","substantive":[1,2,3,4,5]},
    {"id":"Q20","variable":"v47","substantive":[1,2,3,4,5,6]},
    {"id":"Q23a","variable":"v54","substantive":[1,2,3,4]},
    {"id":"Q28a","variable":"v64","substantive":[1,2,3,4]},
    {"id":"Q34","variable":"v72","substantive":[1,2,3,4]},
    {"id":"Q36a","variable":"v74","substantive":list(range(0,11))},
]
weights = ["DWEIGHT_HH","DWEIGHT_TS","DWEIGHT_COM","PSWEIGHT","WEIGHT_COM"]
r = pd.io.stata.StataReader(src, convert_categoricals=False)
d = r.read()
varlabels = r.variable_labels()
alllabels = r.value_labels()
version_values = d["version"].dropna().astype(str).unique().tolist()
if len(version_values) != 1 or not version_values[0].startswith("2.0.0"):
    raise ValueError("Unexpected dataset release metadata: " + repr(version_values))
required = {"country","INTLANG","version",*weights,*[i["variable"] for i in items]}
missing = sorted(required - set(d.columns))
if missing:
    raise ValueError("Missing required DTA fields: " + repr(missing))
out = {"version":version_values[0],"rows":int(len(d)),"variables":int(len(d.columns)),"items":{},"countries":[]}
for item in items:
    var = item["variable"]
    labelset = alllabels.get(var.upper(), {})
    item["variable_label"] = varlabels.get(var, "")
    item["labels"] = {str(int(k)):str(v) for k,v in labelset.items()}
    if not item["variable_label"] or not item["labels"]:
        raise ValueError("Missing variable/value labels for " + var)
    out["items"][item["id"]] = item
for c in countries:
    full = d.loc[d["country"] == c["code"]].copy()
    c["full_n"] = int(len(full))
    c["language_counts"] = {str(k):int(v) for k,v in full["INTLANG"].value_counts(dropna=False).items()}
    if c["name"] == "Canada":
        selected = full.loc[full["INTLANG"] == "eng (English)"].copy()
        c["language_filter"] = 'INTLANG == "eng (English)"'
        c["literal_eng_n"] = int((full["INTLANG"] == "eng").sum())
    else:
        selected = full
        c["language_filter"] = "Full country sample"
        c["literal_eng_n"] = None
    c["n"] = int(len(selected))
    if c["n"] != c["expected"]:
        raise ValueError("N mismatch for " + c["name"] + ": expected " + str(c["expected"]) + ", found " + str(c["n"]))
    c["items"] = {}
    c["weights"] = {}
    for item in items:
        var = item["variable"]
        labels = {int(k):v for k,v in out["items"][item["id"]]["labels"].items()}
        observed = selected[var]
        counts = {}
        for raw, n in observed.value_counts(dropna=False).items():
            key = "SYSMIS" if pd.isna(raw) else str(int(raw))
            counts[key] = int(n)
        for code in labels:
            counts.setdefault(str(code), 0)
        if sum(counts.values()) != len(selected):
            raise AssertionError("Count reconciliation failed: " + c["name"] + "/" + var)
        extra = set(counts) - {str(x) for x in labels} - {"SYSMIS"}
        if extra:
            raise AssertionError("Unexpected code(s): " + repr((c["name"],var,extra)))
        c["items"][item["id"]] = {"counts":counts,"item_base_n":int(observed.notna().sum()),"system_missing_n":int(observed.isna().sum())}
    v1 = selected["v1"]
    v26 = selected["v26"]
    c["q10d"] = {
        "eligible_n":int(v1.isin([1,2,3,4,5,6]).sum()),
        "screen_never_n":int((v1 == 7).sum()),
        "screen_no_answer_n":int((v1 == -9).sum()),
        "screen_system_missing_n":int(v1.isna().sum()),
        "substantive_n":int(v26.isin([1,2,3,4,5]).sum()),
        "response_system_missing_n":int(v26.isna().sum()),
        "cant_choose_n":int((v26 == -8).sum()),
        "no_answer_n":int((v26 == -9).sum()),
        "nap_n":int((v26 == -4).sum()),
        "other_n":int((~v26.isin([-9,-8,-4,1,2,3,4,5]) & v26.notna()).sum()),
        "screen_codes":{},"q10_codes":{},"cross_counts":[]
    }
    q1labels = {int(k):v for k,v in out["items"]["Q1"]["labels"].items()}
    q10labels = {int(k):v for k,v in out["items"]["Q10d"]["labels"].items()}
    screen_codes, response_codes, joint_counts = q10d_cross_counts(v1,v26,q1labels,q10labels)
    c["q10d"]["screen_codes"] = screen_codes
    c["q10d"]["q10_codes"] = response_codes
    c["q10d"]["cross_counts"] = joint_counts
    for w in weights:
        s=selected[w]
        c["weights"][w]={"missing_n":int(s.isna().sum()),"distinct_n":int(s.nunique(dropna=True)),"min":None if s.dropna().empty else float(s.min()),"max":None if s.dropna().empty else float(s.max())}
    out["countries"].append(c)
print(json.dumps(out,ensure_ascii=False,allow_nan=False))
`;

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === "--data") args.data = argv[++i];
    else if (argv[i] === "--output") args.output = argv[++i];
    else if (argv[i] === "--python") args.python = argv[++i];
    else throw new Error(`Unknown argument: ${argv[i]}`);
  }
  if (!args.data) throw new Error("Provide the pooled Stata file with --data /path/to/ZA10020_v2-0-0.dta");
  args.data = path.resolve(args.data);
  args.output = path.resolve(args.output || path.join(ROOT, "SurveyData_MultiCountry.xlsx"));
  args.python = args.python || process.env.PYTHON || "python3";
  return args;
}

function hashBytes(buf) { return crypto.createHash("sha256").update(buf).digest("hex"); }
function columnName(n) {
  let s = "";
  while (n > 0) { const r = (n - 1) % 26; s = String.fromCharCode(65 + r) + s; n = Math.floor((n - 1) / 26); }
  return s;
}
function codeLabel(item, code) {
  if (code === "SYSMIS") return "System-missing value";
  return item.labels[String(code)] || "Declared/observed code without a value label";
}
function specialStatus(item, code) {
  if (code === "SYSMIS") return "System missing";
  const n = Number(code);
  if (n === -4) return "Not applicable / filtered (NAP)";
  if (n === -8) return "Can't choose";
  if (n === -9) return "No answer";
  if (n === -6 && item.variable === "v47") return "Poland-specific NAP; not expected in selected countries";
  if (item.substantive.includes(n)) return "Substantive response";
  return "Other special or non-substantive code";
}
function codeOrder(a,b) {
  if (a === "SYSMIS") return 1;
  if (b === "SYSMIS") return -1;
  return Number(a)-Number(b);
}
function summarize(values) { return values.map(([k,v])=>`${k}: ${v}`).join("; "); }

function mappingNote(countryName, itemId) {
  const d = COUNTRY_DOCS[countryName];
  const c = CROSSWALK[itemId][d.code];
  return c;
}
function sourceRef(countryName, itemId) {
  const d = COUNTRY_DOCS[countryName];
  return `${d.questionnaire}, ${ITEM_PAGES[itemId][d.code]}`;
}

function buildCrosswalk(data) {
  const rows = [];
  for (const item of ITEMS) {
    const meta = data.items[item.id];
    const categories = Object.entries(meta.labels).map(([k,v])=>`${k}=${v}`).join(" | ");
    for (const c of COUNTRIES) {
      const doc = COUNTRY_DOCS[c.name];
      const [officialId, pages, wording, caveat] = mappingNote(c.name, item.id);
      const notes = item.id === "Q10d"
        ? "DTA special values: -4 NAP, -8 can't choose, -9 no answer. Do not resolve denominator here."
        : item.variable === "v47"
          ? "DTA -6 label is Poland-specific; no -6 observed in the six selected country samples."
          : "Retain DTA special codes separately: -8 can't choose; -9 no answer where declared/observed.";
      const assessment = item.id === "Q10d" || item.id === "Q20" || item.id === "Q28a" || item.id === "Q34"
        ? "Comparable with caveat"
        : "Comparable; translation/form notes retained";
      rows.push([
        item.id, c.name, c.group, item.variable, meta.variable_label, item.label,
        officialId, wording, categories, notes, caveat,
        item.id === "Q10d" ? "Internet-user skills battery; local routing is listed in the country-specific note. Full Q1 × v26 table is on Q10d Routing." : "All respondents / no item-specific routing noted in source questionnaire.",
        assessment, `${doc.questionnaire}, ${pages}`, doc.background,
      ]);
    }
  }
  return rows;
}

function buildLong(data) {
  const rows = [];
  for (let ix=0; ix<COUNTRIES.length; ix++) {
    const country = COUNTRIES[ix];
    const c = data.countries[ix];
    for (const item of ITEMS) {
      const meta = data.items[item.id];
      const d = c.items[item.id];
      const counts = d.counts;
      const codeKeys = Object.keys(counts).sort(codeOrder);
      const substantiveN = item.substantive.reduce((sum,code)=>sum+(counts[String(code)]||0),0);
      for (const code of codeKeys) {
        const count = counts[code] || 0;
        const isSub = code !== "SYSMIS" && item.substantive.includes(Number(code));
        let eligibleCount = null, eligiblePct = null, eligibleN = null;
        let substPct = null;
        if (item.id === "Q10d") {
          const q = c.q10d;
          eligibleN = q.eligible_n;
          const rc = Number(code);
          eligibleCount = q.cross_counts.filter(x=>Number(x.screen_code)>=1 && Number(x.screen_code)<=6 && x.response_code===code).reduce((s,x)=>s+x.count,0);
          eligiblePct = eligibleN ? eligibleCount/eligibleN : null;
          substPct = isSub && q.substantive_n ? count/q.substantive_n : null;
        } else {
          eligibleN = c.n;
          eligibleCount = count;
          eligiblePct = c.n ? count/c.n : null;
          substPct = isSub && substantiveN ? count/substantiveN : null;
        }
        rows.push([
          country.name, country.group, c.language_filter, item.id, item.label, item.variable,
          code === "SYSMIS" ? "SYSMIS" : Number(code), codeLabel(meta, code), specialStatus(item, code),
          count, d.item_base_n, c.n, c.n, count/c.n,
          isSub ? substantiveN : null, substPct,
          item.id === "Q10d" ? eligibleN : null,
          item.id === "Q10d" ? eligibleCount : null,
          item.id === "Q10d" ? eligiblePct : null,
          item.id === "Q10d"
            ? (isSub ? "Substantive-only denominator: Q10d codes 1–5; eligible-screen view denominator: Q1 codes 1–6; full code counts remain against the full selected sample." : "Special/system-missing codes are retained in full-sample counts and the eligible-screen counts; excluded from substantive-only denominator.")
            : "Full-sample denominator includes all observed substantive and special codes; substantive-only denominator uses item substantive codes only.",
          sourceRef(country.name, item.id),
        ]);
      }
    }
  }
  return rows;
}

function table(sheet, headers, rows, name, startRow=1) {
  const matrix = [headers, ...rows];
  const endRow = startRow + matrix.length - 1;
  const endCol = headers.length;
  const range = `${columnName(1)}${startRow}:${columnName(endCol)}${endRow}`;
  sheet.getRange(range).values = matrix;
  const t = sheet.tables.add(range, true, name);
  t.style = "TableStyleMedium2";
  t.showFilterButton = true;
  sheet.freezePanes.freezeRows(startRow);
  sheet.showGridLines = false;
  sheet.getRange(range).format.font = { name: "Arial", size: 10, color: "#1F2937" };
  sheet.getRange(`${columnName(1)}${startRow}:${columnName(endCol)}${startRow}`).format = {
    fill: "#244A6B",
    font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
    wrapText: true,
    verticalAlignment: "center",
  };
  sheet.getRange(range).format.verticalAlignment = "center";
  sheet.getRange(range).format.autofitColumns();
  for (let col=1; col<=endCol; col++) {
    const r = sheet.getRange(`${columnName(col)}:${columnName(col)}`);
    const current = r.format.columnWidth;
    if (current > 44) r.format.columnWidth = 44;
    if (current < 12) r.format.columnWidth = 12;
  }
  sheet.getRange(`${columnName(1)}${startRow}:${columnName(endCol)}${startRow}`).format.rowHeight = 34;
  expectedTables.push({sheetName:sheet.name,startRow:startRow-1,startCol:0,matrix,label:name});
  return {range, startRow, endRow, endCol};
}

function notes(sheet, title, lines) {
  sheet.showGridLines = false;
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A1").format = { font: { name: "Arial", size: 15, bold: true, color: "#183B56" }, rowHeight: 26 };
  const rows = lines.map(([label,value])=>[label,value]);
  sheet.getRange(`A3:B${2+rows.length}`).values = rows;
  sheet.getRange(`A3:A${2+rows.length}`).format = { font: { name: "Arial", size: 10, bold: true, color: "#183B56" }, verticalAlignment: "top" };
  sheet.getRange(`B3:B${2+rows.length}`).format = { font: { name: "Arial", size: 10, color: "#1F2937" }, wrapText: true, verticalAlignment: "top" };
  sheet.getRange("A:A").format.columnWidth = 31;
  sheet.getRange("B:B").format.columnWidth = 112;
  sheet.getRange(`A3:B${2+rows.length}`).format.rowHeight = 38;
}

function assertCellEqual(expected, actual, location) {
  if (expected === null || expected === undefined) {
    if (actual === null || actual === undefined || actual === "") return;
    throw new Error(`${location}: expected blank, found ${JSON.stringify(actual)}`);
  }
  if (typeof expected === "number") {
    if (typeof actual !== "number" || Math.abs(actual - expected) > Math.max(1e-12, Math.abs(expected) * 1e-12)) {
      throw new Error(`${location}: expected ${expected}, found ${JSON.stringify(actual)}`);
    }
    return;
  }
  if (actual !== expected) throw new Error(`${location}: expected ${JSON.stringify(expected)}, found ${JSON.stringify(actual)}`);
}

function validateExportedTables(reopen, expectedSheetNames) {
  const count = reopen.worksheets.getSheetCount();
  const actualSheetNames = Array.from({length:count},(_,i)=>reopen.worksheets.getSheetNameByIndex(i));
  if (JSON.stringify(actualSheetNames) !== JSON.stringify(expectedSheetNames)) {
    throw new Error(`Exported workbook sheet list differs: ${JSON.stringify(actualSheetNames)}`);
  }
  for (const expected of expectedTables) {
    const sheet = reopen.worksheets.getItem(expected.sheetName);
    const rowCount = expected.matrix.length;
    const colCount = expected.matrix[0].length;
    const actual = sheet.getRangeByIndexes(expected.startRow,expected.startCol,rowCount,colCount).values;
    if (!Array.isArray(actual) || actual.length !== rowCount) {
      throw new Error(`Exported table ${expected.label} has an unexpected row count.`);
    }
    for (let r=0;r<rowCount;r++) for (let c=0;c<colCount;c++) {
      assertCellEqual(expected.matrix[r][c],actual[r]?.[c],`${expected.sheetName}/${expected.label} R${r+1}C${c+1}`);
    }
  }
}

async function main() {
  const args = parseArgs(process.argv);
  try { await fs.access(args.data); } catch { throw new Error(`Data file not accessible: ${args.data}`); }
  try { await fs.access(args.output); throw new Error(`Refusing to overwrite existing workbook: ${args.output}`); } catch (e) { if (e.code !== "ENOENT") throw e; }
  const py = spawnSync(args.python, ["-c", PY_EXTRACT, args.data], { encoding: "utf8", maxBuffer: 80*1024*1024 });
  if (py.error) throw py.error;
  if (py.status !== 0) throw new Error(`DTA extraction failed (Python exit ${py.status}):\n${py.stderr}`);
  const data = JSON.parse(py.stdout);
  if (data.rows !== 47635 || data.variables !== 365) throw new Error(`Unexpected pooled file shape: ${data.rows}x${data.variables}`);
  const countriesByName = Object.fromEntries(data.countries.map(c=>[c.name,c]));
  const de = countriesByName.Germany;
  const germanyNeverResponses = Object.fromEntries(
    de.q10d.cross_counts
      .filter(x => Number(x.screen_code) === 7 && [1,2,3,4,5].includes(Number(x.response_code)))
      .map(x => [String(x.response_code), x.count])
  );
  const germanyNeverSubstantiveN = Object.values(germanyNeverResponses).reduce((s,n)=>s+n,0);
  if (de.q10d.screen_never_n !== 67 || de.q10d.nap_n !== 56 || germanyNeverSubstantiveN !== 11 ||
      germanyNeverResponses["1"] !== 0 || germanyNeverResponses["2"] !== 0 ||
      germanyNeverResponses["3"] !== 3 || germanyNeverResponses["4"] !== 2 || germanyNeverResponses["5"] !== 6) {
    throw new Error("Germany Q10d routing discrepancy changed; inspect source before continuing.");
  }
  if (countriesByName.Canada.literal_eng_n !== 0 || countriesByName.Canada.n !== 1342) throw new Error("Canada language filter validation failed.");
  const protectedFiles = [
    path.join(ROOT,"SurveyData_DE_US.xlsx"),
    path.join(ROOT,"Prompts","conditions.xlsx"),
    path.join(ROOT,"Prompts","prompts.csv"),
    path.join(ROOT,"Prompts","build_prompts.py"),
  ].map(p=>path.isAbsolute(p)?p:path.join(ROOT,p));
  const beforeHashes = new Map();
  for (const p of protectedFiles) beforeHashes.set(p, hashBytes(await fs.readFile(p)));

  const workbook = Workbook.create();
  const sheetNames = [
    "Read Me","Item Crosswalk",...ITEMS.map(x=>x.sheet),"Distributions Long","Q10d Routing","Language Weights QA",
  ];
  const sheets = Object.fromEntries(sheetNames.map(n=>[n,workbook.worksheets.add(n)]));

  notes(sheets["Read Me"],"ISSP 2024 Digital Societies — multi-country survey distributions",[
    ["Source and release",`ZA10020_v2-0-0.dta, Release ${data.version}; DOI 10.4232/5.ZA10020.2.0.0. Respondent-level pooled file: ${data.rows.toLocaleString()} rows × ${data.variables} variables. Source path supplied at run time.`],
    ["Scope", "Germany, Austria, Switzerland, USA, Australia, and Canada English-interview subset only. England, Scotland, and New Zealand are excluded."],
    ["Prompt-language groups", "German prompt: Germany, Austria, Switzerland. English prompt: USA, Australia, Canada. These labels describe prompt language, not necessarily interview language."],
    ["Language composition", "Switzerland full sample: German 2,129; French 731; Italian 168. USA full sample: English 1,534; Spanish 56. Canada is restricted to the observed INTLANG value eng (English), N=1,342; literal eng matches zero records."],
    ["Unweighted method", "All counts and percentages are unweighted. No survey weight has been applied. Each item sheet shows percentages of the full selected sample, including special codes, plus a separate substantive-only percentage and denominator."],
    ["Q10d denominator views", "Both views are retained: A) eligible-screen base, Q1 codes 1–6; B) substantive-response base, v26 codes 1–5. Neither is designated the single correct denominator. Q1=7 and Q1=-9 screen cases remain visible in Q10d Routing."],
    ["Q10d routing discrepancy", "Germany has 67 Q1=7 cases and 56 v26=-4 NAP cases. The remaining 11 cases have substantive v26 responses (3=3, 4=2, 5=6). No cases are recoded or forced to NAP."],
    ["Special codes", "Retain -4 NAP, -8 can't choose, and -9 no answer separately. v47 also has a pooled -6 Poland-specific NAP label; it is included as a zero-count declared category when absent from the selected samples."],
    ["Labels and zero counts", "Response codes and labels come from the DTA value-label metadata. Every declared code is listed for each selected country; a raw count of 0 means declared but not observed, not unavailable. System-missing values, if present, are counted in a separate SYSMIS row and included in the raw-count reconciliation."],
    ["Weighting", "Available fields: DWEIGHT_HH, DWEIGHT_TS, DWEIGHT_COM, PSWEIGHT, WEIGHT_COM. Documentation conflicts remain unresolved; none is selected or applied. Canada PSWEIGHT suitability for the English subset is unresolved. Switzerland observed weight fields are constant 1."],
    ["Comparability", "Preserve wording from country forms. Q20 media/platform examples vary; Q28a names each country's state/government or Swiss authorities; Q34 explicitly names each country. These are comparability caveats, not proven equivalent wording."],
    ["Source documents", "Country wording, response categories, and routing references are listed row by row on Item Crosswalk. Background-variable page references for weight notes appear on Language Weights QA. The DTA includes labels; separate missing-code listing is ZA10020_v2-0-0_missing.txt."],
    ["Percent interpretation", "Full-sample percentages use the selected country sample N; substantive, special-code, and any system-missing percentages together sum to 100%. Substantive-only percentages use only the item's substantive response codes. Q10d separately reports eligible-screen percentages and substantive-only percentages."],
  ]);

  const cwHeaders = ["Project item","Country","Prompt-language group","Pooled DTA variable","DTA variable label","Project topic label (not GESIS wording)","Official questionnaire ID","Official question wording/excerpt","DTA response codes and value labels","Special-code handling","Country wording / comparability note","Routing / base","Comparability status","Questionnaire source and page","Background-variable source"];
  const crossRows = buildCrosswalk(data);
  table(sheets["Item Crosswalk"],cwHeaders,crossRows,"ItemCrosswalkTable",1);

  const longHeaders = ["Country","Prompt-language group","Sample filter","Project item","Project topic label","Pooled DTA variable","Original response code","Original DTA response label","Special/missing status","Raw count","Item base N","Selected sample N","Full-sample denominator N","Percent of full sample","Substantive denominator N","Substantive-only percent","Q10d eligible-screen denominator N","Q10d count in eligible base","Percent of Q10d eligible-screen base","Denominator definition","Questionnaire source/page"];
  const longRows = buildLong(data);
  const longInfo = table(sheets["Distributions Long"],longHeaders,longRows,"DistributionsLongTable",1);
  for (const col of [14,16,19]) sheets["Distributions Long"].getRange(`${columnName(col)}2:${columnName(col)}${longInfo.endRow}`).format.numberFormat = "0.00%";
  for (const col of [10,11,12,13,15,17,18]) sheets["Distributions Long"].getRange(`${columnName(col)}2:${columnName(col)}${longInfo.endRow}`).format.numberFormat = "#,##0";

  for (const item of ITEMS) {
    const sheet = sheets[item.sheet];
    const rows = longRows.filter(r=>r[3]===item.id).map(r=>[
      r[0],r[1],r[2],r[5],r[6],r[7],r[8],r[9],r[11],r[10],r[12],r[13],r[14],r[15],r[19],r[20],
    ]);
    const headers = ["Country","Prompt-language group","Sample filter","Source variable","Original response code","Original response label","Special/missing status","Raw count","Selected sample N","Item base N","Full-sample denominator N","Percent of full sample","Substantive denominator N","Substantive-only percent","Denominator definition","Questionnaire source/page"];
    const info = table(sheet,headers,rows,`${item.id.replace(/[^A-Za-z0-9]/g,"")}DistributionTable`,1);
    sheet.getRange(`L2:L${info.endRow}`).format.numberFormat = "0.00%";
    sheet.getRange(`N2:N${info.endRow}`).format.numberFormat = "0.00%";
    for (const col of [8,9,10,11,13]) sheet.getRange(`${columnName(col)}2:${columnName(col)}${info.endRow}`).format.numberFormat = "#,##0";
  }

  const qSheet = sheets["Q10d Routing"];
  notes(qSheet,"Q10d routing audit — both denominator views retained",[
    ["View A: eligible-screen base","Denominator is Q1 codes 1–6. Q1=7, Q1=-9, and system-missing screen cases remain in the full cross-tab and are not silently dropped from the audit."],
    ["View B: substantive-response base","Denominator is all observed v26 codes 1–5. This is shown separately and does not imply screen eligibility."],
    ["Special response codes","v26 -4 NAP, -8 can't choose, -9 no answer remain separate. Any other observed code is retained. Cross-tab includes zero-count combinations for declared codes."],
    ["Germany check","Q1=7 N=67; v26=-4 N=56; 11 cases have substantive v26 values (3=3, 4=2, 5=6). No recode is applied."],
  ]);
  const qSummaryHeaders = ["Country","Prompt-language group","Selected sample N","Q1=1–6 eligible-screen N","Q1=7 never N","Q1=-9 no-answer N","Q1 system-missing N","v26 substantive 1–5 N","v26 system-missing N","v26 -4 NAP N","v26 -8 can't choose N","v26 -9 no answer N","Other v26 N","Q1=7 minus v26=-4 discrepancy count"];
  const qSummaryRows = data.countries.map(c=>[
    c.name,c.group,c.n,c.q10d.eligible_n,c.q10d.screen_never_n,c.q10d.screen_no_answer_n,c.q10d.screen_system_missing_n,
    c.q10d.substantive_n,c.q10d.response_system_missing_n,c.q10d.nap_n,c.q10d.cant_choose_n,c.q10d.no_answer_n,c.q10d.other_n,
    c.name==="Germany"?c.q10d.screen_never_n-c.q10d.nap_n:null,
  ]);
  table(qSheet,qSummaryHeaders,qSummaryRows,"Q10dSummaryTable",8);
  const qHeaders = ["Country","Prompt-language group","Screen variable","Q1 raw code","Q1 label","Screen group","Eligibility in view A","Q10d variable","Q10d raw code","Q10d label","Raw joint count","Full sample N","Percent of full sample","View A eligible denominator N","View A joint count","Percent of eligible-screen base","View B substantive denominator N","View B substantive count","Percent of substantive-response base","Special/missing status"];
  const qRows=[];
  for (const c of data.countries) {
    const q=c.q10d;
    for (const cell of q.cross_counts) {
      const sc=cell.screen_code, rc=cell.response_code, count=cell.count;
      const q1label=sc==="SYSMIS"?"System missing":sc==="ALL"?"All screen cases":(q.screen_codes[sc]||"Observed/unlabeled code");
      const q10label=rc==="SYSMIS"?"System missing":rc==="ALL"?"All response codes":(q.q10_codes[rc]||"Observed/unlabeled code");
      const eligible=Number(sc)>=1&&Number(sc)<=6;
      const substantive=Number(rc)>=1&&Number(rc)<=5;
      qRows.push([
        c.name,c.group,"v1",sc==="SYSMIS"?"SYSMIS":sc==="ALL"?"ALL":Number(sc),q1label,
        sc==="SYSMIS"?"screen system missing":sc==="-9"?"screen no answer":sc==="7"?"never":eligible?"known use (Q1 1–6)":"other screen code",
        eligible?"Yes":"No","v26",rc==="SYSMIS"?"SYSMIS":rc==="ALL"?"ALL":Number(rc),q10label,
        count,c.n,c.n?count/c.n:null,eligible?q.eligible_n:null,eligible?count:null,
        eligible&&q.eligible_n?count/q.eligible_n:null,substantive?q.substantive_n:null,substantive?count:null,
        substantive&&q.substantive_n?count/q.substantive_n:null,
        rc==="SYSMIS"?"System missing":specialStatus(data.items.Q10d,rc),
      ]);
    }
  }
  const qInfo=table(qSheet,qHeaders,qRows,"Q10dFullRoutingTable",15);
  for (const col of [13,16,19]) qSheet.getRange(`${columnName(col)}16:${columnName(col)}${qInfo.endRow}`).format.numberFormat="0.00%";

  const qa = sheets["Language Weights QA"];
  notes(qa,"Language, weights, and validation",[
    ["Language scope","Prompt-language group labels do not establish interview language. USA and Switzerland are intentionally retained as full country samples; Canada is restricted using the exact observed English label."],
    ["Weight policy","No weight applied. The fields below are inventoried only; resolve official documentation and target-population fit before producing weighted percentages."],
    ["Validation","Source counts, item code totals, labels, Canada filter, Q10d full cross-tabs, and German discrepancy are checked by the preparation script before export."],
    ["Special codes","Special and missing categories remain separate. Declared but unobserved response codes appear with zero count in the distribution sheets."],
  ]);
  const languageRows=[];
  for (const c of data.countries) for (const [lang,n] of Object.entries(c.language_counts)) {
    languageRows.push([c.name,c.group,lang,n,c.n,c.language_filter,c.name==="Switzerland"?"Full multilingual sample":c.name==="USA"?"Full sample includes English and Spanish interviews":c.name==="Canada"?"Selected subset is English interview language":"Observed sample language"]);
  }
  table(qa,["Country","Prompt-language group","Observed INTLANG value","Full-country count for value","Selected sample N","Selected-sample policy","Interpretation"],languageRows,"LanguageCompositionTable",8);
  const weightRows=[];
  for (const c of data.countries) for (const w of ["DWEIGHT_HH","DWEIGHT_TS","DWEIGHT_COM","PSWEIGHT","WEIGHT_COM"]) {
    const s=c.weights[w];
    weightRows.push([c.name,w,s.missing_n,s.distinct_n,s.min,s.max,"No",COUNTRY_DOCS[c.name].weight]);
  }
  const weightStart=10+languageRows.length+2;
  table(qa,["Country","Weight variable","Missing N","Distinct values N","Observed minimum","Observed maximum","Applied","Documentation note"],weightRows,"WeightInventoryTable",weightStart);
  const qaRows=[];
  for (const c of data.countries) for (const item of ITEMS) {
    const d=c.items[item.id];
    const total=Object.values(d.counts).reduce((s,n)=>s+n,0);
    const meta=data.items[item.id];
    const substantiveN=meta.substantive.reduce((s,x)=>s+(d.counts[String(x)]||0),0);
    const pctSum=meta.substantive.reduce((s,x)=>s+(d.counts[String(x)]||0),0)/substantiveN;
    qaRows.push([c.name,item.id,d.item_base_n,d.system_missing_n,total,c.n,total===c.n?"PASS":"FAIL",substantiveN,substantiveN?pctSum:null,substantiveN&&Math.abs(pctSum-1)<1e-9?"PASS":"FAIL"]);
  }
  const qaStart=weightStart+weightRows.length+3;
  const qaInfo=table(qa,["Country","Item","Item base N","System-missing N","Raw code count sum","Selected sample N","Count reconciliation","Substantive N","Substantive percentage total","Substantive percentage check"],qaRows,"CountValidationTable",qaStart);
  qa.getRange(`I${qaStart+1}:I${qaInfo.endRow}`).format.numberFormat="0.00%";
  const finalChecks = [
    ["Canada exact INTLANG filter",countriesByName.Canada.n===1342?"PASS":"FAIL",`eng (English) N=${countriesByName.Canada.n}; literal eng N=${countriesByName.Canada.literal_eng_n}`],
    ["Germany Q10d discrepancy",de.q10d.screen_never_n===67&&de.q10d.nap_n===56&&germanyNeverSubstantiveN===11?"PASS":"FAIL",`Q1=7: 67; v26=-4: 56; substantive among Q1=7: 11 (code 3: ${germanyNeverResponses["3"]}, code 4: ${germanyNeverResponses["4"]}, code 5: ${germanyNeverResponses["5"]}).`],
    ["Weights", "PASS", "No weight applied."],
    ["Pooled data release",data.version.startsWith("2.0.0")?"PASS":"FAIL",`${data.version}; ${data.rows} rows × ${data.variables} variables`],
  ];
  const checkStart=qaStart+qaRows.length+3;
  table(qa,["Validation","Status","Details"],finalChecks,"FinalChecksTable",checkStart);

  for (const name of sheetNames) {
    const sheet=sheets[name];
    sheet.showGridLines=false;
  }
  workbook.recalculate();

  // Independent source-level checks before export.
  for (const c of data.countries) {
    for (const item of ITEMS) {
      const itemData=c.items[item.id];
      const allCodes=Object.values(itemData.counts).reduce((s,n)=>s+n,0);
      if (allCodes!==c.n) throw new Error(`Raw counts fail to reconcile for ${c.name}/${item.id}.`);
      if (itemData.item_base_n+itemData.system_missing_n!==c.n) throw new Error(`Observed plus system-missing N fails to reconcile for ${c.name}/${item.id}.`);
    }
    const q=c.q10d;
    const crossTotal=q.cross_counts.reduce((s,x)=>s+x.count,0);
    if (crossTotal!==c.n) throw new Error(`Q10d cross-tab fails to reconcile for ${c.name}.`);
    for (const [code,n] of Object.entries(c.items.Q1.counts)) {
      const margin=q.cross_counts.filter(x=>x.screen_code===code).reduce((s,x)=>s+x.count,0);
      if (margin!==n) throw new Error(`Q10d screen margin fails for ${c.name}/Q1=${code}.`);
    }
    for (const [code,n] of Object.entries(c.items.Q10d.counts)) {
      const margin=q.cross_counts.filter(x=>x.response_code===code).reduce((s,x)=>s+x.count,0);
      if (margin!==n) throw new Error(`Q10d response margin fails for ${c.name}/v26=${code}.`);
    }
    const eligibleCrossN=q.cross_counts.filter(x=>Number(x.screen_code)>=1&&Number(x.screen_code)<=6).reduce((s,x)=>s+x.count,0);
    if (eligibleCrossN!==q.eligible_n) throw new Error(`Q10d eligible-screen base fails for ${c.name}.`);
  }

  const tempDir=await fs.mkdtemp(path.join(os.tmpdir(),"survey-multicountry-build-"));
  try {
    const tempOutput=path.join(tempDir,"SurveyData_MultiCountry.xlsx");
    const xlsx=await SpreadsheetFile.exportXlsx(workbook);
    await xlsx.save(tempOutput);
    const reopen=await SpreadsheetFile.importXlsx(await FileBlob.load(tempOutput));
    validateExportedTables(reopen,sheetNames);
    const previewDir=path.join(tempDir,"previews");
    await fs.mkdir(previewDir);
    for (let i=0;i<sheetNames.length;i++) {
      const name=sheetNames[i];
      const preview=await reopen.render({sheetName:name,autoCrop:"all",scale:0.8,format:"png"});
      const bytes=new Uint8Array(await preview.arrayBuffer());
      if (!bytes.length) throw new Error(`Could not render sheet ${name}.`);
      await fs.writeFile(path.join(previewDir,`${String(i+1).padStart(2,"0")}.png`),bytes);
    }

    const changed=[];
    for (const p of protectedFiles) {
      const after=hashBytes(await fs.readFile(p));
      if (after!==beforeHashes.get(p)) changed.push(p);
    }
    if (changed.length) throw new Error("Protected input changed during build: " + changed.join(", "));

    // Exclusive copy closes the check-then-save race: an existing target is never replaced.
    await fs.copyFile(tempOutput,args.output,fsConstants.COPYFILE_EXCL);
  } finally {
    await fs.rm(tempDir,{recursive:true,force:true});
  }
  console.log(JSON.stringify({
    output:args.output,source:args.data,release:data.version,source_shape:[data.rows,data.variables],
    country_Ns:Object.fromEntries(data.countries.map(c=>[c.name,c.n])),
    canada_literal_eng_N:countriesByName.Canada.literal_eng_n,
    sheet_names:sheetNames,distribution_rows:longRows.length,crosswalk_rows:crossRows.length,
    q10d_germany:{q1_never:de.q10d.screen_never_n,v26_nap:de.q10d.nap_n,substantive_among_never:germanyNeverSubstantiveN,substantive_codes_among_never:germanyNeverResponses},
    protected_inputs_unchanged:true,temporary_previews_cleaned:true,
  },null,2));
}

main().catch(err=>{console.error(err?.stack||err);process.exitCode=1;});
