from ._benchmark import _benchmark

from flask import request, jsonify, Flask, render_template
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)

#app.config['SECRET_KEY'] = 'secret!' #Obviously, for testing only
socketio = SocketIO(app)

@app.route("/")
def home():
    return render_template("./home.html")


@app.route("/compare")
def compare():
    params = (
        "target_fork",
        "target_commit",
        "base_commit",
        "benchmarks",
        "pgo",
        "tier2",
        "jit",
    )
    vars = {}
    for p in params:
        vars[p] = request.args.get(p, None)

    if vars["base_commit"]:
        return _benchmark(
            vars["base_commit"],
            benchmarks=vars["benchmarks"],
            pgo=vars["pgo"],
            tier2=vars["tier2"],
            jit=vars["jit"],
        )
    else:
        return jsonify({"Result": "No commits specified"})


@app.route("/benchmark")
def benchmark():
    params = ("commit", "benchmarks", "pgo", "tier2", "jit")
    vars = {}
    for p in params:
        vars[p] = request.args.get(p, None)

    result = _benchmark(
        commit=request.args["commit"],
        benchmarks=vars["benchmarks"],
        pgo=vars["pgo"],
        tier2=vars["tier2"],
        jit=vars["jit"],
    )

    return result

@app.route("/wstest")
def wstest():
     return render_template("wstest.html")

@socketio.on('my event')
def handle_message(data):
    print(f"Received message: {data}")
    emit('resp', f'Thanks for sending me {data}')