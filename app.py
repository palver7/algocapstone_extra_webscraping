from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

table = soup.find('table',attrs={'class': 'table table-striped table-hover table-hover-solid-row table-simple history-data'})
tr = table.find_all('tr')
temp = [] #initiating a tuple

for i in range(len(tr)):
#insert the scrapping process here
    cells = tr[i].find_all('td')
    if len(cells) > 2:
        date = cells[0].text
        value = cells[2].text
        date = date.strip()
        value = value.strip()
        temp.append([date, value]) 

temp = temp[::-1]

#change into dataframe
data = pd.DataFrame(temp, columns = ('date','value'))

#insert data wrangling here
data['date'] = pd.to_datetime(data['date'])
data['value'] = data['value'].apply(lambda x : x.replace("IDR",""))
data['value'] = data['value'].apply(lambda x : x.replace(",",""))
data['value'] = data['value'].astype('float')
data = data.set_index("date")
data = data.reindex(pd.date_range(start='2020-09-09', end='2021-03-08'))
data['value'] = data['value'].ffill()
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'USD {data["value"].mean().round(2)}'

	# generate plot
	ax = data.plot(figsize = (20,9))
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]


	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
