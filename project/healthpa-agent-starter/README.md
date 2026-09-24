# HealthPA Agent

Agentic AI prior-authorization and coverage assistant built for a healthcare-payer use case.

## Stage 1-2: Local setup and real CMS data ingestion

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create local environment file

Windows:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

### 4. Download real CMS Medicare coverage data

Run from the project root:

```bash
python -m src.ingestion.download_cms_ncds
```

This retrieves the CMS National Coverage Determination report and a configurable
number of NCD detail records through the public Medicare Coverage API.

### 5. Inspect the returned data structure

```bash
python -m src.ingestion.inspect_cms_data
```

Do not build embeddings yet. First inspect the real CMS document schema. Our next
stage will normalize meaningful fields such as title, coverage text, effective dates,
document identifiers, and policy sections before deciding how to chunk them.

## Why NCD first?

National Coverage Determinations are a clean starting point because they are actual
CMS national Medicare coverage policies and their report/detail API flow does not
depend on the local LCD/Article license-token workflow.

LCDs and Articles will be added after the first ingestion path is working because
many of those endpoints require acceptance of the AMA/ADA/AHA license agreement
and a short-lived bearer token.
