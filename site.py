from app import app, socketio


@socketio.on('connection')
def handle_message(recv):
    print("Got connection with status: " + str(recv))


@socketio.on('updateAlerts')
def handle(recv):
    print(recv)
    socketio.emit('updateComplete')


if __name__ == "__main__":
    # Using socketio.run instead of app.run because we need to support socketio
    # MAKE SURE TO REMOVE PORT AND DEBUG!
    socketio.run(app, debug=True, host="0.0.0.0", port=8000)
