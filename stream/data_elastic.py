from elasticsearch import Elasticsearch
from utils import httputils
import http.client
import os

'''
    Exemplo de envio
    {
        "measurement": "brushEvents",
        "tags": {
            "user": "Carol",
            "brushId": "6c89f539-71c6-490d-a28d-6c5d84c0ee2f"
        },
        "time": "2018-03-28T8:01:00Z",
        "fields": {
            "duration": 127
        }
    }
'''

url = os.environ.get('URL_ELK', 'localhost:9200')  # export URL_ELK=localhost:9200
user = os.environ.get('USER_ELK')  # export USER_ELK=None
senha = os.environ.get('PWD_ELK')

class ManagerInfluxDB():

    def __init__(self):
        self.es = None
        if(self.user and self.senha):
            self.es = Elasticsearch(['https://'+ self.url], http_auth=(self.user, self.senha))
        else:
            self.es = Elasticsearch(['http://' + self.url])

    def sendData(self, index, envio):
        try:
            self._client.write_points(envio, database='data-test', time_precision="m")
            res = self.es.index(index=index, body=envio)
        except Exception as e:
            if "database not found" in str(e):
                self._client.create_database('data-test')

    def sendBulkElastic(self, envio):
        params = envio
        headers = httputils.setHeaders("application/x-ndjson")

        conn = None
        if (self.user and self.senha):
            conn = http.client.HTTPSConnection(self.url)
        else:
            conn = http.client.HTTPConnection(self.url)

        conn.request("POST", "/_bulk", params, headers)

        response = conn.getresponse()

        print('Status do Elasticsearch -> ' + str(response.status) + ' - ' + response.reason)

        conn.close()