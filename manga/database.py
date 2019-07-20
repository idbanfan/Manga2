import os,sys,time

import pymongo


def main():

    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    data_base = myclient["local"]
    tag_table = data_base['tag_table']



    for tag_name in []:
        result = tag_table.insert_one({
            'tag_name': tag_name,
            'tag_type': 'manga_product',
            'sub_type': 'style'
        })

        print(
            result.acknowledged,
            result.inserted_id
        )

    #tag_table.drop()
    # for each in tag_table.find({'tags':{ "$regex": "color"}},{'_id':0}):
    #     print(each['path'])

    # t = tag_table.update_one(
    #     {'tag_type': 'quick_tag'},
    #     {"$set": {"tags": "color;lolicon;group;sister;3p;pose;character;pantyhose;foot;shotacon;swimsuit;stockings;"
    #                       "kimono;schoolgirl uniform;maid;miko;yuri;bunny girl;school swimsuit;beauty"}}
    # )



    #print(t.acknowledged)


if __name__ == '__main__':
    main()