from stream import data_elastic
from stream import loaddata
from utils import dateutils, hashutils, numutils
import pandas as pd
import json

def TaskHistorico(_dados, _json, _intervalo, _index, _historico_em_dias, _amplitude, acumulativo):
        _key_model         = hashutils.key_model(_json)
        _key_entity        = hashutils.gerarHash(json.dumps(_json))
        print("Loading old data - " + str(_json) + " - " + str(_historico_em_dias))

        sum_valores = 0

        if(_historico_em_dias>0):

            freqCalc = str(_intervalo) + 'S'

            db = data_elastic.ManagerElastic()

            envios = ''
            count = 1
            end_date = dateutils.dateutils().dataAtual()
            end_date = dateutils.dateutils().addMinutes(end_date, -1)

            for new_date in pd.date_range(end=end_date, periods=(_historico_em_dias*24*60), freq=freqCalc):
                valor = loaddata.getValor(_dados, new_date)
                valor = valor + numutils.calcRandom(_amplitude, 15)
                sum_valores += valor

                dict_envio = {**_json, "time": new_date.strftime("%Y-%m-%dT%H:%M:%SZ"), "value": valor}

                if acumulativo:
                    dict_envio['value'] = sum_valores

                envios += '{ "index" : { "_index" : "' + _index + '" } }\n'
                envios += json.dumps(dict_envio) + '\n'

                if count > 300:
                    print("Envio do historico -> " + new_date.strftime("%Y-%m-%d"))
                    db.sendBulkElastic(envios)
                    envios = ''
                    count = 0

                count += 1

            db.sendBulkElastic(envios)

            print('Fim do processo de geracao do historico...')

        return sum_valores