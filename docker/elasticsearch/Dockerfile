FROM elasticsearch:8.19.10

# IK 中文分词器，版本必须与 Elasticsearch 版本完全一致
RUN bin/elasticsearch-plugin install --batch \
    https://get.infini.cloud/elasticsearch/analysis-ik/8.19.10
