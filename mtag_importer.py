#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set noet:ts=4:ai

#sshfs meta@10.10.10.100:meta-storage /mnt/syno1/

DATASTORE_TMP = '/home/meta/naspi/metameta/meta/datastore_tmp/'

from termcolor import colored 
from os import path
from shutil import move as movefile
from translation_system import transform, Repr, pWarn, pError, pInfo, pEngine, pSQL, pTODO, pVerbose
from pathlib import Path

FETCHLIMIT=300		# SQL fetch limit
DEFAULT_PRINT_SQL = True
DEFAULT_PRIORITY = 64
DEFAULT_TS_OUT = 0

# system
from sys import stderr
from time import time

# database backend
#import sqlite3 as sql
from db import get_engine, save_entry, get_entry, get_entries

from runes import *
from engine import Engine, dec, enc
from dictionnary import Word, Dictionnary, Item, Say
D = Dictionnary()
ITEM_LABEL = D.read(b'_label')

async def main(dbdb, dbuser, dbpwd, datapath):
	global D, E
	E = await Engine.startEngine( dbdb = dbdb, user = dbuser, pwd = dbpwd )
	T = E, D

	dbpath = datapath+'/data.sqlite3'
	binpath = datapath+'/pictures/'

	db = get_engine(dbpath)
	entries = get_entries(db)

	for index in entries:
		uuid = index['id']
		p = Path(binpath,uuid+'.jpeg')
		if p.exists():
			print('>>>>', colored(uuid,'green'))
			move( p, DATASTORE_TMP )
		else:
			print('>>>>', colored(uuid,'red'))
		entry = get_entry(db, uuid)
		date = entry['updated']
		keyWord = D.read(enc(entry['text_fields'][0]['key']))
		valueWord = D.read(enc(entry['text_fields'][0]['value']))
		print(f"\t{keyWord}\t{valueWord}")
		await Say.now( Ansuz, D.read(uuid), keyWord, valueWord, True, T=T )
	
	return E

if __name__ == '__main__':
	from credentials import *
	import settings
	from sys import argv
	import asyncio

	engine = asyncio.run(main( dbdb, dbuser, dbpwd, argv[1] ))
	#engine = asyncio.run(quotesFromLegacyFile( dbdb, dbuser, dbpwd ))

	asyncio.run(engine.shutDown())

