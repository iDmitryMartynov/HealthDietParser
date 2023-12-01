import json
import random
import time
import requests
from bs4 import BeautifulSoup
import csv

link = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'

headers = {
    'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
}

response = requests.get(link, headers=headers)

page = response.text


soup = BeautifulSoup(page, 'lxml')

product_hrefs = soup.find_all(class_='mzr-tc-group-item-href')

categories = {}
for i in product_hrefs:
    name_product = i.text
    href = 'https://health-diet.ru' + i['href']
    categories[name_product] = href
    print(f'{name_product}: {href}')

with open('categories.json', 'w', encoding='utf-8') as file:
    json.dump(categories, file, indent=4, ensure_ascii=False)

with open('categories.json', 'r', encoding='utf-8') as file:
    categories = json.load(file)

count_iteration = int(len(categories)) - 1
count = 0

print(f'Всего итераций: {count_iteration}')

for name_product, href_product in categories.items():

    response = requests.get(href_product, headers=headers)
    response = response.text

    with open(f'data/{count}_{name_product}.html', "w", encoding='utf-8') as file:
        file.write(response)

    with open(f'data/{count}_{name_product}.html', encoding='utf-8') as file:
        response = file.read()

    soup = BeautifulSoup(response, 'lxml')

    alert_block = soup.find(class_='uk-alert-danger')
    if alert_block:
        continue

    table_list = soup.find(class_='mzr-tc-group-table').find('tr').find_all('th')
    product = table_list[0].text
    calories = table_list[1].text
    protein = table_list[2].text
    fats = table_list[3].text
    carbohydrates = table_list[4].text

    with open(f'data/{count}_{name_product}.csv', 'w', encoding='utf-8-sig', newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow((product, calories, protein, fats, carbohydrates))

    products_data = soup.find(class_='mzr-tc-group-table').find('tbody').find_all('tr')

    product_info = []
    for i in products_data:
        product_ids = i.find_all('td')
        title = product_ids[0].find('a').text
        calories = product_ids[1].text
        protein = product_ids[2].text
        fats = product_ids[3].text
        carbohydrates = product_ids[4].text

        product_info.append(
            {
                'title': title,
                'Calories': calories,
                'Protein': protein,
                'Fats': fats,
                'Carbohydrates': carbohydrates
            }
        )

        with open(f'data/{count}_{name_product}.csv', 'a', encoding='utf-8-sig', newline="") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow((title, calories, protein, fats, carbohydrates))

    with open(f'data/{count}_{name_product}.json', 'a', encoding='utf-8-sig', newline="") as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f'Итерация {count}. {name_product} записан')
    count_iteration = count_iteration - 1

    if count_iteration == 0:
        print("Работа завершена")
        break
    print(f'Осталось итераций: {count_iteration}')
    time.sleep(random.randrange(2, 4))