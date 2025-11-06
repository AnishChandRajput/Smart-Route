from flask import Flask, render_template, redirect, url_for
import subprocess
import os

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/run/<algo>')
def run_algo(algo):
    # Make sure Python path is correct
    python_path = "python"  # or "python3"

    if algo == 'astar':
        subprocess.Popen([python_path, 'city_sim.py'])
    elif algo == 'blind':
        subprocess.Popen([python_path, 'blind_search.py'])
    elif algo == 'dfs':
        subprocess.Popen([python_path, 'dfs_maze_simulation.py'])

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
