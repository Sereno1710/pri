# docker run --name pri_solr -d -p 8983:8983 -v "/mnt/c/Users/Diogo Monteiro/Desktop/data:/data" solr
docker run --name pri_solr -d -p 8983:8983 -v "C:\Users\User\OneDrive\Documentos\PRI\pri/data:/data" solr
docker exec pri_solr solr create_core -c covid
docker exec -it pri_solr bash
curl -X POST -H "Content-Type: application/json" --data-binary "@/data/cord-19.json" "http://localhost:8983/solr/covid/update?commit=true" &