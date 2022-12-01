from collections import defaultdict
import os
import pickle
from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, SelectField, RadioField, StringField
from wtforms.validators import DataRequired,EqualTo, ValidationError, InputRequired
import pandas
from flask import request
from tabulate import tabulate

from tastes1 import tastes


app = Flask(__name__)
app.config['SECRET_KEY'] = 'kek'


def token_item(item):
  if not item=="сыр" or len(item)>3:
      return item[:-1]
  else:
      return item

TASTE=defaultdict(list)

for item in tastes:
        TASTE[item[0]].append(item[1])
    

with open("recepies.pkl", "rb") as f:
  tastes_df=pickle.load(f)

tastes_df = tastes_df.iloc[: , :-2]






class MyForm(FlaskForm):
    taste = StringField('Напишите основной продукт для блюда', validators=[InputRequired()])
    submit = SubmitField('Найти')
    
    
##    ingr=RadioField('Кухня',
##                       choices=['азиатская', 'европейская', '', "повседневный"],
##                       validators=[InputRequired()])

@app.route('/', methods=['GET', 'POST'])
def index():
    global TASTE
    form = MyForm()
    
    global tastedata
    result_taste=None
    ingredients_to_search=[]
    
    if form.validate_on_submit():
      tastedata=form.taste.data.lower()
      
      if tastedata in TASTE.keys():
        print(form.taste.data.lower())
        result_taste=TASTE[form.taste.data.lower()] #MAY BE SEVERAL ITEMS!!! SO, several searches of recepies
    
       

        #THIS IS TO FORM BUTTONS
        for i in result_taste:
              item=[form.taste.data.lower(), i]
              ingredients_to_search.append(item)
        print(ingredients_to_search)

        ###HERE ANOTHER FORM 
        #####ingredients_tokens=[token_item(item) for item in result_taste


        if not form.taste.data.lower() in TASTE.keys():
            result_taste="Что-то ничего не смогли найти =("

    
        #return redirect(url_for("recepies", taste=taste)) #(f'recepies/{taste}'))
            

        #result_recepie= #TO DO _ SEARCH


    form.taste.data = ""
    return render_template('index.html', form=form, ingredients_to_search=ingredients_to_search)

@app.route('/recepies/', methods=['GET', 'POST'])
def recepies():
    global tastes_df
    if request.method == 'POST':
        taste=request.form["choice_button"]# BUTTONS WITH INGREDIENT LIST
        print(type(taste))
        resulttaste = "".join(x for x in taste if x.isalpha() or x.isspace())
        print(resulttaste)
        taste_list=resulttaste.split(" ") #list
        print(taste_list)
        ingredients_tokens=[token_item(item) for item in taste_list]
        print( ingredients_tokens, type(ingredients_tokens))
        print(len(ingredients_tokens))

    
        result_df=tastes_df[tastes_df["Состав"].apply(lambda a: all(i in str(a) for i in ingredients_tokens))]
        if "сыр" in ingredients_tokens:
          result_df=result_df[result_df["Состав"].str.contains("сыры|сырая|сыро")==False]
        if "виногра" in ingredients_tokens:
          result_df=result_df[result_df["Состав"].str.contains("виноградн")==False]
        result_df["Описание"]=result_df["Описание"].str.replace("_x000D_", "").replace('\n', "")
        #result_df = result_df.iloc[: , :-2]
        print("_________________________________________")
        print("_________________________________________")
        print("_________________________________________")
        print(result_df.shape)
        print(result_df.columns)
        
        
        result_df_list=list(result_df.values)

        print(type(result_df_list))
        print(len(result_df_list))
        for item in result_df_list:
            print(item, "/n", "______________________________________________________")
        
      
##        for i in range(0, len(result_df)):
##            print(result_df.iloc[i])
        ##result_df_html=tabulate(result_df, headers='keys', tablefmt='html')
            
        if len(result_df)==0:
          return redirect(url_for("no_recepies"))


            
    return render_template("recepies.html", recepies=result_df_list)

@app.route('/no_recepies')
def no_recepies():
    return render_template("no_recepies.html")


@app.route('/single_ingredient_recepies', methods=['GET', 'POST'])
def single_ingredient_recepies():
    global tastes_df
    if request.method == 'POST':
      single_ingredient=token_item(tastedata)
      print("_________________________________________")
      print("_________________________________________")
      print("_________________________________________")
      print(single_ingredient)
      print(type(single_ingredient))
      result_df=tastes_df[tastes_df["Состав"].str.contains(single_ingredient)==True]
      result_df["Описание"]=result_df["Описание"].str.replace("_x000D_", "").replace('\n', "")
      result_df_list=list(result_df.values)
    return render_template("single_ingredient_recepies.html", recepies=result_df_list)
      
   



app.run('0.0.0.0', os.environ.get('PORT', 5000))


