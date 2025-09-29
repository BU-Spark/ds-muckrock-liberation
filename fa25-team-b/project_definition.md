# Project Definition

## Problem Statement
Slot machines on overseas U.S. military bases generate tens of millions of dollars in annual revenue, yet there is little transparency into how this money is distributed across bases, branches, and regions, or what it implies for the gambling risks faced by service members. Without clear, accessible analysis, policymakers and the public cannot fully understand which bases present the highest risks, which games are most associated with addiction, or how revenue trends have evolved over time. This lack of insight hinders informed oversight and limits the ability to address potential gambling-related harms within the military.

## Data
The data for this project comes from the Army Recreation Machine Program (ARMP), which currently operates **1,889 slot machines across 79 overseas military bases** and generated **$70.9 million in revenue during FY2024**.

MuckRock has obtained a cache of official records delivered as unstructured PDFs containing tabular financial and asset information. The available documents include:

- District Revenues (FY2020–FY2024)  
- Financial Statements  
- Annual Asset Reports (FY2020–FY2024)  
- Marine Revenue Reports (FY2020–FY2024)  
- Navy Revenue Reports (FY2020–FY2024)  
- Revenue Comparison Reports  
- Presentations and supporting files  

## Project Objectives / Goals
- Extract, clean, and standardize ARMP slot machine records into a structured dataset.  
- Deploy a SQLite/Datasette interface that enables interactive browsing and visualization of revenues.  
- Explore patterns of revenue distribution, trends over time, and game types linked to gambling risks.  
- Provide recommendations to support transparency and responsible gaming practices.  

## Scope
The scope of this project includes:  
- Data extraction from PDFs  
- Cleaning and normalization of records  
- Exploratory analysis of slot machine revenues  
- Data visualization  
- Database deployment for public access  
- Report preparation summarizing findings and recommendations  

## Deliverables
- A cleaned and documented dataset of ARMP slot machine revenues.  
- A reproducible extraction and cleaning pipeline in Python.  
- A deployed SQLite/Datasette instance for browsing and visualization.  
- A written report summarizing findings, limitations, and recommendations.  
