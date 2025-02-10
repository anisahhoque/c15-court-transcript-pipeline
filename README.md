# Court Transcript Pipeline

## Overview

This project automates the enhancement, discoverability, and analysis of court transcripts released daily by the National Archives. It processes plain text transcripts, extracts key information, summarizes the content using GPT-4, and provides a searchable dashboard to help the public, journalists, and researchers gain better insights into court proceedings.

## Manual Set Up

### Prerequisites
- API Key for GPT-4
- Python 3.13
- AWS Account - for deploying cloud resources
- Terraform - for setting up and tearing down cloud infrastructure

### Set Up Instructions
- `git clone https://github.com/anisahhoque/c15-court-transcript-pipeline.git`
- `cd c15-court-transcript-pipeline`
- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
