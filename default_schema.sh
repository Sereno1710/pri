docker run --name pri_solr -d -p 8983:8983 -v"$(pwd)":/data solr

sleep 3

docker exec pri_solr solr create_core -c covid

docker exec -it pri_solr bash
curl -X POST -H 'Content-type: application/json' --data-binary "@/data/schema_default.json" "http://localhost:8983/solr/covid/schema" &

sleep 3

curl -X POST -H "Content-Type: application/json" --data-binary "@/data/cord-19.json" "http://localhost:8983/solr/covid/update?commit=true" &