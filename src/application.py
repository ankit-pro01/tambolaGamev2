
from flask import Flask

from flask import render_template, jsonify, request

from flask_socketio import SocketIO, send, emit, join_room, leave_room

from time import localtime, strftime
import random

import numpy as np

import os

app = Flask(__name__, static_url_path='', static_folder="build", template_folder="build")

socketIo = SocketIO(app, cors_allowed_origins="*")
        

ROOMS = []

KING = {}

# GAME_DATA = {}

NAMES = []

check_list = []

check_list_with_room = {}

total_players_list = {}

host_list = [i for i in range(0,100)]


class Host():

    def __init__(self):
            pass
    def getList(self):
        return [i for i in range(0,100)]

        

@socketIo.on('connect')
def test_connect():
    print('connected')


@socketIo.on('king')
def king(data):
    king = data['king']
    emit('king', {"king" : king})


@socketIo.on('total_players')
def total_players(data):
    room = data['room']
    players = data['total_players']

    print("inside the total players function:", players)

    print("players function:", players)

    send({'msg' : "", 'name' : name, 'player_list' : players}, room = data['room'])




@socketIo.on('join')
def on_join(data):
    print("inside room")
    print(data)
    room = data['room']
    name = data['name']


    print("joining room is : ", room)
    
    if room in ROOMS:
        if name not in NAMES:
            total_players_list[room].append(name)
            join_room(room)
            emit('join', { 'msg' : data['name'] + " has joined the room ", 'error' : '','room': room, 'total_players': total_players_list[room], 'king': KING[room]}, room = data['room'])
        else:
            emit('join', { 'error' : 'please select different username'},)
    else:
        emit('join', { 'error' : room + ' room is not there, please create '},)



@socketIo.on('leave')
def on_leave(data):
    print("inside leave  room")
    print(data)
    room = data['room']
    name = data['name']
    leave_room(room)

    print("total numbers before leave: ", total_players_list[room])
    (total_players_list[room]).remove(name)
    z = total_players_list[room]
    print("total numbers after leave: ", total_players_list[room])

    emit('total_players', {'room': room, 'total_players' : z})
    return None



@socketIo.on('newRoom')
def on_newRoom(data):
    print("inside new room creation")
    print(data)
    room = data['room']
    name = data['name']
    
    all_names = []
    all_names.append(name)
    total_players_list[room] = all_names

    ROOMS.append(room)

    check_list_with_room[room] = []

    KING[room] = data['name']

    print(KING)

    join_room(room)

    # if name == KING[room]:
    #     king_flag = True
    # else:
    #     king_flag = False

    # print(king_flag)

    emit('join', { 'msg' : data['name'] + " has joined the room ", 'error' : '', 'room': room, 'king': KING[room]}, room = data['room'])




@socketIo.on('claim')
def on_claim(data):
    check = False
    List2 = data['number_list']
    print("list is ",List2)
    room = data['room']
    name = data['claimer']
    print("check list is : ", check_list_with_room[room])

        
    if len(check_list_with_room[room]) >= 18:
        if len(List2) != 0:
            print("checking....for the claim....")
            check =  all(item in check_list_with_room[room] for item in List2)
            print("check list is : ",check_list_with_room[room])
            print("chit is : ", List2)
            print("room name is " + room)
    
    if check:
        print("yes")
        emit('claim', { 'msg' : "YES", 'claimer' : name}, room = room)
    else:
        print("Warning")
        emit('claim', { 'msg' : "NO", 'claimer' : name}, room = room)



def get_arr():
    return random.sample(range(1, 100), 18)



@socketIo.on("message")
def handleMessage(data):
    print("inside message")
    print(data)
    room = data['room']
    print("inside message:  total players : ", total_players_list[room])
    send({'msg' : data['msg'], 'username': data['name'], 'time_stamp': strftime("%b-%d %I:%M%p", localtime()), 'player_list' : total_players_list[room]}, room = data['room'])
    return None

@socketIo.on("chits")
def distribute_chits():
    chit = get_arr()
    print(chit)
    emit('chits',{'chit' : chit})
    return None
    

@socketIo.on("start")
def handleStart(data):
    print("starting..")
    room = data['room']
    global host_list
    print(data)
    if  host_list == []:
        print("host_list is empty....")
        host_list =  [i for i in range(0,100)]

    # host = Host()
    # list1 = host.getList()
    random.shuffle(host_list)
    check_list_with_room[room].append(host_list[-1])
    
    emit('start',{'username': 'host', 'msg' :host_list.pop()}, room = data['room'])


@socketIo.on("playAgain")
def playAgain(data):
    room = data['room']
    print("playing again...")
    (check_list_with_room[room])[:] = []
    emit("playAgain", {'msg': "playAgain"})
    


#for the static....................................
@app.route('/')
def hello():
    return app.send_static_file('index.html')



@app.errorhandler(404)
def not_found(error = None):
    message = {
        'status': 404,
        'message': 'Not Found' + request.url
    }

    resp = jsonify(message)
    resp.status_code = 404
    return resp 


if __name__ == '__main__':
    #for development
    # socketIo.run(app, host='0.0.0.0', debug=True)
    app.run() #for static and production
