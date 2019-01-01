# Utilities for manipulating items and neopoints.
import re
from collections import defaultdict

from lib import NeoPage
from activities import bank_interest
from . import item_db

# Items will be deposited unless assigned a special role here.
item_policy = defaultdict(lambda: 'deposit')

def list_items():
    np = NeoPage()
    np.get('/inventory.phtml')
    items = np.findall(r'\n<td class=.*?>.*?</td>')
    for item in items:
        attr = re.search(r'<td class="(.*?)"><a href="javascript:;" onclick="openwin\((\d+)\);"><img src="http://images.neopets.com/items/(.*?)" width="80" height="80" title="(.*?)" alt="(.*?)" border="0" class="(.*?)"></a><br>(.*?)(<hr noshade size="1" color="#DEDEDE"><span class="attr medText">(.*?)</span>)?</td>', item, flags=re.DOTALL)
        item_id = attr[2]
        item_image = attr[3]
        item_desc = attr[4]
        item_name = attr[7]
        item_db.update_item(item_name, image=item_image, desc=item_desc)

def always_keep(item):
    item_policy[item] = None

def always_stock(item):
    item_policy[item] = 'stock'

def quickstock(exclude=[]):
    # First list items to add them to the item db
    np = NeoPage()
    list_items()
    np.get('/quickstock.phtml')
    items = np.findall(r'''<TD align="left">(.*?)</TD><INPUT type="hidden"  name="id_arr\[(.*?)\]" value="(\d+?)">''')
    args = []
    args.append('buyitem=0')
    for name, idx, item_id in items:
        args.append(f'id_arr[{idx}]={item_id}')
        if name in exclude: continue
        policy = item_policy[name]
        if policy:
            args.append(f'radio_arr[{idx}]={policy}')
    np.post('/process_quickstock.phtml', *args)

def ensure_np(amount):
    # Withdraws from the bank to get up at least [amount] NP.
    np = NeoPage()
    np.get('/bank.phtml')
    if np.contains('Collect Interest ('):
        bank_interest.bank_interest()
    nps = np.current_np()
    if nps >= amount: return
    need = amount - nps
    denom = 10**max(len(str(need)), len(str(amount)))
    need = (need // denom + 1) * denom
    np.post('/process_bank.phtml', 'type=withdraw', f'amount={need}')
    print(f'Withdrawing {need} NP')

def withdraw_sdb(item):
    # Withdraws item from SDB.
    np = NeoPage()
    np.get('/safetydeposit.phtml', f'obj_name={item}', 'category=')
    items = re.findall(r'''<td align="center"><img src="http://images.neopets.com/items/(.*?)" height="80" width="80" alt="" border="1"></td>\n<td align="left"><b>(.*?)<br><span class="medText"></span></b></td>\n<td width="350" align="left"><i>(.*?)</i></td>\n<td align="left"><b>(.*?)</b></td>\n<td align="center"><b>(.*?)</b></td>\n<td align="center" nowrap>\n.*<input type='text' name='back_to_inv\[(.*?)\]' size=3 value='0' data-total_count='(.*?)' class='remove_safety_deposit' data-remove_val='n' ><br>\n.*<a href="javascript:onClick=passPin\((.*?),(.*?),'(.*?)','(.*?)'\);" class="medText">Remove One</a></td>
</tr>''', np.content)
    for img, name, desc, cat, quant, _, _, offset, obj_info_id, obj_name, category in items:
        print(f'Have {quant}x {name}')
        if name == item:
            np.get('/process_safetydeposit.phtml', f'offset={offset}', f'remove_one_object={obj_info_id}', f'obj_name={obj_name}', f'category={category}', 'pin=')
            print('Took one.')
            break
    else:
        print(f'No {item} in SDB.')

def purchase(item, image=None, budget=None, quantity=1):
    # TODO
    level2_by_item = item_db.update_prices(name, laxness=laxness)
    to_spend = 0
    for obj_info_id, level2 in level2_by_item.items():
        for price, qty, url in level2:
            pass
    pass
