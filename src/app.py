from ._benchmark import _benchmark

from flask import request, jsonify, Flask, render_template

app = Flask(__name__)


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
