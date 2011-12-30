#_*_ coding: utf-8 _*_

class Loader(object):
    pass


class Parser(object):
    pass


class Archiver(object):
    pass




init loader
init archiver

loader.login()

parser for loader.get_page(1)
remote_count = parser.get_weibo_count()  #lock with this value

while parser.is_valid():
    for weibo in parser:
        created = archiver.save(weibo)
        if not created:
            the updated first
            break
    if have next page:
        parser for loader.get_page(next)

#now, update proccess finish
#remote_count should always great than or equal the archived_count
archived_count = archiver.get_weibo_count()

if archived_count == remote_count:
    archived success, exit


#try find out the page to continue archive
get page_num base on 10-per-page
parser for loader.get_page(page_num)
for weibo in parser:
    get unarchived_count 
if unarchived_count == parser.get_page_weibo_count():
    #all unarchived, try former page
    page_num -= 1 until 0
elif unarchived_count == 0:
    #all archived, try next page
    page_num += 1
else:
    #assert that the unarchived is not out of order
    now the page_num is the continue archive start page

parser for loader.get_page(page_num)
while parser.is_valid():
    for weibo in parser:
        created = archiver.save(weibo)
        assert created
    parser for load.get_page(next)

archived_count = archiver.get_weibo_count()

if archived_count == remote_count:
    archived success, exit
elif archived_count > remote_count:
    my failure
else:
    maybe some weibo had remote deleted

