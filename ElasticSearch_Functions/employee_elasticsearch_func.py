from elasticsearch import Elasticsearch, helpers
import csv

es = Elasticsearch(["http://localhost:8989"])

def createCollection(p_collection_name):
    if not es.indices.exists(index=p_collection_name):
        es.indices.create(index=p_collection_name)
        print(f"Collection '{p_collection_name}' created.")
    else:
        print(f"Collection '{p_collection_name}' already exists.")

def indexData(p_collection_name, p_exclude_column):
    with open('employee_data.csv', mode='r') as file:
        reader = csv.DictReader(file)
        actions = []
        
        for row in reader:
            row.pop(p_exclude_column, None)
            actions.append({
                "_index": p_collection_name,
                "_source": row
            })
        
        helpers.bulk(es, actions)
        print(f"Data indexed into '{p_collection_name}' excluding column '{p_exclude_column}'.")

def searchByColumn(p_collection_name, p_column_name, p_column_value):
    query = {
        "query": {
            "match": {
                p_column_name: p_column_value
            }
        }
    }
    results = es.search(index=p_collection_name, body=query)
    print(f"Search results for {p_column_name}='{p_column_value}':")
    for hit in results['hits']['hits']:
        print(hit['_source'])

def getEmpCount(p_collection_name):
    count = es.count(index=p_collection_name)['count']
    print(f"Total employee count in '{p_collection_name}': {count}")

def delEmpById(p_collection_name, p_employee_id):
    query = {
        "query": {
            "match": {
                "employee_id": p_employee_id
            }
        }
    }
    es.delete_by_query(index=p_collection_name, body=query)
    print(f"Employee with ID '{p_employee_id}' deleted from '{p_collection_name}'.")

def getDepFacet(p_collection_name):
    query = {
        "size": 0,
        "aggs": {
            "department_counts": {
                "terms": {
                    "field": "department.keyword"
                }
            }
        }
    }
    results = es.search(index=p_collection_name, body=query)
    print("Employee count by department:")
    for bucket in results['aggregations']['department_counts']['buckets']:
        print(f"Department: {bucket['key']}, Count: {bucket['doc_count']}")

v_nameCollection = 'Hash_JohnDoe'
v_phoneCollection = 'Hash_1234'

createCollection(v_nameCollection)
createCollection(v_phoneCollection)

getEmpCount(v_nameCollection)

indexData(v_nameCollection, 'Department')
indexData(v_phoneCollection, 'Gender')

getEmpCount(v_nameCollection)

delEmpById(v_nameCollection, 'E02003')

getEmpCount(v_nameCollection)

searchByColumn(v_nameCollection, 'Department', 'IT')
searchByColumn(v_nameCollection, 'Gender', 'Male')
searchByColumn(v_phoneCollection, 'Department', 'IT')

getDepFacet(v_nameCollection)
getDepFacet(v_phoneCollection)
