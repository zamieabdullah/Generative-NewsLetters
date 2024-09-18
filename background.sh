#!/bin/bash
echo "Running Bash script!"

# Example loop calling a URL 10 times
for i in {1..10}; do
  response=$(curl -s -o /dev/null -w "%{http_code}" https://your-flask-app-url/run-daily-task)

  if [ "$response" -eq 200 ]; then
    echo "Request $i: Success"
  else
    echo "Request $i: Failed with status code $response"
  fi
done