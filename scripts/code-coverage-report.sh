#!/bin/bash
# This script has 3 main functions:
#  - generate a code coverage report in different formats (html, json, xml)
#  - check if the code coverage threshold for the repository is meet
#  - check if the code coverage threshold for critical files is meet

echo "Running coverage report..."
coverage report
cc_resport_status=$?

echo ""
echo "Generating coverage reports in different formats (html, json, xml)...)"
# html report will be stored as build artifact when build fails
coverage html
# coverage json will be used by coverage-threshold
coverage json
# coverage xml will be used by orgoro/coverage github action
coverage xml

echo "Running coverage threshold checks for critical files..."
coverage-threshold --config=.coverage_threshold
ct_resport_status=$?

echo ""
# Check if coverage checks passed
if [ $cc_resport_status -eq 0 ] && [ $ct_resport_status -eq 0 ]; then
    echo "Coverage checks passed."
else
    echo "Coverage checks failed, please check the logs above and reports for more details."
    exit 1
fi
