__author__ = "Kira Klimt, Daniel Braun"
__copyright__ = "Copyright 2020, Technical University of Munich"
__license__ = "MPL"
__version__ = "1.0"
__maintainer__ = "Daniel Braun"
__email__ = "daniel.braun@tum.de"
__status__ = "Production"

from lxml import etree as ET
from collections import defaultdict
import re

namespace = "{http://www.mediawiki.org/xml/export-0.10/}"

# Extract German words from Wiktionary
def parseWiktionary(wiktionary_filepath):
    print("Parsing wiktionary...")
    lexicon = ET.Element('lexicon')
    wordID = 1
    verbsCounter = 0
    nounsCounter = 0
    adjCoutner = 0
    advCounter = 0
	 
    for event, elem in ET.iterparse(wiktionary_filepath, recover = True):
        # general word information
        base = ""
        category = ""
        genus = ""
        plural = ""
        
        # flag if entry for this word should be created
        create = False
        
        # is there a flexion entry for this word
        flexion = False

        # attributes for verb flexion
        regular = False
        separable = False # some verbs in german are separable, e.g. "widerspiegelt" -> "es spiegelt wider"
        part1 = "" # part 1 widerspiegeln = wider
        flexword = ""
        reflexive = False
        plur_firstPers = ""
        plur_secPers = ""
        # tense form for verbs: preterite participle II,...
        pret = ""
        part2 = ""
        firstPers = ""
        secPers = ""
        thirdPers = ""
        past = False

        # inflected noun forms according to grammatical cases
        gen_sin = ""
        gen_pl = ""
        dat_sin = ""
        dat_pl = ""
        akk_sin = ""
        akk_pl = ""
        
        # comparative and superlative for adjectives
        comp = ""
        sup = ""
        
        if elem.tag != namespace+'page':
            continue
        # parse title (word)
        title = elem.find('./' + namespace + 'title')
        if title is None:
            elem.clear()
            continue
        # skip multi-base pages 
        base = title.text
        if not base or ":" in base:
            # full verb conjugation tables
            if "Flexion:" in base:
                flexion = True
                pass
            else:
                elem.clear()
                continue
        # parse futher content
        text_element = elem.find('.//' + namespace + 'text')
        # TODO: sometimes, there are tags inside text (e.g. </ref>) which casue abort. Remove them.
        if text_element is None or text_element.text is None:
            elem.clear()
            continue
        text = text_element.text.splitlines()
		
        for line in text:
            if flexion:
            # Verb flexion tables
                if "Adjektiv" in line:
                    create = False
                    break
                if line.startswith('== ') and line.endswith('==') and "({{Verbkonjugation|Deutsch}})" in line:
                    if flexword != "" and "reflexiv" not in line:
                        break
                    create = True
                    flexword =  re.split(" ", re.split("== ", line)[1])[0]
                    if flexword.startswith("[[") and flexword.endswith("]]"):
                        flexword = flexword.strip("[[]]")
                if line.startswith("{{Deutsch Verb") and line.endswith("}}"):
                    if "Deutsch" in line and (" regelmäßig" in line or "schwach" in line):
                        regular = True
                    if "Teil 1" in line: 
                        separable = True
                        part1 = re.split("\|",re.split('Teil 1=', line)[1])[0]
                    if "reflexiv" in line:
                        reflexive = True
                if "|Indikativ Präsens (wir)=" in line:
                    split_plur_firstPers = re.split("\|Indikativ Präsens (wir)|=",line)
                    plur_firstPers = split_plur_firstPers[2]
                if "|Indikativ Präsens (ihr)=" in line:
                    split_plur_secPers = re.split("\|Indikativ Präsens (ihr)|=",line)
                    plur_secPers = split_plur_secPers[2]
            else:
            # all other words
                if line.startswith('== ') and line.endswith('=='):
                    if 'Sprache|Deutsch' not in line:
                        #create = False
                        break
                if line.startswith('=== ') and line.endswith('==='):
                    if "Wortart" in line and "Deutsch" in line and ("|Substantiv|" in line or "|Verb|" in line or "|Vollverb|" in line or "|Hilfsverb|" in line or "|Adjektiv|" in line or "|Adverb|" in line or "adverb|" in line):
                        create = True
                        # get part of speech
                        split_pos = re.split('Wortart|\|',line)
                        pos = split_pos[2]
                        if pos == "Substantiv" or pos == "Abkürzung":
                            category = "noun"
                        elif "Verb" in pos or "verb" in pos and not "Adverb" in pos and not "adverb" in pos:
                            category = "verb"
                        elif "Adjektiv" in pos or "adjektiv" in pos:
                            category = "adjective"
                            adjCoutner +=1
                        elif "Adverb" in pos or "adverb" in pos:
                            category = "adverb"
                            advCounter +=1
                        else:
                            create = False
                            break
                if "Genus=" in line:
                    split_gen = re.split("Genus=",line)
                    genus = split_gen[1]
                # Some words, e.g. "Bereich", have several genus forms
                if "Genus 1=" in line:
                    split_gen = re.split("Genus 1=",line)
                    genus = split_gen[1]
                if "Nominativ Plural=" in line:
                    split_plural = re.split("Nominativ Plural=",line)
                    plural = split_plural[1]
                # Some words, e.g. "Risiko", have several plural forms
                if "Nominativ Plural 1=" in line:
                    split_plural = re.split("Nominativ Plural 1=",line)
                    plural = split_plural[1]
                    if plural == "Risikos":
                        plural = "Risiken"
                # Noun inflection regarding grammatical cases
                if category == "noun":
                    if "Genitiv Singular=" in line:
                        split_gen_sin = re.split("Genitiv Singular=",line)
                        gen_sin = split_gen_sin[1]
                    if "Genitiv Plural=" in line:
                        split_gen_pl = re.split("Genitiv Plural=",line)
                        gen_pl = split_gen_pl[1]
                    if "Dativ Singular=" in line:
                        split_dat_sin = re.split("Dativ Singular=",line)
                        dat_sin = split_dat_sin[1]
                    if "Dativ Plural=" in line:
                        split_dat_pl = re.split("Dativ Plural=",line)
                        dat_pl = split_dat_pl[1]
                    if "Akkusativ Singular=" in line:
                        split_akk_sin = re.split("Akkusativ Singular=",line)
                        akk_sin = split_akk_sin[1]
                    if "Akkusativ Plural=" in line:
                        split_akk_pl = re.split("Akkusativ Plural=",line)
                        akk_pl = split_akk_pl[1]
                    if "{{Pl.}}" in line and plural == "" and not "Lautschrift" in line:
                        split_plural = re.split(", {{Pl\.}} ", line)
                        if(len(split_plural)>1):
                            plural_help = split_plural[1]
                            plural = plural_help.replace("·", "")
                    # Different notations in Wiktionary regarding nouns without singular forms
                    if "|kein Plural=1" in line:
                        dat_sin = "\u2014"
                if category == "adjective":
                    if "Komparativ=" in line:
                        split_comp = re.split("Komparativ=",line)
                        comp = split_comp[1]
                    if "Superlativ=" in line:
                        split_sup = re.split("Superlativ=",line)
                        sup = split_sup[1]
                if ":[1]" in line and ("Vorname" in line or "Familienname" in line or "Nachname" in line):
                    create = False
                    break
                # After that, word entry with interesting fields for lexicon should be completed
                if "{{Herkunft}}" in line or "{{Synonyme}}" in line:
                    break
                # Add past tenses
                if "{{Prät.}}" in line and "{{Part.}}" in line and not past:
                    line = " ".join(line.split())
                    split_pret = re.split("{{Prät\.}}|{{Part\.}}",line)
                    # preterite
                    pret = split_pret[1].replace('·', '')
                    pret = pret.strip()
                    pret = pret.strip(",")
                    # sometimes, there are multiple past versions, seperated by ",". Use only the 1st one.
                    split_pret2 = re.split(",", pret)
                    pret = split_pret2[0]
                    # participle II
                    part2 = split_pret[2].replace('·', '')
                    part2 = part2.strip()
                    part2 = part2.strip(",")
                    # sometimes, there are multiple past versions, seperated by ",". Use only the 1st one.
                    split_part2 = re.split(",", part2)
                    part2 = split_part2[0]
                    past = True
                if "|Präsens_ich" in line:
                    split_firstPers = re.split("\|Präsens_ich|=",line)
                    firstPers = split_firstPers[2]
                if "|Präsens_du" in line:
                    split_secPers = re.split("\|Präsens_du|=",line)
                    secPers = split_secPers[2]
                if "|Präsens_er" in line:
                    split_thirdPers = re.split("\|Präsens_er, sie, es|=",line)
                    thirdPers = split_thirdPers[2]
        
        # create new word entry in lexicon
        if create:
            # check if flexion, if word exists, get element, add features, if not exist new word
            if flexion:
                searchstring = './/base[text()="' + flexword + '"]'
                if len(lexicon.xpath(searchstring)) > 0:
                    if lexicon.xpath(searchstring)[0].text == flexword:
                        # print("Flexion: " + flexword + " already exists in lexikon! Enrich existing entry.")
                        # find existing entry
                        searchstringParent = './/base[text()="' + flexword + '"]/..'
                        word = lexicon.xpath(searchstringParent)[0]
                        # print(ET.tostring(word, pretty_print = True))
                else:
                    # print(flexword + " does not yet exist. Create new entry.")
                    # create new entry
                    word = ET.SubElement(lexicon, 'word')
                    baseXML = ET.SubElement(word, 'base')
                    baseXML.text = flexword
                    idXML = ET.SubElement(word, 'id')
                    idXML.text = str(wordID)
                    wordID += 1

                # add flexion information to entry
                regularXML = ET.SubElement(word, 'regular')
                regularXML.text = str(regular)
                separableXML = ET.SubElement(word, 'separable')
                separableXML.text = str(separable)
                refflexiveXML  = ET.SubElement(word, 'reflexive')
                refflexiveXML.text = str(reflexive)
                if separable:
                    refflexiveXML  = ET.SubElement(word, 'part1')
                    refflexiveXML.text = str(part1)
                
                # 1st & 3rd person plural are the same
                if plur_firstPers != "":
                    plur_firstPersXML = ET.SubElement(word, 'plFirstThirdPerPres')
                    plur_firstPersXML.text = plur_firstPers
                if plur_secPers != "":
                    plur_secPersXML = ET.SubElement(word, 'plSecPerPres')
                    plur_secPersXML.text = plur_secPers

            else:
                if category == "verb":
                    verbsCounter += 1
                    # if word already exists, i.e. was created by a flexion entry
                    searchstring = './/base[text()="' + base + '"]'
                    if len(lexicon.xpath(searchstring)) > 0:
                        if lexicon.xpath(searchstring)[0].text == base:
                            # print("Base word: " + base + " already exists in lexikon! Enrich existing entry.")
                            # find existing entry
                            searchstringParent = './/base[text()="' + base + '"]/..'
                            word = lexicon.xpath(searchstringParent)[0]
                            # print(ET.tostring(word, pretty_print = True))
                    else:
                    # word does not yet exist, create new entry
                        # print(base + " does not yet exist. Create new entry.")
                        word = ET.SubElement(lexicon, 'word')
                        baseXML = ET.SubElement(word, 'base')
                        baseXML.text = base
                        idXML = ET.SubElement(word, 'id')
                        idXML.text = str(wordID)
                        wordID += 1
                    pretXML = ET.SubElement(word, 'preterite')
                    part2XML = ET.SubElement(word, 'participle2')
                    pretXML.text = pret
                    part2XML.text = part2
                    # present = ET.SubElement(word, 'present')
                    firstPersXML = ET.SubElement(word, 'firstPerPres')
                    firstPersXML.text = firstPers
                    secPersXML = ET.SubElement(word, 'secPerPres')
                    secPersXML.text = secPers
                    thirdPersXML = ET.SubElement(word, 'thirdPerPres')
                    thirdPersXML.text = thirdPers
                
                else:
                    # non-verbs
                    word = ET.SubElement(lexicon, 'word')
                    baseXML = ET.SubElement(word, 'base')
                    baseXML.text = base
                    idXML = ET.SubElement(word, 'id')
                    idXML.text = str(wordID)
                    wordID += 1

                categoryXML = ET.SubElement(word, 'category')
                categoryXML.text = category
                
                if plural != "—" and plural !="":
                    pluralXML = ET.SubElement(word, 'plural')
                    pluralXML.text = plural
                
                if category == "noun":
                    nounsCounter += 1
                    if genus != "":
                        genusXML = ET.SubElement(word, 'genus')
                        genusXML.text = genus
                    if gen_sin != "":
                        gen_sinXML = ET.SubElement(word, 'genitive_sin')
                        gen_sinXML.text = gen_sin
                    if gen_pl != "":
                        gen_plXML = ET.SubElement(word, 'genitive_pl')
                        gen_plXML.text = gen_pl
                    if dat_sin != "":
                        dat_sinXML = ET.SubElement(word, 'dative_sin')
                        dat_sinXML.text = dat_sin
                    if dat_pl != "":
                        dat_plXML = ET.SubElement(word, 'dative_pl')
                        dat_plXML.text = dat_pl
                    if akk_sin != "":
                        akk_sinXML = ET.SubElement(word, 'akkusative_sin')
                        akk_sinXML.text = akk_sin
                    if akk_pl != "":
                        akk_plXML = ET.SubElement(word, 'akkusative_pl')
                        akk_plXML.text = akk_pl
                
                if category == "adjective":
                    if comp != "" and comp != "—":
                        compXML = ET.SubElement(word, 'comp')
                        compXML.text = comp
                    if sup != "" and sup != "—":
                        supXML = ET.SubElement(word, 'sup')
                        supXML.text = sup
               
    # Write new lexicon to file
    tree = ET.ElementTree(lexicon)
    tree.write('wiktionary-lexicon.xml', pretty_print=True, xml_declaration=True, encoding="utf-8")
    print("Done. Number of entries: " + str(wordID-1))
    print("Number of nouns: " + str(nounsCounter))
    print("Number of verbs: " + str(verbsCounter))
    print("Number of adjectives: " + str(adjCoutner))
    print("Number of adverbs: " + str(advCounter))
       
parseWiktionary('dewiktionary.xml')
