import pytrec_eval

# Carregar os arquivos de relevância (qrels) e resultados
with open('qrels_trec.txt', 'r') as f_qrel:
    qrel_data = f_qrel.readlines()
qrels = pytrec_eval.parse_qrel(qrel_data)

with open('results_sys1_trec.txt', 'r') as f_run:
    run_data = f_run.readlines()

results = pytrec_eval.parse_run(run_data)

print(results)

# Criar o avaliador
evaluator = pytrec_eval.RelevanceEvaluator(qrels, measures=["map", "ndcg","recip_rank"])

# Avaliar os resultados
scores = evaluator.evaluate(results)

# Imprimir as métricas de avaliação
for query_id, query_scores in scores.items():
    print(f"Query ID: {query_id}")
    for metric, score in query_scores.items():
        print(f"{metric}: {score}")
