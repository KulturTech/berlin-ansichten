# Data Card: Berlin-Ansichten

## Kurzbeschreibung

Ein kleiner, explorativer Bildkorpus mit Ansichten von Berlin und zugehörigen
Provenienz- und Datierungsangaben. Er wurde für den Prototyp einer Pipeline zur
Annotation, Segmentierung und zeitlichen Klassifikation zusammengestellt.

## Herkunft und Erhebung

- Quelle: Wikimedia Commons, Kategorie `Category:Views of Berlin`
- Abruf: 24. November 2026 mit `src/fetch_commons.py`, Kategorie-Tiefe 0,
  Abruflimit 150 Dateien
- Erfasster Stand: 30 Bilder in `data/images` und 30 Einträge in
  `data/metadata.csv`
- Auswahl: JPEG- und PNG-Dateien, die das Skript anhand der Commons-Lizenzangabe
  als frei lizenziert erkennt. Die Auswahl ist eine Kategorien-Stichprobe, keine
  systematische oder repräsentative Erhebung.

## Inhalt

Die Metadaten enthalten unter anderem Commons-Dateititel, Kategorie, Quell- und
Bild-URL, Lizenzangaben, Urheber- und Credit-Felder, Beschreibung,
Datumsangabe, abgeleitete Jahreszahl und Epochenklasse. `medium` und `district`
sind für manuelle Annotation vorgesehen.

Im erfassten Stand verteilen sich die Epochenlabels wie folgt:

| Epoche | Bilder |
| --- | ---: |
| `ab_1990` | 25 |
| `vor_1900` | 3 |
| `1900_1945` | 1 |
| `1946_1989` | 1 |

Die Epochen werden aus Commons-Datumsmetadaten abgeleitet. Sie beschreiben nicht
notwendigerweise die dargestellte Zeit: Zum Beispiel kann ein jüngeres Foto ein
historisches Gemälde zeigen.

## Lizenzen und Weitergabe

Für jedes Bild gelten die Lizenz- und Attributionsbedingungen auf der jeweiligen
Commons-Dateiseite; die Angaben im CSV dienen als Provenienz und ersetzen keine
Prüfung der Originalseite. Die Projektlizenz überträgt sich nicht auf die
Bilder oder fremde Metadatentexte. Vor Weitergabe sind die einzelnen
Lizenzbedingungen zu beachten.

## Bekannte Einschränkungen

- Eine einzelne Commons-Kategorie erzeugt Selektionsverzerrungen; bekannte
  Wahrzeichen, häufig fotografierte Orte und jüngere Bilder können
  überrepräsentiert sein.
- Der kleine Umfang und die seltenen historischen Epochen erlauben keine
  belastbaren Aussagen über Berlin-Darstellungen insgesamt.
- Datumsfelder können fehlen, ungenau sein oder das Erstellungsdatum des Bildes
  statt der dargestellten Epoche beschreiben.
- Lizenz- und Metadaten stammen von Commons und können unvollständig sein.
