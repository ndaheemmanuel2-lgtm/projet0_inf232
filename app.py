from flask import Flask, render_template, request, redirect
import statistics
import numpy as np

app = Flask(__name__)

data = []

# ------------------ ROUTES ------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/submit', methods=['POST'])
def submit():
    student = {
        "nom": request.form['nom'],
        "age": int(request.form['age']),
        "heures": float(request.form['heures']),
        "internet": float(request.form['internet']),
        "social": float(request.form['social']),
        "environnement": float(request.form['environnement']),
        "moyenne": float(request.form['moyenne'])
    }

    data.append(student)
    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', data=data)


# ------------------ ANALYSE STATISTIQUE ------------------

@app.route('/analysis')
def analysis():

    if len(data) < 2:
        return render_template('analysis.html', result=None)

    # --------- EXTRACTION DES DONNÉES ----------
    moyennes = np.array([d["moyenne"] for d in data])

    # --------- STATISTIQUES ----------
    moyenne = np.mean(moyennes)
    variance = np.var(moyennes)
    ecart_type = np.std(moyennes)

    # --------- QUANTILES ----------
    q1 = np.percentile(moyennes, 25)
    q2 = np.percentile(moyennes, 50)
    q3 = np.percentile(moyennes, 75)
    iqr = q3 - q1

    # --------- Z-SCORE ----------
    z_scores_list = []

    for val in moyennes:
        z = (val - moyenne) / ecart_type if ecart_type != 0 else 0

        # interprétation
        if z > 1:
            interpretation = "Au-dessus de la moyenne"
        elif z < -1:
            interpretation = "En dessous de la moyenne"
        else:
            interpretation = "Dans la moyenne"

        z_scores_list.append({
            "valeur": round(val,2),
            "z": round(z,2),
            "interpretation": interpretation
        })

    # --------- CORRÉLATIONS ----------
    heures = np.array([d["heures"] for d in data])
    internet = np.array([d["internet"] for d in data])

    corr_heures = np.corrcoef(heures, moyennes)[0,1]
    corr_internet = np.corrcoef(internet, moyennes)[0,1]

    def interpretation_corr(c):
        if c > 0.5:
            return "Forte relation positive"
        elif c > 0:
            return "Relation faible"
        elif c < -0.5:
            return "Forte relation négative"
        else:
            return "Pas de lien clair"

    # --------- RESULT FINAL ----------
    result = {
        "moyenne": round(moyenne,2),
        "variance": round(variance,2),
        "ecart_type": round(ecart_type,2),

        "q1": round(q1,2),
        "q2": round(q2,2),
        "q3": round(q3,2),
        "iqr": round(iqr,2),

        "z_score": "Analyse détaillée ci-dessous",
        "z_scores": z_scores_list,

        "corr_heures": round(corr_heures,2),
        "corr_internet": round(corr_internet,2),
        "int_heures": interpretation_corr(corr_heures),
        "int_internet": interpretation_corr(corr_internet)
    }

    return render_template('analysis.html', result=result)


# ------------------ LANCEMENT ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
