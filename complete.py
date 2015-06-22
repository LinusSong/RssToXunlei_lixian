#-*-coding:utf-8 -*-
import update
import yaml
import sqlite3
import os

def removeNone(a):
    try:
        while True:
            a.remove(None)
    except:
        pass
    return a

def main():
    task = open('lixiantask.sh','w')
    task.write('#!/bin/sh'+'\n')
    config = yaml.load(open('config.yml').read())
    username = config['global']['username']
    password = config['global']['password']
    dldir = config['global']['dldir']
    HttpProxy = config['global']['HttpProxy']
    tasks = config['tasks']
    conn = sqlite3.connect('bangumi.db')
    cell = conn.cursor()
    try:
        cell.execute("SELECT * FROM Updated;")
    except:
        cell.execute('''CREATE TABLE Updated
        (weekday TEXT,series TEXT,title TEXT,episode INTEGER,
        PubDate TEXT,team TEXT,infohash TEXT);''')
    for item in tasks.keys():
        update.mkdir(dldir,item)
        weekday = item[:3]
        series = item[4:]
        team = tasks[item].keys()[0]
        itemlist = update.CatchFeedinfo(item, tasks[item].values()[0], HttpProxy)
        for epi in itemlist:
            title, PubDate, infohash, mailadded = epi
            episode = update.Cal_episode(title)
            cell.execute('''SELECT * from Updated 
                            WHERE title = ? AND infohash = ?;''',(title,infohash))
            if cell.fetchone() == None:
                entry = (weekday,series,title,episode,PubDate,team,infohash)
                cell.execute('INSERT INTO Updated VALUES (?,?,?,?,?,?,?)',entry)
                conn.commit()

        episodeNums = []
        for root,dirs,files in os.walk(os.path.join(dldir,item)):
            for name in files:
                episodeNums.append(int(update.Cal_episode(name)))
        episodeNums = removeNone(episodeNums)
        cell.execute('SELECT title, PubDate, infohash, episode FROM Updated WHERE series = (?);',(series,))
        a = cell.fetchall()
        for i in a:
            title, PubDate, infohash, episode = i
            if not episode in episodeNums:
                task.write(update.Task(item, title, PubDate, infohash, dldir))
    conn.close()

if __name__ == '__main__':
    main()