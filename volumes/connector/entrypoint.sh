
echo -e "\n\n=============\nWaiting for Kafka Connect to start listening on connector ⏳\n=============\n"
while [ $(curl -s -o /dev/null -w %{http_code} http://connector:8083/connectors) -ne 200 ] ; do
  echo -e "\t" $(date) " Kafka Connect listener HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://connector:8083/connectors) " (waiting for 200)"
  sleep 5
done
echo -e $(date) "\n\n--------------\n\o/ Kafka Connect is ready! Listener HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://connector:8083/connectors) "\n--------------\n"

# Now create your connector
## Inline config example: 
curl -X DELETE -H "Content-Type: application/json" -d @- http://connector:8083/connectors/db-connector
eval "cat <<EOF
$(cat config.json)
EOF" | curl -X POST -H "Content-Type: application/json" -d @- http://connector:8083/connectors