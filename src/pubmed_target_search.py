#!/usr/bin/env python3
"""
Search PubMed for potential drug targets based on disease keywords. 
This script performs comprehensive literature mining from PubMed to identify potential 
drug targets for specified diseases. It leverages NCBI's E-utilities API to search 
through millions of biomedical publications and extract relevant information about 
therapeutic targets, biomarkers, and molecular mechanisms.
"""
import argparse
import requests
import csv
import sys
from xml.etree import ElementTree as ET

def search_pubmed(disease, max_results=100):
    """Search PubMed for disease-related papers and extract potential targets"""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Search for papers
    search_url = f"{base_url}esearch.fcgi"
    search_params = {
        'db': 'pubmed',
        'term': f'"{disease}"[Title/Abstract] AND ("drug target" OR "therapeutic target")',
        'retmax': max_results,
        'retmode': 'xml'
    }
    
    response = requests.get(search_url, params=search_params)
    root = ET.fromstring(response.content)
    
    # Get PMIDs
    pmids = [id_elem.text for id_elem in root.findall('.//Id')]
    
    if not pmids:
        return []
    
    # Fetch abstracts
    fetch_url = f"{base_url}efetch.fcgi"
    fetch_params = {
        'db': 'pubmed',
        'id': ','.join(pmids),
        'retmode': 'xml'
    }
    
    response = requests.get(fetch_url, params=fetch_params)
    articles_root = ET.fromstring(response.content)
    
    results = []
    for article in articles_root.findall('.//PubmedArticle'):
        try:
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "No title"
            
            abstract_elem = article.find('.//AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else "No abstract"
            
            pmid_elem = article.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else "No PMID"
            
            results.append({
                'pmid': pmid,
                'title': title,
                'abstract': abstract[:500] + "..." if len(abstract) > 500 else abstract
            })
        except Exception as e:
            continue
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Search PubMed for drug targets')
    parser.add_argument('-d', '--disease', required=True, help='Disease name')
    parser.add_argument('-n', '--max-results', type=int, default=50, help='Maximum results')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file')
    
    args = parser.parse_args()
    
    print(f"Searching PubMed for '{args.disease}' targets...")
    results = search_pubmed(args.disease, args.max_results)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['pmid', 'title', 'abstract']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Found {len(results)} articles. Results saved to {args.output}")

if __name__ == "__main__":
    main()
