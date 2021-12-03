import requests
from bs4 import BeautifulSoup
import sqlite3

conn = sqlite3.connect('bergonline.db')

def parse(meal_no):
    URL = f"http://www.foodpro.huds.harvard.edu/foodpro/menu_items.asp?type=30&meal={meal_no}"
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
    
    return(new_dict)



for i in range(0,3):
    data = parse(i)

    for j in data:
        with conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO menu_data (name, link, meal, calories, carbs, fat, protein, serving_size) VALUES (?,?,?,?,?,?,?,?)",
                              (j[0], j[1], i, data[j][0], data[j][1], data[j][2], data[j][3], data[j][4]))
            except TypeError:
                continue
            conn.commit()
    print("meal" + str(i) + "loaded")