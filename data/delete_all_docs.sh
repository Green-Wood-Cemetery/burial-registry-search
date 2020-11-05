## delete all documents
curl -X "POST" "https://greenwood-kstyate-arc.searchbase.io/interments/_delete_by_query?pretty&conflicts=proceed" \
     -H 'Content-Type: application/json' \
     -u 'user:auth_key' \
     -d $'{
  "query": {
    "match_all": {}
  }
}'