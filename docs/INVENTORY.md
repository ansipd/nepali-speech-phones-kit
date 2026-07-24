# CANONICAL PHONE INVENTORY — NSPC-Kit
# Part of docs/. Defines the authoritative phone set the frontend emits.
# Source: Standard v1.0 R2 (segmental inventory), Acharya (1991), Clements &
# Khatiwada (2009). Decision D1 (palatal च/छ) ACCEPTED.

This is the UNIVERSAL intermediate representation. Adapters (Piper, Matcha,
IPA, JSON) translate these tokens to their target format. Every token here
has exactly one IPA counterpart; the map is bidirectional.

================================================================================
1. TOKEN CONVENTIONS
================================================================================
- Tokens are ASCII, whitespace-separated in a sequence.
- A phone sequence looks like:  ʋ i k aː s   ɡʱ ʱ a r   ɦ u n
  (in token form:               vi ka:s gh ha r hu n)
- Special tokens:
    ':'  = gemination (precedes/marks a lengthened consonant; see §5)
    '.'  = word / syllable boundary pause (optional, for trainers that want it)
    'ˈ'  = primary stress (optional; computed by R4, not required for training)
- The inherent vowel is 'a' (/ə/), realized [ə]~[ʌ]. NOT 'a:'.

================================================================================
2. VOWELS  (R2.2)
================================================================================
TOKEN   IPA     DEVANAGARI TRIGGER          EXAMPLE WORD        NOTES
------  ------  -------------------------  -----------------  --------------------
a       ə       inherent (क्→k, but क→kə)   क→/kə/             mid-central; default
a:      aː      ा (दीर्घ आ)                 आम→/a:m/          low long
i       i       ि                         कि→/ki/
e       e       े                         के→/ke/
o       o       ो                         को→/ko/
u       u       ु                         कु→/ku/
u:      uː      ू (दीर्घ ऊ)                कू→/ku:/
a~      ã       ँ (candrabindu)            माँ→/mã/
i~      ĩ       ं ि (nasal i)             हिँ→/hĩ/  (rare)
u~      ũ       ं ु                       हुँ→/hũ/
e~      ẽ       ं े                       हें→/hẽ/  (rare)
o~      õ       ं ो                       हों→/hõ/  (rare)
NOTE: NO /o~/ in Nepali. Length is NOT phonemic for a/e/o/u except where R9.2
      (final ई/ऊ dirgha for strīliṅgī/bhāvavācī) forces it — handled in rules,
      not by adding more tokens.

================================================================================
3. CONSONANTS  (R2.1; alveopalatal preferred over "retroflex", Acharya 2.0.5)
================================================================================
TOKEN  IPA     DEVANAGARI   EXAMPLE
------ ------  -----------  -----------------
k      k       क            क→/kə/
kh     kʰ      ख            ख→/kʰə/
g      ɡ       ग            ग→/ɡə/
gh     ɡʱ      घ            घ→/ɡʱə/
ng     ŋ       ङ            ङ→/ŋ/
c      tʃ      च            च→/tʃə/   [D1: PALATAL, not alveolar ts]
ch     tʃʰ    छ            छ→/tʃʰə/  [D1: PALATAL, not alveolar tsh]
j      dʒ      ज            ज→/dʒə/
jh     dʒʱ     झ            झ→/dʒʱə/
ny     ɲ       ञ            ञ→/ɲ/
t      t       ट            ट→/ʈə/  (retroflex — kept distinct per Acharya)
th     tʰ      ठ            ठ→/ʈʰə/
d      d       ड            ड→/ɖə/
dh     dʱ      ढ            ढ→/ɖʱə/
n      n       ण            ण→/ɳ/
T      t       त            त→/tə/  (dental)
Th     tʰ      थ            थ→/tʰə/
D      d       द            द→/də/
Dh     dʱ      ध            ध→/dʱə/
N      n       न            न→/nə/
p      p       प            प→/pə/
ph     pʰ      फ            फ→/pʰə/
b      b       ब            ब→/bə/
bh     bʱ      भ            भ→/bʱə/
m      m       म            म→/mə/
y      j       य (onset)    य→/jə/  (coda → i, R2.3)
r      r       र            र→/rə/  (also ɾ in fast speech; one token)
l      l       ल            ल→/lə/
w      w       व (onset)    व→/wə/  (coda → u, R2.3; ब/व split R2.3/O4.5)
s      s       स            स→/sə/  (dental s)
sh     ʃ       श            श→/ʃə/  (palatal s)
S      ʂ       ष            ष→/ʂə/  (retroflex s)
h      ɦ       ह            ह→/ɦə/  (deleted post-vocalically, R3.9)
ks     kʂ      क्ष          क्ष→/kʂə/ (conjunct)
jn     dʒɲ    ज्ञ          ज्ञ→/dʒɲə/ (conjunct)
tr     t̪r      त्र          त्र→/t̪rə/ (conjunct)

NOTE on ब/व: व→/b/ in the closed Academy set (बिन्दु, बिम्ब, बेला, बार …),
      otherwise /w/ (R2.3, O4.5). Implemented as a character map, not a phone
      change.

================================================================================
4. GLIDES & SPECIAL  (R2.3)
================================================================================
य onset → j ; य coda → i (e.g. आय→/a:i/)
व onset → w ; व coda → u (e.g. नउ→/nau/)
Visarga ः → silent (R2.4), e.g. दुःख→/dukʱə/ (h also deleted).

================================================================================
5. GEMINATION  (R5.2 / R7.2)
================================================================================
A geminated consonant is represented by the SAME token twice, OR by the ':'
marker after the token. We choose the **double-token** form for trainer
compatibility (Piper/Matcha token vocabularies are flat):
    एक्घाउ /eɡ.ɡʱaːu/  →  e ɡ ɡʱ a: u
This avoids needing a separate ':' symbol in the inventory and maps cleanly to
any trainer's token list. (The IPA adapter may render as eɡ.ɡʱaːu.)

================================================================================
6. TRAINER TOKEN MAPS (generated by adapters/)
================================================================================
- PIPER: each token above → an id in phoneme_id_map (text mode). PAD=0, BOS=1,
         EOS=2, SPACE=3 reserved per Piper convention. Plus '_' pad token.
- MATCHA: tokens.txt one-per-line; symbols.py reads them. SPACE and PAD handled
         by Matcha's intersperse(.,0).
- IPA: tokens → IPA via IPA_MAP (§2–§4) for human/validation display.

These maps are PRODUCED by the adapters from THIS inventory — the inventory is
the single source of truth. Changing a phone here updates every adapter.

================================================================================
7. COVERAGE GUARANTEE
================================================================================
Every phoneme in Standard R2 is represented. The test_adapter harness asserts
100% inventory coverage (no emitted phone exists outside this file). OOV words
are resolved by U5 rules into tokens defined here — never invented symbols.
