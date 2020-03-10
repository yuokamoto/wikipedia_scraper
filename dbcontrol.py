#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import mojimoji, re
def pre_process(data):
    data = data.lower()
    data = data.replace(' ', u'_')
    data = data.replace('-', u'ー')
    data = data.replace(".", u"．")
    data = data.replace(",", u"，")
    data = data.replace("\'", u"’")
    data = data.replace("&", u"＆")
    data = data.replace("/", u"／")
    data = data.replace("(", u"（")
    data = data.replace(")", u"）")
    data = data.replace("[", u"［")
    data = data.replace("]", u"］")
    data = data.replace(":", u"：")
    data = data.replace("!", u"！")
    data = data.replace("?", u"？")
    return data

def key_pre_process(data):
    orig = data
    data = pre_process(data)
    if len(data)>1 and re.match('[0-9]', data[0]):
        d = mojimoji.han_to_zen(data[0].decode('utf-8'))
        data = d+data[1:]

    data = data.encode('utf-8')
#
#     if orig != data:
#         print orig, data
    return data

def value_pre_process(data):
    data = pre_process(data)
    data = data.encode('utf-8')
    return data

def get_list_from_list_of_touple(list_data):
    return [x[0] for x in list_data]

def get_decode_list(list_data):
    return [x.decode('utf-8') for x in list_data]

class DBControl(object):
    def __init__(self, dbname, user, password, host='localhost'):
        self._conn = psycopg2.connect(dbname=dbname, host=host, user=user, password=password)
        self._cur = self._conn.cursor()
        
    def __del__(self):
        self._cur.close()
        self._conn.close()

    def execute_commit(self, cur_input):
        self._cur.execute(cur_input)
        self._conn.commit()

    def execute_fetchall(self, cur_input):
        self._cur.execute(cur_input)
        return self._cur.fetchall()
        
    def get_columns_name(self, table):
        cur_input = 'SELECT information_schema.columns.column_name FROM information_schema.columns WHERE table_name=\''+table+'\';'
        return self.execute_fetchall(cur_input)

    def get_table_name(self):
        cur_input = """SELECT table_name FROM information_schema.tables
               WHERE table_schema = 'public'"""
        return self.execute_fetchall(cur_input)

    def create_table(self, table):
        cur_input = 'CREATE TABLE IF NOT EXISTS ' + table + ' (name text PRIMARY KEY);'
        self.execute_commit(cur_input)

    def insert(self, table, column, value):
        if self.get_value(table, column, value) != []:
            print value + ' is exist already'
            return
        
        cur_input = 'INSERT INTO ' + table + ' (' + column + ") VALUES (\'" + value + "\');"
        self.execute_commit(cur_input)
        print value + ' was inserted'

    def update(self, table, column, value, name):
        cur_input = 'UPDATE ' + table + ' set ' + column + '=' + "\'" + value + "\' WHERE name=\'" + name + "\'"
        self.execute_commit(cur_input)

    def alter(self, table, column, data_type):
        cur_input = 'ALTER TABLE '+table+' ADD '+column+' '+data_type+';'
        self.execute_commit(cur_input)
    
    def get_value(self, table, key, value, column='*'):
        cur_input = 'SELECT '+column+' FROM ' + table + ' WHERE ' + key + "=\'" + value + "\';"
        return self.execute_fetchall(cur_input)
