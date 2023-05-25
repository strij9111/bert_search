import pickle
import sys
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pymysql.cursors
from itertools import groupby
from collections import OrderedDict
from flask import Flask, request, jsonify
import pandas as pd

           
MAX_RECOMMENDED = 3
           
# Создание ресурсов GPU
res = faiss.StandardGpuResources()
                    
model2 = SentenceTransformer('sentence-transformers/LaBSE', device='cuda')
index = faiss.read_index("films_labse_simicolon.faiss")
index = faiss.index_cpu_to_gpu(res, 0, index)

with open('ids.pkl', 'rb') as f:
    ids = pickle.load(f)

types_dict = {'user': int, 'item': str, 'rating': int}
df = pd.read_csv('user-item-rating.csv', dtype=types_dict)
df = df.query('rating >= 7')

app = Flask(__name__)


def getAssets(cursor, similar_ids, similar_distances, source, coef=0.0):
    results = []
    for idx, movie_id in enumerate(similar_ids):
        sql = "SELECT nativeitemid, title, description, genretitles, personnames from datamart WHERE nativeitemid=%s and description<>''"
        cursor.execute(sql, (movie_id))
        result = cursor.fetchall()

        for r in result:
            title = r['title']
            description = r['description']
            r['distance'] = np.float64(similar_distances[idx])+coef
            r['source'] = source
            results.append(r)
            
    return results
    
def getRecommended(cursor, df):
    vectors = []
    
    for item in df['item']:
        sql = "SELECT nativeitemid, title, description, genretitles, personnames from datamart WHERE nativeitemid=%s and description<>''"
        cursor.execute(sql, (item))
        result = cursor.fetchall()

        for r in result:
            description = r['description']
            desc_vector = model2.encode(description)
            vectors.append(desc_vector)

    # Усреднение векторов
    average_vector = np.mean(vectors, axis=0)
    print(average_vector.shape)
    # Поиск наиболее похожих векторов в FAISS
    D, I = index.search(np.array([average_vector]), 5)

    # Получение идентификаторов наиболее похожих элементов
    similar_ids = [ids[i] for i in I[0]]
    similar_distances = D[0]
    
    return getAssets(cursor, similar_ids, similar_distances, 'recommendation', 1.5)


@app.route('/search', methods=['GET'])
def search():
    # Поисковая фраза
    query = request.args.get('query')
    
    # ID пользователя для рекомендации
    user_id = request.args.get('user_id')
    user_exists = False
    if user_id:
        user_exists = df['user'].isin([int(user_id)]).any()

    if not query:
        return jsonify({'error': 'Missing query parameter'})    
        
    connection = pymysql.connect(host='localhost',
                                 port=9306,
                                 user='root',
                                 password='',
                                 database='',
                                 cursorclass=pymysql.cursors.DictCursor)

    # Получаем эмбеддинг от поисковой фразы
    query_vector = model2.encode(query.lower())

    # Поиск наиболее похожих векторов в FAISS
    D, I = index.search(np.array([query_vector]), 5)

    # D - расстояния до наиболее похожих векторов
    # I - индексы наиболее похожих векторов

    # Получение идентификаторов наиболее похожих элементов
    similar_ids = [ids[i] for i in I[0]]
    similar_distances = D[0]

    results = []
    with connection:
        with connection.cursor() as cursor:    
            # BERT - выбираем фильмы, которые лучше всего соответствуют запросу 
            results = getAssets(cursor, similar_ids, similar_distances, 'BERT')
            
            descriptions_rec = []
            # Если указан user_id - используем рекомендации
            if user_exists:
                user_ratings = df[df['user'] == int(user_id)]
                top_ratings = user_ratings.nlargest(MAX_RECOMMENDED, 'rating')
                descriptions_rec.extend(getRecommended(cursor, top_ratings))
                    
            results.extend(descriptions_rec)

            # Ранкер Manticore - выбираем фильмы, которые лучше всего соответствуют запросу 
            sql = f"""
            SELECT nativeitemid, title, description, genretitles, personnames, weight() as weight 
            FROM datamart 
            WHERE description<>'' and genretitles<>'' and MATCH('@(title) "{query}"/0.25') AND type IN ('MOVIE','SERIAL') LIMIT 5
            OPTION ranker=expr('sum((4*lcs+3*(min_hit_pos<3)+exact_hit*(min_gaps==0)*exact_order*3)*user_weight)+bm25'), field_weights=(description=10,title=100)
            """            
            cursor.execute(sql)
            result = cursor.fetchall()

            for r in result:
                r['distance'] = (r['weight']/1000)
                r['source'] = 'Manticore'
                results.append(r)
                

    sorted_data = sorted(results, key=lambda x: x['title'])
    grouped_data = groupby(sorted_data, key=lambda x: x['title'])

    # Создаем OrderedDict для сохранения уникальных элементов
    unique_data = OrderedDict((key, next(group)) for key, group in grouped_data)
    unique_data = list(unique_data.values())
    unique_data = sorted(unique_data, key=lambda x: x['distance'])
                   
    return jsonify(unique_data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8090)
