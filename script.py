from function import *

if __name__ == '__main__':
    dv = launchChrome()
    search(dv, 'xreading')
    
    first_link = select_visible(dv.find_element_by_xpath('a'))