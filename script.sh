#python add_embeddings_to_json.py < data/cord-19.json > data/updated_cord-19.json
#python3 add_embeddings_to_json.py < data/cord-19.json > data/updated_cord-19.json

docker run --name pri_solr -d -p 8983:8983 -v "/mnt/c/Users/Diogo Monteiro/Desktop/pri/data:/data" solr
# docker run --name pri_solr -d -p 8983:8983 -v "C:\Users\User\OneDrive\Documentos\PRI\pri/data:/data" solr

#docker run --name pri_solr -d -p 8983:8983 -v "C:\Users\sjose\OneDrive\Documentos\pri2024/data:/data" solr
#docker run --name pri_solr -d -p 8983:8983 -v "C:\Users\João Longras\Desktop\M.IA\PRI\pri/data:/data" solr

sleep(3)
docker exec pri_solr bin/solr delete -c covid

docker cp synonyms.txt pri_solr:/var/solr/data/covid/conf
docker cp stop_words.txt pri_solr:/var/solr/data/covid/conf

docker exec pri_solr solr create_core -c covid

docker exec -it pri_solr bash
curl -X POST -H 'Content-type: application/json' --data-binary "@/data/schema_stemmer.json" "http://localhost:8983/solr/covid/schema" &
curl -X POST -H 'Content-type: application/json' --data-binary "@/data/schema_semantic.json" "http://localhost:8983/solr/covid/schema" &

sleep(3)
curl -X POST -H "Content-Type: application/json" --data-binary "@/data/updated_cord-19.json" "http://localhost:8983/solr/covid/update?commit=true" &
