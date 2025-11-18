#!/bin/bash

# Script to run pydantic_diversification_analyst.py for all PDF files in aux/pdfs

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directory containing PDFs
PDF_DIR="aux/pdfs"

# Check if directory exists
if [ ! -d "$PDF_DIR" ]; then
    echo -e "${RED}Error: Directory $PDF_DIR does not exist${NC}"
    exit 1
fi

# Count total PDFs
total_pdfs=$(find "$PDF_DIR" -name "*.pdf" -type f | wc -l)
echo -e "${BLUE}Found $total_pdfs PDF files to process${NC}"
echo ""

# Counter for processed files
counter=0

# Loop through all PDF files
for pdf_file in "$PDF_DIR"/*.pdf; do
    # Check if file exists (handles case where no PDFs are found)
    if [ ! -f "$pdf_file" ]; then
        echo -e "${RED}No PDF files found in $PDF_DIR${NC}"
        exit 1
    fi

    counter=$((counter + 1))
    filename=$(basename "$pdf_file")

    echo -e "${GREEN}[$counter/$total_pdfs] Processing: $filename${NC}"
    echo "----------------------------------------"

    # Export PDF_PATH and run the Python script
    PDF_PATH="$pdf_file" python3 pydantic_diversification_analyst_sup.py

    exit_code=$?

    if [ $exit_code -ne 0 ]; then
        echo -e "${RED}Error processing $filename (exit code: $exit_code)${NC}"
    fi

    echo ""
    echo ""
done

echo -e "${BLUE}Finished processing all $total_pdfs PDF files${NC}"
