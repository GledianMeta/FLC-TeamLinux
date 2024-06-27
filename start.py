from flask import Flask

PORT=8080
HOST="127.0.0.1"


@app.route('/hc')
def health_check():
    return "I'm alive"



app= Flask(__name__)
if __name__=="__main__":
    app.run(HOST,PORT,true)