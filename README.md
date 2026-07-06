# OpenSpark - Bot Engine (`spark_bot`)

The core automation engine for **OpenSpark**. This background worker continuously scrapes the open internet for hackathon/project data, cleans it, runs it through an AI evaluation pipeline, stores unique ideas, and posts them to the OpenSpark ecosystem.

## The Data Pipeline
The bot engine operates in a strict sequential pipeline:
`Scraping ➔ Data Cleaning ➔ Data Modeling ➔ Store in DB ➔ DS/ML (AI Judge Basic) ➔ spark_bot ➔ Post`

## Tech Stack
- **Language:** Python 3.11+
- **Database:** PostgreSQL
- **Data Gathering:** BeautifulSoup / Playwright / Requests
- **AI/ML Layer:** LangChain / OpenAI API (or custom RAG framework wrapper)

## Targeted Data Sources
- Devfolio
- DevPost
- Unstop