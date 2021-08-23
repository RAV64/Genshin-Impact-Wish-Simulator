from flask import Flask, render_template, redirect, url_for, session, request
from datetime import datetime, timedelta
from main import Wisher
import os
import logging

app = Flask(__name__)

app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

app.secret_key = "wishsim"
app.permanent_session_lifetime = timedelta(days=100)

wish = Wisher()

files = os.listdir("static/images/banners/character")
files.sort(key=lambda date: datetime.strptime(date.split(" ")[1].split(".")[0], '%Y-%m-%d'))
files.reverse()


@app.route('/')
def to_main():
    if "banner" in session:
        return redirect(url_for("main_page", banner=session["banner"]))
    else:
        return redirect(url_for("main_page", banner="Adrift_in_the_Harbor 2021-01-12.png"))


@app.route('/pull=<num>')
def puller(num):
    num = int(num)
    pulls = wish.pull(num)

    if "times_pulled" in session:
        session["times_pulled"] += num
    else:
        session["times_pulled"] = 0

    return render_template("index.html",
                           banner_list=files,
                           active_banner=session["banner"],
                           mainvis="hidden",
                           pullscreenvis="visible",
                           pulls=list(pulls)
                           )


@app.route('/<banner>/', methods=["POST", "GET"])
def main_page(banner):
    wish.currentbanner = banner.replace(" ", "/").split(".")[0]
    session.permanent = True
    session["banner"] = banner
    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    print(request.environ['REMOTE_ADDR'])
    return render_template("index.html",
                           banner_list=files,
                           active_banner=banner,
                           mainvis="visible",
                           pullscreenvis="hidden"
                           )


@app.route('/reset')
def reset():
    print("Reset!")
    session.pop("times_pulled", None)

    wish.fiftyfifty = {"weap4ff": False, "weap5ff": False,
                       "char4ff": False, "char5ff": False}

    return render_template("index.html",
                           banner_list=files,
                           active_banner=session["banner"],
                           mainvis="visible",
                           pullscreenvis="hidden"
                           )


if __name__ == '__main__':
    app.run()
