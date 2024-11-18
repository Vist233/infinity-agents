from baidusearch.baidusearch import search
 
results = search('Full Stack Developer')  # 返回10个或更少的结果
for result in results:
    print(result['title'], result['url'])