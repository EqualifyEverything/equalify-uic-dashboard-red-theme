# UIC Red Theme Accessibility Report Generator

This Python CLI app processes accessibility scan results for public URLs on the UIC Red Theme website. It generates summary reports including:

- **Pages Scanned**: Total number of public URLs scanned
- **Total Violations**: Total number of accessibility violations found
- **Unique Nodes**: Total number of unique HTML nodes with violations

## File Structure

- `output.csv`: Contains metadata and links to individual scan result JSON files
- `results/`: Folder containing individual JSON files with accessibility violation data
- `equalify-uic-dashboard-red-theme.py`: Python CLI script to generate accessibility reports

## How to Run the Report Generator

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_ORG/equalify-uic-dashboard-red-theme.git
cd equalify-uic-dashboard-red-theme
```

### 2. Install dependencies

Make sure you have Python 3.8+ and pip installed. Then run:

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
pip install -r requirements.txt
```

### 3. Add Data Files

Ensure you have:
- `output.csv` in the root directory
- A `results/` folder containing all JSON files referenced in `output.csv`

### 4. Run the report generator

```bash
python equalify-uic-dashboard-red-theme.py
```

The script will process the data and generate CSV reports.

## Output CSV Files

The script generates the following CSV files:

- `output-summary.csv`: Summary of scan results including pages scanned, total violations, and unique nodes.
- `output-nodes.csv`: Details of unique HTML nodes where violations were found.
- `output-violation_messages.csv`: List of distinct violation messages identified during scans.

## License

This project is open source and available under the MIT License.
