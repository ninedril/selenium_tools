from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import itertools, time
from collections import defaultdict

from importlib import reload

##### For debug, insert following
#import pdb; pdb.set_trace()

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
    

# WebDriver => [WebElement, WebElement, ...]
def find_google_result_links(wd):
    ##### 1. Collect all visible <a>
    all_links = select_visible(wd.find_elements_by_tag_name('a'))

    ##### 2. Make chain lists of antescedants by tag names(ex. ['a_div_div', 'a_p_div', ...])
    all_chains = list(map(lambda e: '_'.join(make_parent_chain(e, with_class=True)), all_links))

    ##### 3. Make dict {chain_str1: [WebElement, ...], chain_str2: ...}
    gid__links_d = defaultdict(list)
    for k, v in zip(all_chains, all_links):
        gid__links_d[k].append(v)
    
    ##### 4. Decide total area of each group by combination
    ###　各グループ同士のあるタグの組み合わせを作る
    ###　タグ同士を比較して、Final_parentをそれぞれ見つける
    ###　グループIDに、それぞれのFina_parentたちを登録していく
    gid__someFp_d = defaultdict(list)
    for gid__links_1, gid__links_2 in itertools.combinations(gid__links_d.items(), 2):
        parent_1, parent_2 = get_final_parent(gid__links_1[1][0], gid__links_2[1][0])
        gid__someFp_d[gid__links_1[0]].append(parent_1)
        gid__someFp_d[gid__links_2[0]].append(parent_2)
    ###　それぞれのグループIDのFinal_parentたちを、最小の一つに絞って登録
    gid__Fp_d = dict()
    for gid, someFp in gid__someFp_d.items():
        gid__Fp_d[gid] = get_minimum_element(someFp)
    ###　全グループ中、中心領域に最も近いFinal_parentを選び、そのグループID（k）を返す
    #中心領域(10%*10%)を求める
    center_pset = get_pointset_of_center_area(wd)
    #中心領域と「辺のみ」重なるFinal_parentを選択、重なった面積を算出してリストにする
    gids = []
    sizes = []
    for gid, fp in gid__Fp_d.items():
        fp_pset = get_pointset_from_element(fp)
        gids.append(gid)
        sizes.append(get_edge_overlapped_size_from_pointset(fp_pset, center_pset))
    ###　gid__links_dから、グループID（k）をKeyとする値（linkのリスト）を返す
    gid = gids[sizes.index(max(sizes))]
    return gid__links_d[gid]

# WebElement => ((int, int), (int, int))
# Pointset consists of two point
def get_pointset_from_element(elem):
    e_loc = ( \
        (elem.location['x'], elem.location['y']), \
        (elem.location['x'] + elem.size['width'], \
        elem.location['y'] + elem.size['height']) \
    )
    return e_loc

# WebDriver, float => ((int, int), (int, int))
def get_pointset_of_center_area(wd, ratio=0.05):
    w_width = wd.execute_script('return window.innerWidth')
    w_height = wd.execute_script('return window.innerHeight')
    start_point = (w_width/2 - w_width*ratio, w_height/2 - w_height*ratio)
    end_point = (w_width/2 + w_width*ratio, w_height/2 + w_height*ratio)

    return (start_point, end_point)

# WebElement, WebElement => boolean
def is_overlapped(elem1, elem2):
    e1_loc = get_pointset_from_element(elem1)
    e2_loc = get_pointset_from_element(elem2)

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

#((int, int), (int, int)), ((int, int), (int, int)) => int
# pointset1 MUST BE BIGGER than pointset2
def get_edge_overlapped_size_from_pointset(pointset1, pointset2):
    if not(is_edge_overlapped_from_pointset(pointset1, pointset2)):
        return 0
    a_x0, a_x1 = pointset1[0][0], pointset1[1][0]
    b_x0, b_x1 = pointset2[0][0], pointset2[1][0]

    # pointset1 is bigger
    if (a_x0 <= b_x0 < b_x1 <= a_x1):
        a_y0, a_y1 = pointset1[0][1], pointset1[1][1]
        b_y0, b_y1 = pointset2[0][1], pointset2[1][1]

        if (a_y0 < b_y0 < a_y1 < b_y1):
            return a_y1 - b_y0
        elif (a_y0 < b_y0 < b_y1 < a_y1):
            return b_y1 - b_y0
        elif (b_y0 < a_y0 < b_y1 < a_y1):
            return b_y1 - a_y0    
    # pointset2 is bigger
    elif (b_x0 <= a_x0 < a_x1 <= b_x1):
        return 0
    
    raise Exception('occured in get_overlapped_size_from_pointset()')


#[WebElement, WebElement, ...] => WebElement
#Return an elem with the least descendants
def get_minimum_element(elems):
    antes_numbers = list(map(lambda e: len(list(parentIterator(e))), elems))
    i = antes_numbers.index(max(antes_numbers))
    return elems[i]

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
def make_parent_chain(elem, length=3, with_class=False):
    p_chain = []
    parent = elem
    for i in range(length):
        try:
            parent = parent.find_element_by_xpath('parent::node()')
        except:
            break

        chain = parent.tag_name
        if with_class:
            chain = chain + '.' + parent.get_attribute('class')
        p_chain.append(chain)

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
        self._parent_elem = elem
    
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            self._parent_elem = self._parent_elem.find_element_by_xpath('parent::node()')
        except:
            raise StopIteration()
        return self._parent_elem