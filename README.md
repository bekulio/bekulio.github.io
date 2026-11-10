# bekulio.github.io

Two pages, one site: **https://bekulio.github.io**

| Page | File | What it is |
|---|---|---|
| Election proposal (main) | `index.html` | "National-spread qualification": a party enters the Knesset only if it passes 3.25% in at least 60% of the entries on a frozen list of localities and regional councils. Hebrew. |
| Holocene Calendar | `calendar.html` | Today's date in a Holocene + International Fixed Calendar system, with Gregorian and Hebrew equivalents. Details: [docs/CALENDAR.md](docs/CALENDAR.md). |

## Election proposal

- Text: `index.html` (same content in [docs/proposal.md](docs/proposal.md))
- Simulation, data and chart: [`simulation/`](simulation/)

```
cd simulation
pip install -r requirements.txt
python final_simulation.py
```

Inputs: `expc_1.csv` (2026 results by locality, Central Elections Committee) and `downloadFile.xlsx` (localities, Central Bureau of Statistics). The simulation is static: it applies the rule to the 2026 votes without any change in voting behavior.

## Local preview

```
python3 -m http.server 8000   # then open http://localhost:8000
```
