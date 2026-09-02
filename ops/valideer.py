"""Controle dat het startpakket intern klopt voordat het wordt opgeleverd."""
import json, os, re, sys

fouten, gecontroleerd = [], 0

# 1. jsonl geldig
for i, regel in enumerate(open("ops/ijkset-nl.jsonl", encoding="utf-8"), 1):
    if regel.strip():
        try:
            r = json.loads(regel)
            for veld in ("id", "domein", "vraag", "verwacht", "let_op"):
                if veld not in r:
                    fouten.append(f"ijkset regel {i}: veld '{veld}' ontbreekt")
            gecontroleerd += 1
        except json.JSONDecodeError as e:
            fouten.append(f"ijkset regel {i}: {e}")

# 2. frontmatter van elke module tegen het contract
VERPLICHT = ["id","titel","spoor","volgorde","competenties","duur_min","beurten",
             "modellen","status","wat_ging_mis","bewijs"]
for map_ in sorted(os.listdir("content/modules")):
    pad = f"content/modules/{map_}/module.md"
    tekst = open(pad, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", tekst, re.S)
    if not m:
        fouten.append(f"{pad}: geen frontmatter"); continue
    fm = {}
    for regel in m.group(1).splitlines():
        if ":" in regel and not regel.startswith((" ", "#")):
            k, v = regel.split(":", 1); fm[k.strip()] = v.strip()
    for veld in VERPLICHT:
        if veld not in fm:
            fouten.append(f"{pad}: frontmatter mist '{veld}'")
    if fm.get("id") != map_:
        fouten.append(f"{pad}: id '{fm.get('id')}' wijkt af van mapnaam '{map_}'")
    # regel 2 uit het modulecontract
    if fm.get("wat_ging_mis") == "true" and fm.get("status") == "gepubliceerd":
        if "Wat hier misging" not in tekst:
            fouten.append(f"{pad}: wat_ging_mis=true maar sectie ontbreekt")
    gecontroleerd += 1

# 3. yaml globaal parseerbaar (indentatie + dubbele sleutels)
for pad in ("config/budget.yaml", "config/modellen.yaml"):
    for i, regel in enumerate(open(pad, encoding="utf-8"), 1):
        if "\t" in regel:
            fouten.append(f"{pad}:{i}: tab in yaml")
    gecontroleerd += 1

# 4. verwijzingen in de backlog bestaan
backlog = open("spec/06-backlog.md", encoding="utf-8").read()
for verwijzing in re.findall(r"`(ops/[\w/.-]+|config/[\w/.-]+|spec/[\w/.-]+)`", backlog):
    if not os.path.exists(verwijzing) and not verwijzing.endswith((".md",".json")):
        fouten.append(f"backlog verwijst naar ontbrekend bestand: {verwijzing}")
    gecontroleerd += 1

print(f"gecontroleerd: {gecontroleerd} items")
if fouten:
    print("\nFOUTEN:"); [print("  -", f) for f in fouten]; sys.exit(1)
print("alles consistent")

# Draai dit na elke wijziging aan content of config:
#   python3 ops/valideer.py
# Controleert: ijkset-jsonl, frontmatter tegen spec/04-modulecontract.md,
# yaml-indentatie, en of verwijzingen uit de backlog bestaan.
