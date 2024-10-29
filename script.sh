docker run --name my_solr -d -p 8983:8983 solr:9 
docker exec pri_solr solr create_core -c ptnews