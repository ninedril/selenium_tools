from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import itertools, time
from collections import defaultdict

from importlib import reload


#[selenium.webdriver.Chrome]
def launchChrome(is_headless=False):
	op = Options()
	op.add_argument('user-data-dir=setting/profile')
	if is_headless:
		op.add_argument('--headless')
		op.add_argument('--disable-gpu')
	op.binary_location = 'bin/chrome/chrome.exe'
	driver = webdriver.Chrome('bin/chromedriver.exe', chrome_options=op)
	return driver

#[boolean]
def search(wd, word):
    wd.get('https://www.google.com')
    inputs = wd.find_elements_by_css_selector('input[type="text" i]')
    inputs = list(filter(lambda e: e.is_displayed(), inputs))

    #####Select inputs which located in center
    body = wd.find_element_by_tag_name('body')
    inputs = list(filter(lambda e: is_centerd_x(e, body), inputs))
    
    #####decide elements
    if not(inputs):
        return False
    search_box = inputs[0]
    
    #####Search
    search_box.send_keys(word)
    search_box.submit()

    #####Click first page
    

#[list<selenium.webdriver.remote.webelement.WebElement>]
def find_google_result_links(wd):
    ##### 1. Collect all visible <a>
    all_links = select_visible(wd.find_elements_by_tag_name('a'))

    ##### 2. Make chain lists of antescedants by tag names(ex. ['a_div_div', 'a_p_div', ...])
    all_chains = list(map(lambda e: '_'.join(make_parent_chain(e)), all_links))

    ##### 3. Make dict {chain_str1: [WebElement, ...], chain_str2: ...}
    gid__links_d = defaultdict(list)
    for k, v in zip(all_chains, all_links):
        gid__links_d[k].append(v)
    
    ##### 4. Decide total area of each group by combination
    ###　各グループ同士のあるタグの組み合わせを作る
    ###　タグ同士を比較して、Final_parentをそれぞれ見つける
    ###　グループIDに、それぞれのFina_parentたちを登録していく
    gid__someFp_d = defaultdict(list)
    for gid__links_1, gid__links_2 in itertools.permutations(gid__links_d.items(), 2):
        parent_1, parent_2 = get_final_parent(gid__links_1[1][1], gid__links_2[1][1])
        gid__someFp_d[gid__links_1[0]].append(parent_1)
        gid__someFp_d[gid__links_2[0]].append(parent_2)
    ###　それぞれのグループIDのFinal_parentたちを、最小の一つに絞って登録
    gid__Fp_d = dict()
    for gid, someFp in gid__someFp_d.items():
        gid__Fp_d[gid] = get_minimum_element(someFp)
    ###　全グループ中、中心領域に最も近いFinal_parentを選び、そのグループID（r）を返す
    #中心領域を求める
    gid__Fp_d 
    #中心領域と「辺のみ」重なるFinal_parentを選択、重なった面積を算出してリストにする
    gid__Fp_overlapped_d = dict()
    for 
    ###　dから、グループID（r）をKeyとする値（linkのリスト）を返す


# WebElement => boolean
def is_overlapped_at_center(elem):

# WebElement => ((int, int), (int, int))
# Pointset consists of two point
def get_pointset(elem):
    e_loc = ( \
        (elem.location['x'], elem.location['y']), \
        (elem.location['x'] + elem.size['width'], \
        elem.location['y'] + elem.size['height']) \
    )
    return e_loc

# WebElement, WebElement => boolean
def is_overlapped(elem1, elem2):
    e1_loc = get_pointset(elem1)
    e2_loc = get_pointset(elem2)

    return is_overlapped_from_pointset(e1_loc, e2_loc)

#((int, int), (int, int)), ((int, int), (int, int)) => boolean
#((s_x0, s_y0), (s_x1, s_y1)), ((e_x0, e_y0), (e_x1, e_y1)) => is_overlapped?
def is_overlapped_from_pointset(pointset1, pointset2):
    b = (pointset1[0][1] < pointset2[1][1]) and (pointset2[0][1] < pointset1[1][1]) and \
        (pointset2[0][0] < pointset1[1][0]) and (pointset1[0][0] < pointset2[1][0])
    return b

#((int, int), (int, int)), ((int, int), (int, int)) => boolean
def is_edge_overlapped_from_pointset(pointset1, pointset2):
    if not(is_overlapped_from_pointset(pointset1, pointset2)):
        return False
    a_x0, a_x1 = pointset1[0][1], pointset1[1][1]
    b_x0, b_x1 = pointset2[0][1], pointset2[1][1]

    return (a_x0 <= b_x0 < b_x1 <= a_x1) or (b_x0 <= a_x0 < a_x1 <= b_x1)

#((int, int), (int, int)), ((int, int), (int, int)) => (int, int)
# 
def get_edge_overlapped_size_from_pointset(pointset1, pointset2):
    if not(is_overlapped_from_pointset(pointset1, pointset2)):
        return -1
    a_x0, a_x1 = pointset1[0][1], pointset1[1][1]
    b_x0, b_x1 = pointset2[0][1], pointset2[1][1]

    # pointset1 is bigger
    if (a_x0 <= b_x0 < b_x1 <= a_x1):
        if (a_y0 < b_y0 < a_y1 < b_y1):
            return a_y1 - b_y0
        elif (a_y0 < b_y0 < b_y1 < a_y1):
            return b_y1 - b_y0
        elif (b_y0 < a_y0 < b_y1 < a_y1):
            return b_y1 - a_y0    
    # pointset2
    elif (b_x0 <= a_x0 < a_x1 <= b_x1):
        if (b_y0 < a_y0 < b_y1 < a_y1):
            return b_y1 - a_y0
        elif (b_y0 < a_y0 < a_y1 < b_y1):
            return a_y1 - a_y0
        elif (a_y0 < b_y0 < a_y1 < b_y1):
            return a_y1 - b_y0
    else:
        return 0



#[WebElement, WebElement, ...] => [(x0, y0), (x1, y1)]
def get_elems_area_point(elem):
    pass

#[WebElement, WebElement, ...] => WebElement
#Return a minimum element from elems
def get_minimum_element(elems):
    pass

#[(WebElement, WebElement)]
def get_final_parent(elem1, elem2):
    elem1_parent = elem1
    elem2_parent = elem2
    elem1_antecedants = [elem1_parent]
    elem2_antecedants = [elem2_parent]
    while True:
        if elem1_parent.tag_name != 'body':
            elem1_parent = elem1_parent.find_element_by_xpath('parent::node()')
            elem1_antecedants.insert(0, elem1_parent)
        if elem2_parent.tag_name != 'body':
            elem2_parent = elem2_parent.find_element_by_xpath('parent::node()')
            elem2_antecedants.insert(0, elem2_parent)
        s1 = set(elem1_antecedants) & set(elem2_antecedants)
        if s1:
            common_parent = s1.pop()
            break
    elem1_final_parent = elem1_antecedants[elem1_antecedants.index(common_parent) + 1]
    elem2_final_parent = elem2_antecedants[elem2_antecedants.index(common_parent) + 1]
    return elem1_final_parent, elem2_final_parent

#[list<str>]
def make_parent_chain(elem, length=3):
    p_chain = []
    parent = elem
    for i in range(length):
        parent = parent.find_element_by_xpath('parent::node()')
        p_chain.append(parent.tag_name)
    return p_chain

#[list<selenium.webdriver.remote.webelement.WebElement>]
def old_find_google_result_links(wd):
    ##### 1.Collect vertical aligned <a /> as group
    all_links = select_visible(dv.find_elements_by_tag_name('a'))
    all_links_loc = [l.location['x'] for l in all_links]
    loc_links_dict = defaultdict(list)
    for k, v in zip(all_links_loc, all_links):
        loc_links_dict[k].append(v)
    ##### 2.Select group num 
    return loc_links_dict

#[list<selenium.webdriver.remote.webelement.WebElement>]
def select_visible(elem_list):
    new_elem_list = list(filter(lambda e: e.is_displayed(), elem_list))
    return new_elem_list

#[boolean]
def is_centerd_x(elem, parent_elem):
    center_loc = elem.location['x'] + elem.size['width']/2
    p_center_loc = parent_elem.location['x'] + parent_elem.size['width']/2
    p_loc_min = p_center_loc - parent_elem.size['width']*0.05
    p_loc_max = p_center_loc + parent_elem.size['width']*0.05
    if p_loc_min <= center_loc <= p_loc_max:
        return True
    else:
        return False

#[(username_elem, password_elem)]
def find_elements_for_login(wd):
    #####Collect all visible <input type='password'>
    password_inputs = wd.find_elements_by_css_selector('input[type="password" i]')
    password_inputs = list(filter(lambda e: e.is_displayed(), password_inputs))
    if not(password_inputs):
        return []
    
    #####Collect all visible <input type='text'>
    text_inputs = wd.find_elements_by_css_selector('input[type="text" i]')
    text_inputs = list(filter(lambda e: e.is_displayed(), text_inputs))
    if not(text_inputs):
        return []

    #####If both contains only one element, decide elements
    if len(password_inputs) == 1 and len(text_inputs) == 1:
        return text_inputs[0], password_inputs[0]
    
    #####Select by alignment and size
    password_text_list = list(itertools.product(password_inputs, text_inputs))
    #Select aligned (p, u)
    password_text_list = [(p, u) for (p, u) in password_text_list if is_aligned(p, u)]
    #Select same size (p, u)
    password_text_list = [(p, u) for (p, u) in password_text_list if p.size == u.size] 

    #####decide elements
    if not(password_text_list):
        return password_text_list[0][1], password_text_list[0][0]

def is_aligned(elem1, elem2):
    elem1_loc = elem1.location
    elem2_loc = elem2.location
    if(elem1_loc['x'] == elem2_loc['x'] or elem1_loc['y'] == elem2_loc['y']):
        return True
    else:
        return False

def exit_driver(wd):
    try:
        for w in wd.window_handles:
            wd.switch_to_window(w)
            wd.close()
            time.sleep(0.5)
    finally:
        wd.quit()

class parentIterator(object):
    def __init__(self, elem):
        print('enter __init__')
        self._parent_elem = elem
    
    def __iter__(self):
        print('enter __iter__')
        return self
    
    def __next__(self):
        print('enter __next__')
        try:
            self._parent_elem = self._parent_elem.find_element_by_xpath('parent::node()')
        except:
            raise StopIteration()
        return self._parent_elem

