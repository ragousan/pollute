#coding: utf-8
from flask import Flask, render_template
from os import path
import time


app = Flask(__name__)

@app.route("/")
def index():
   return render_template("pollution_oz.html")

if __name__ == '__main__':
   
   time_to_wait = 10
   time_counter = 0
   while not path.exists("./templates/pollution_oz.html"):
      time.sleep(1)
      time_counter += 1
      print("Waiting for html map")
      if time_counter > time_to_wait:break

   app.run(debug = True, host='0.0.0.0')
