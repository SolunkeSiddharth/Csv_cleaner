from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CLEAN_FOLDER = "cleaned"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEAN_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        file = request.files["file"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        df = pd.read_csv(filepath, na_values=["", " ", "NA", "null", "?"])

        df.replace(r'^\s*$', pd.NA, regex=True, inplace=True)

        missing_counts = df.isna().sum()
        columns = missing_counts[missing_counts > 0].index.tolist()

        missing_counts = missing_counts.to_dict()


        return render_template(
            "index.html",
            columns=columns,
            filename=file.filename,
            missing_counts=missing_counts
        )

    return render_template("index.html")


@app.route("/clean", methods=["POST"])
def clean():

    filename = request.form["filename"]
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    df = pd.read_csv(filepath, na_values=["", " ", "NA", "null", "?"])
    df.replace(r'^\s*$', pd.NA, regex=True, inplace=True)

    for column in list(df.columns):

        method = request.form.get(column)

        # Drop column
        if method == "drop":
            df.drop(column, axis=1, inplace=True)
            continue

        # Mean
        if method == "mean":
            if pd.api.types.is_numeric_dtype(df[column]):
                df[column] = df[column].fillna(df[column].mean())

        # Median
        elif method == "median":
            if pd.api.types.is_numeric_dtype(df[column]):
                df[column] = df[column].fillna(df[column].median())

        # Mode
        elif method == "mode":
            if not df[column].mode().empty:
                df[column] = df[column].fillna(df[column].mode()[0])

    cleaned_file = os.path.join(CLEAN_FOLDER, "cleaned_" + filename)

    df.to_csv(cleaned_file, index=False)

    return send_file(cleaned_file, as_attachment=True)


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)