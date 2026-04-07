#this script is used to restore the response_database.py file to a minimal baseline version,
#in order to demonstrate the chatbot's ability to learn and promote mature word usage
Copy-Item -LiteralPath ".\learning_resource\response_database_minimal.py" -Destination ".\learning_resource\response_database.py" -Force
Write-Host "Restored learning_resource/response_database.py from the minimal baseline."
