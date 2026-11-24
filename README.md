# Berlin-Ansichten – Mini-Pipeline (Prototyp)

Kleiner Prototyp für ein offenes, annotiertes Bildkorpus von Berlin-Darstellungen:
Korpusaufbau mit Provenienz/Lizenz, Annotationsschema, Zero-Shot-Segmentierung,
zeitliche Klassifikation (Epoche) und Bias-Analyse.

## Setup (VS Code)
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
In VS Code: *Python: Select Interpreter* -> `.venv`.

## Ablauf
1. Korpus holen (Kategorienamen vorher auf commons.wikimedia.org prüfen; User-Agent in `src/fetch_commons.py` mit Kontakt ergänzen):
   `python src/fetch_commons.py --category "Category:..." --depth 1 --limit 150`
2. Annotieren: `pip install label-studio`, `label-studio start`, Projekt mit `schema/label_studio_config.xml`
   anlegen, Bilder aus `data/images` importieren, ca. 100 Bilder labeln; `medium` und `district`
   in `data/metadata.csv` nachtragen. Epoche aus Commons-Datierung prüfen und ggf. korrigieren.
3. Segmentierung (zero-shot): `python src/zero_shot_segment.py --n 60` -> Overlays in `results/overlays/`.
4. Klassifikation: `python src/train_probe.py` -> `results/metrics.json`, `results/predictions.csv`.
5. Bias-Report: `python src/bias_report.py` -> `results/bias_tables.md` + Plots.

## Methodische Hinweise
- Commons-Datierung = Aufnahmedatum der Datei, nicht zwingend die dargestellte Zeit (z. B. Foto eines Gemäldes). Epochenlabels stichprobenartig prüfen.
- Kleine Stichprobe: Test-Split ist klein, Ergebnisse als Tendenz lesen, Unsicherheit angeben.
- Auswahl über Commons-Kategorien erzeugt eigene Verzerrungen (Mitte/Wahrzeichen überrepräsentiert, Medium, Lizenz). Genau das im Report benennen.
- Lizenzen pro Bild stehen in `metadata.csv`; bei Weitergabe des Korpus Lizenzbedingungen beachten.

## Projektkarten

- [Data Card](DATA_CARD.md): Herkunft, Aufbau und Grenzen des Bildkorpus.
- [Model Card](MODEL_CARD.md): Modell, Auswertung und bekannte Einschränkungen.

## Zitieren

Zitationsangaben stehen in [`CITATION.cff`](CITATION.cff). 

## Lizenz

- Der Quellcode dieses Repositoriums steht unter der [MIT-Lizenz](LICENSE).
- Die README-Dokumentation steht, sofern nicht anders gekennzeichnet, unter
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de).
- Die annotierten Metadaten und Annotationsausgaben stehen unter
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de), sofern nicht
  anders gekennzeichnet.
- Die über Wikimedia Commons bezogenen Bilder sind nicht durch die Lizenz dieses
  Repositoriums abgedeckt. Für jede Datei gelten die in `data/metadata.csv`
  dokumentierten Lizenz- und Attributionangaben.
- Das verwendete CLIP-Modell und daraus abgeleitete Modelle haben eigene
  Nutzungsbedingungen; ihre Lizenz muss bei Weitergabe gesondert berücksichtigt
  werden.
