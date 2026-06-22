"""Create the BigQuery dataset and load the forecast table via the Python client.

Used instead of the ``bq`` CLI, which cannot reach the BigQuery endpoint from some
networks (the google-cloud-bigquery client uses a different transport that does).
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    """Create the dataset (idempotent) and load ``--source`` parquet into the table."""
    from google.cloud import bigquery

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="gen-ai-2-500107")
    parser.add_argument("--dataset", default="gridpulse")
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--table", default="forecast")
    parser.add_argument("--source", type=Path, default=Path("data/forecast.parquet"))
    args = parser.parse_args()

    client = bigquery.Client(project=args.project, location=args.location)
    dataset = bigquery.Dataset(f"{args.project}.{args.dataset}")
    dataset.location = args.location
    client.create_dataset(dataset, exists_ok=True)

    table_id = f"{args.project}.{args.dataset}.{args.table}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    with args.source.open("rb") as handle:
        job = client.load_table_from_file(handle, table_id, job_config=job_config)
    job.result()
    print(f"loaded {job.output_rows} rows into {table_id}")


if __name__ == "__main__":
    main()
