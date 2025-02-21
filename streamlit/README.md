# Judgment Reader Dashboard

## Overview

Judgment Reader is a data-driven platform that enhances the discoverability, analysis, and visualization of courtroom judgments. It provides an interactive Streamlit-based dashboard for legal professionals, journalists, courts, and general users to explore judicial data efficiently.

## Features

* **Most Recent Judgment** : Displays the latest court judgment with key details.
* **Judgment of the Day** : Highlights a randomly selected judgment for insights.
* **Cases Over Time** : A visualization of the trend of cases over a period.
* **Cases by Judgment Type** : Categorizes cases based on their judgment types.
* **Cases by Court** : Compares the number of cases handled by different courts.
* **Detailed Judgment Search** : Provides a searchable database of court judgments.
* **Judicial Metrics** : Analyzes judicial performance, judge activity, and chamber comparisons.
* **Subscription for Updates** : Users can subscribe to receive daily judgment reports via email.

## Pages

1. **Explore Judgments** : Enables users to search, filter, and explore various court judgments.

* Uses `display_judgment_search` to provide a search interface for judgments.
* Connects to a database via `get_db_connection`.
* Integrates an S3 client for document retrieval.

1. **Insight of the Courts** : Provides in-depth analytics on court performance and case trends.

* Uses `display_judgments_for_court` to showcase judgments related to specific courts.
* Connects to a database via `get_db_connection`.
* Loads environment variables via `dotenv` for configuration management.

1. **Judicial Metrics** : Displays key judicial statistics and comparative metrics.

* Uses `display_judgments_by_judge` to analyze judgments per judge.
* Uses `display_number_of_judgments_by_chamber` to show chamber activity.
* Implements `compare_chambers` to evaluate chamber performance against one another.

1. **Subscribe** : Allows users to subscribe for updates and curated insights.

* Users enter their email to receive daily judgment reports.
* Validates email input using `is_valid_email`.
* Uses `create_client` to connect to an email service for sending updates.
* Implements `create_contact` to add users to the mailing list.

## Tech Stack

* **Frontend** : Streamlit for interactive UI components.
* **Backend** : PostgreSQL (with psycopg2) for data storage and retrieval.
* **Data Processing** : Pandas for data manipulation and Altair for visualizations.
* **Environment Management** : dotenv for loading environment variables.
* **Cloud Storage** : S3 client integration for document access.
* **Email Notifications** : Amazon SES (Simple Email Service) for email subscriptions.

## How to Run

1. Clone the repository.
2. Install dependencies using:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables using a `.env` file.
4. Run the Streamlit app:
   ```sh
   streamlit run main.py
   ```

## Future Enhancements

* Advanced filtering and search capabilities.
* More detailed comparative analysis between courts and chambers.
* User authentication for personalized insights.
* Integration with external legal data sources.
* Enhanced document retrieval and visualization using S3 storage.
* Expanded court performance analytics with additional metrics and visualizations.
* More advanced email subscription settings, such as frequency customization and topic selection.
