from lib import item_db
from lib import g
import sys

def get_market(name, laxness):
    level2_by_item = item_db.update_prices(name, laxness=laxness)
    for obj_info_id, level2 in level2_by_item.items():
        print(f'obj_info_id {obj_info_id}')
        for price, qty, url in level2:
            print(f'{qty}@{price}: http://www.neopets.com{url}')

if __name__ == '__main__':
    item_name = sys.argv[1]
    laxness = 3 if len(sys.argv) <= 2 else int(sys.argv[2])
    get_market(sys.argv[1], laxness)
