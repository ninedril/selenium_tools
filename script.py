from function import *

if __name__ == 'script':
    dv = launchChrome()
    search(dv, 'xreading')
    
    try:
        a1 = select_visible(dv.find_elements_by_tag_name('a'))[10]
        for p in parentIterator(a1):
            print(p.tag_name)
    finally:
        time.sleep(5)
        exit_driver(dv)