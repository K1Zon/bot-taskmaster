import requests
from bs4 import BeautifulSoup
import psycopg2
from time import sleep
import schedule


def get_data():
    try:
        conn = psycopg2.connect(dbname='tasks', user='postgres', password='7355608k', host='localhost')
    except:
        print("Can't establish connection to database")

    cur = conn.cursor()
    url = "https://codeforces.com/problemset?order=BY_RATING_ASC"
    resp = requests.get(url)
    html = resp.content
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find_all('span', 'page-index')
    max_page = int(pages[-1].text)

    for page in range(1, max_page+1):
        url = f"https://codeforces.com/problemset/page/{page}?order=BY_RATING_ASC"
        response = requests.get(url)
        html = response.content

        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'problems'})
        rows = table.find_all('tr')
        rows = rows[1:]

        for row in rows:
            data = []

            cols = row.find_all('td')

            # 0 - id
            # 1 - name
            # 2 - tag
            # 3 - difficulty
            # 4 - times solved

            link = cols[0].find('a')
            href = link.get('href')
            href = 'https://codeforces.com' + href

            num = cols[0].text.strip()

            name_tags = cols[1].text.strip().replace(',', '')

            tags = name_tags.split('   ')
            tags = [tag.strip() for tag in tags]
            tags = list(filter(None, tags))

            name = tags[0]
            tags = tags[1:]

            difficulty = cols[3].text.strip()
            solved = cols[4].text.strip()

            data.append([num, name, tags, difficulty, solved, href])

            for dat in data:
                cur.execute(
                    f"INSERT INTO tasks (num, name, difficulty, solved, link) VALUES ('{dat[0]}', $${dat[1]}$$, '{dat[3]}', '{dat[4]}', $${dat[5]}$$) ON CONFLICT DO NOTHING"
                )
                for i in range(len(tags)):
                    cur.execute(
                        f"INSERT INTO tags (tag_name) VALUES ('{dat[2][i]}') ON CONFLICT DO NOTHING;\n"
                        f"INSERT INTO tasks_tags (task_num, tag_id) SELECT num, tag_id FROM tasks, tags WHERE num = '{dat[0]}' AND tag_name = '{dat[2][i]}' ON CONFLICT DO NOTHING"
                    )

    conn.commit()
    cur.close()
    conn.close()



while True:
    get_data()
    print("i parsed")
    sleep(3600)


