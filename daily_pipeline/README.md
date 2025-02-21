# Daily Pipeline

## Overview

The **Daily Pipeline** automates the extraction, transformation, and loading of court judgment data from the UK National Archives. This pipeline processes XML judgments, extracts metadata, summarizes case details using AI, and loads the structured data into a PostgreSQL database.

## Components

The pipeline consists of the following stages:

1. **Daily Extract**: Downloads court judgments in XML format.
2. **Daily Prompt Engineering**: Uses OpenAI's GPT model to extract case summaries from judgments.
3. **Daily Transform**: Converts and structures judgment data for database ingestion.
4. **Daily Load**: Seeds the parsed and structured data into the database and uploads HTML versions to S3.

---

## File Breakdown

### `<span>daily_pipeline.py</span>`

This is the main entry script that orchestrates the entire process. It performs the following:

* Loads environment variables from `<span>.env</span>`.
* Initializes logging and API/database connections.
* Calls the extraction module to download new judgments.
* Transforms and processes XML judgments using OpenAI.
* Seeds the processed data into the PostgreSQL database.
* Uploads judgment HTML versions to AWS S3.
* Cleans up processed files after completion.

#### **Key Functions:**

* `<span>download_days_judgments("judgments")</span>` - Downloads XML judgments.
* `<span>process_all_judgments("judgments", "judgments_html", api_client)</span>` - Extracts structured data.
* `<span>seed_db_base_tables(judgment_data, conn, mappings)</span>` - Seeds base tables.
* `<span>seed_judgment_data(conn, judgment_data, updated_mappings)</span>` - Inserts judgment details.
* `<span>upload_multiple_files_to_s3(s_three, "judgments_html", ENV["BUCKET_NAME"])</span>` - Uploads parsed data to S3.

---

### `<span>daily_prompt_engineering.py</span>`

This module extracts structured data from judgment XML files using OpenAI's GPT model.

#### **Key Functions:**

* `<span>get_client(api_key: str) -> OpenAI</span>` - Returns an OpenAI client.
* `<span>get_xml_data(filename: str) -> str</span>` - Reads XML content.
* `<span>get_case_summary(model: str, client: OpenAI, case: str) -> dict</span>` - Uses GPT to extract structured information.

#### **AI Model Used:**

* GPT-4o-mini

#### **Data Extracted:**

* **Type of Crime** (Criminal or Civil)
* **Judgment Description**
* **Presiding Judge**
* **Parties Involved** (Names, Roles, Counsels, Chambers)
* **Ruling (Winning Party)**

---

### `<span>daily_transform.py</span>`

This module processes XML judgments into a structured format ready for database insertion.

#### **Key Functions:**

* `<span>process_all_judgments(folder_path: str, html_folder_path: str, api_client: OpenAI) -> list[dict]</span>`
  * Converts XML files to HTML.
  * Extracts metadata from judgments.
  * Calls OpenAI to extract structured case details.
  * Merges extracted data into a final dictionary format.

#### **Outputs:**

* List of dictionaries containing metadata, case summary, and extracted details.

---

### `<span>daily_load.py</span>`

This module seeds the extracted and transformed data into the PostgreSQL database and handles S3 uploads.

#### **Key Functions:**

* `<span>get_db_connection()</span>` - Establishes database connection.
* `<span>get_base_maps(conn)</span>` - Retrieves existing mappings from the database.
* `<span>seed_db_base_tables(judgment_data, conn, mappings)</span>` - Seeds base metadata.
* `<span>seed_judgment_data(conn, judgment_data, updated_mappings)</span>` - Loads judgment details.
* `<span>upload_multiple_files_to_s3(s_three, "judgments_html", ENV["BUCKET_NAME"])</span>` - Uploads HTML versions to AWS S3.

---

## Setup & Execution

### **Prerequisites**

* Python 3.8+
* PostgreSQL database
* AWS S3 for storage
* OpenAI API key

### **Installation**

```
pip install -r requirements.txt
```

### **Environment Variables (.env file)**

Create a `<span>.env</span>` file with the following:

```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
ACCESS_KEY=your_aws_access_key
SECRET_KEY=your_aws_secret_key
BUCKET_NAME=your_s3_bucket_name
OPENAI_KEY=your_openai_api_key
```

### **Running the Pipeline**

```
python daily_pipeline.py
```

This will execute the full pipeline, downloading and processing the latest judgments.

---

## Error Handling & Logging

* Errors during AI extraction are logged, and affected cases are skipped.
* Database operations use transaction handling to prevent corruption.
* Logs are saved using Python’s `<span>logging</span>` module.

---

## Future Enhancements

* Implement retry mechanisms for OpenAI requests.
* Optimize database queries for bulk inserts.
