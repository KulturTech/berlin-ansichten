# Model Card: Zeitliche Klassifikation von Berlin-Ansichten

## Modell und Zweck

Der Prototyp in `src/train_probe.py` vergleicht zwei Ansätze zur Zuordnung
eines Bildes zu einer Epoche:

- Zero-shot-Vorhersage mit Textprompts und dem vortrainierten
  `openai/clip-vit-base-patch32`-Modell.
- Eine logistische Regression auf normalisierten CLIP-Bildmerkmalen.

Das Modell ist für Experimente und Demonstrationen gedacht, nicht für
Entscheidungen mit Auswirkungen auf Personen, Institutionen oder historische
Dokumentation.

## Daten und Labels

Eingabe sind die Bilder und Epochenlabels aus der [Data Card](DATA_CARD.md).
Labels werden aus dem Commons-Datumsfeld abgeleitet; sie sind nicht zwingend
eine verlässliche Kennzeichnung der dargestellten Zeit. Klassen mit weniger
als zwei Beispielen werden für den Train/Test-Vergleich ausgeschlossen.

## Auswertung

Ein protokollierter Lauf verwendete 28 Bilder aus zwei Klassen (`ab_1990`: 25,
`vor_1900`: 3), mit einem festen, stratifizierten 70/30-Split
(`random_state=0`). Das Testset umfasste 9 Bilder.

| Verfahren | Macro-F1 |
| --- | ---: |
| CLIP Zero-shot | 1,00 |
| CLIP-Merkmale + logistische Regression | 0,80 |

Die Ergebnisse sind wegen des sehr kleinen und unausgewogenen Datensatzes
nicht belastbar. Insbesondere enthält das Testset nur ein Beispiel aus
`vor_1900`; der perfekte Zero-shot-Wert ist daher kein Nachweis allgemeiner
Leistungsfähigkeit. Frühere Epochenklassen mit je nur einem Bild waren vom
Vergleich ausgeschlossen.

## Risiken und Grenzen

- Verwechslung von Aufnahmedatum und dargestellter Zeit kann zu falschen Labels
  und irreführenden Vorhersagen führen.
- Die Kategorieauswahl und Lizenzverfügbarkeit erzeugen Verzerrungen, die sich
  in den Vorhersagen spiegeln können.
- CLIP ist ein allgemeines Bild-Text-Modell und wurde nicht für die historische
  Einordnung von Berlin-Ansichten feinabgestimmt.
- Ergebnisse sollten nicht als verlässliche Datierung verwendet werden;
  Vorhersagen benötigen menschliche Prüfung und fachlichen Kontext.

## Reproduzierbarkeit und Lizenzen

Der Modellbezeichner ist `openai/clip-vit-base-patch32`; die Gewichte werden
beim ersten Lauf über Hugging Face geladen. Der aktuelle Code pinnt keinen
Modell-Commit, daher können spätere Modelländerungen die Reproduktion
beeinflussen. Für CLIP und die Bilddaten gelten ihre jeweiligen Upstream- und
Commons-Lizenzbedingungen; die MIT-Lizenz dieses Repositoriums ersetzt diese
nicht.
