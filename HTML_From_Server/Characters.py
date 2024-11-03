from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('character-get.html')



@app.route('/result', methods=['GET'])
def result():
    SeriesID = request.args.get('SeriesID')
    Title = request.args.get('Title')
    VolumeNumber = request.args.get('VolumeNumber')
    StartYear = request.args.get('StartYear')

    return render_template('ComicSeriesDynamic.html', SeriesID=SeriesID, Title=Title, VolumeNumber=VolumeNumber, StartYear=StartYear)

if __name__ == '__main__':
    app.run(port=8000, debug=True, host="0.0.0.0")