![AI BI Co-Pilot screenshot](AI%20BI%20COPILOT.png)
<img width="1902" height="860" alt="AI Verification Layer" src="https://github.com/user-attachments/assets/3c580135-119a-417f-aa5b-39bc6f14e6a1" />
<img width="1897" height="697" alt="Green results" src="https://github.com/user-attachments/assets/92ea1541-6f40-49c8-b8e4-d2f654118ec2" />



# AI BI Co-Pilot

Ask a business question in plain English. The AI writes the SQL, runs it, explains what it means, and tells you how much to trust the answer.

## Live Demo

https://charulata-ai-copilot.streamlit.app

## What it does

You type a question like "how many users are inactive" or "average listening hours by subscription type." The tool sends it to an AI model, which writes the SQL, runs it against the data, and returns the answer as a number, table, or chart, along with a plain-English business interpretation.

No SQL knowledge needed to use it.

## Features

- Natural language to SQL using the OpenAI API
- Reliability layer that rates each answer green, yellow, or red, flagging small sample sizes, differences too small to be meaningful, and low data coverage
- Plain-English translation of every query, so a non-technical user can verify the logic behind an answer
- Business-insight layer that interprets the result, not just returns the number
- Read-only safety guardrail that blocks any destructive query
- Self-correcting queries: if a query fails, the tool sends the error back to the AI and retries
- Automatic bar, line, and area charts for grouped results
- Built-in demo dataset (50,000 records) plus CSV upload for your own data

## Why the reliability layer matters

AI tools are built to sound confident, giving a clean answer whether or not the data supports it. More than half of companies say they can't verify whether AI-generated analysis is trustworthy. This tool addresses that by checking its own results and telling the user when not to act on a number.

## Built with

Python, OpenAI API, SQL, DuckDB, Streamlit, pandas

## Author

Charulata Ranbhare
