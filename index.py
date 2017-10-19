from flask import Flask, render_template, url_for, request, redirect, session
import data
import searching
import users
import bcrypt
from functools import wraps
from datetime import datetime

app = Flask(__name__)
# How should I secure that key?
app.secret_key = 'abc'

@app.route("/")
@app.route("/page/<num>")
def index(num=1):
  last_index = data.get_number() - 1
  fresh_offers = []

  # Page number
  num = int(num)
  i = (num * 10) - 10

  for x in range(i, i+10):
    try:
      if (last_index-x) >= 0:
        fresh_offers.append( data.read_offer(last_index-x) )
    except:
      print "reading error"

  # Page number has to be incremented, because the button "next page" needs this
  # number.
  num +=1
  return render_template('index.html', fresh_offers = fresh_offers, num = num)

# Doesn't work.
def check_if_logged_in(f):
  status = session.get('logged_in', False)
  if status == True:
    return "ok"
  else:
    return "notok"

# Works but I don't get it.
# 1. Why does it have such recursive structure. 
# 2. What about the arguments.
# 3. What the wraps means?
# ---
# Should I add here redirection to the requested page after login?
# Why the first version doesn't work?
def check_if_logged(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    status = session.get('logged_in', False)
    if status == True:
      return f(*args, **kwargs)
    else:
      return redirect('/login')
  return decorated

@app.route("/sell", methods=['POST', 'GET'])
@check_if_logged
def sell():
  if request.method == 'POST':
    id = "AXN000"+str(data.get_number()+1)
    title = request.form['title']
    desc = request.form['desc']
    startDate = datetime.now().strftime("%d.%m.%Y %H:%M")
    endDate = request.form['endDate']
    startPrice = request.form['startPrice']
    endPrice = request.form['endPrice']
    seller = "Sylvester Omsky"
    photo = request.files['photo']
    photo.save('static/uploads/'+id+'.png')  
    offer = {'id': id, 'title': title, 'desc': desc, 'startDate': startDate,
    'endDate': endDate, 'startPrice':startPrice, 'endPrice':endPrice,
    'seller':seller}
    data.add_offer( offer )
    return "Done"
  else:
    return render_template('sell.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
  if request.method == 'POST':
    login = request.form['login']
    password = request.form['password']
    result = users.check_credentials( login, password )
    if result == 'true':
      session['logged_in'] = True
      return redirect('/')
    else:
      return render_template('login.html')
  else:
    return render_template('login.html')

@app.route("/register", methods=['POST', 'GET'])
def register():
  if request.method == 'POST':
    login = request.form['login']
    password = request.form['password']
    email = request.form['email']
    fname = request.form['fname']
    sname = request.form['sname']
    phone = request.form['phone']
    address = request.form['address']
    town = request.form['town']
    code = request.form['code']
    country = request.form['country']
    user = {'address': address, 'code': code, 'country': country, 'email':
    email, 'fname': fname, 'login': login, 'password': password, 'phone':
    phone, 'sname': sname, 'town': town}
    users.add_user( user )
    return "Done"
  else:
    return render_template('register.html')

@app.route("/account", methods=['POST', 'GET'])
@check_if_logged
def account():
  if request.method == 'POST':
    return "Ok"
  else:
    user = users.read_user( 0 )
    return render_template('account.html', user=user)

@app.route("/search", methods=['POST', 'GET'])
def search():
  if request.method == 'POST':
    phrase = request.form['phrase']
    price_min = request.form['price_min']
    price_max = request.form['price_max']
    results_numbers = searching.search_for( phrase, price_min, price_max )
    results = []

    for x in results_numbers:
      try:
        results.append( data.read_offer( x  )  )
      except:
        print "reading error"

    return render_template('results.html', results = results)

  else:
    return render_template('search.html')

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)

