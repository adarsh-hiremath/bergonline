import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from flask import redirect, render_template, request, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def parse():
    URL = "http://www.foodpro.huds.harvard.edu/foodpro/menu_items.asp?type=30&meal=1"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    menu_items = soup.find_all("td", class_ = "menu_item")

    new_dict = {}

    for food_item in menu_items:
        for each in food_item.findAll("a"):
            href = each.get('href')
            new_dict[(each.string.strip(), href)] = None

    for (menu_item_name, menu_item_link), value in new_dict.items(): 
        another_page = requests.get(menu_item_link)
        soup2 = BeautifulSoup(another_page.content, "html.parser")
        # facts = soup2.find_all("td", class_ = "facts")
        calories = soup2.find("b", text="Calories:")
        carbs = soup2.find("b", text = "Total Carbs:")
        fat = soup2.find("b", text = "Total Fat:")
        protein = soup2.find("b", text = "Protein:")
        serving_size = soup2.find("b", text = "Serving Size:")

        try:
            calories = calories.next_sibling.strip(" g")
            carbs = carbs.next_sibling.strip(" g")
            fat = fat.next_sibling.strip(" g")
            protein = protein.next_sibling.strip("g ")
            serving_size = serving_size.next_sibling.strip()
            serving_size = serving_size.replace("\xa0",'')

        except:
            continue

        new_dict[(menu_item_name, menu_item_link)] = (calories, carbs, fat, protein, serving_size)