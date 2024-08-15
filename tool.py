import time,asyncio,random,re,requests
from websockets.sync.client import connect
import json
import time
import hashlib,threading

def get_pos(list_num):
    list1 = [1,-1,120,-120,121,119,-121,-119]
    list_all=[]
    for num in list_num:
        list_all = list_all + list(num +i for i in list1)
    if list_all!=[]:
        pos =max(list_all,key=list_all.count)
        return pos
    else:return 0
def get_num(string):
    temp = re.findall(r'\d+', string)
    print(temp)
    # res = list(map(int, temp))
    try:return int(temp[0])
    except:return 0
def po_ex_xy(pos):
    y = int(int(pos)/120)
    x = int(int(pos))%120
    return x,y
def po_ex_num(x,y):
    pos_num = int(y*120+x)
    return pos_num
def get_safe_positions(mypos,enemy_positions):
    def pos_to_matrix(enpos,mypos):
        tru = int(mypos) - int(enpos)
        if tru ==1:pos_enermy =(1,0)
        elif tru==-1:pos_enermy=(1,2)
        elif tru ==120:pos_enermy=(0,1)
        elif tru ==-120:pos_enermy=(2,1)
        elif tru ==121:pos_enermy=(0,0)
        elif tru ==119:pos_enermy=(0,2)
        elif tru ==-121:pos_enermy=(2,2)
        elif tru==-119:pos_enermy =(2,0)
        else:pos_enermy=None
        return pos_enermy
    
    def matrix_to_pos(matrix_pos, mypos):
        matrix_positions = {
            (1, 0): 1,
            (1, 2): -1,
            (0, 1): 120,
            (2, 1): -120,
            (0, 0): 121,
            (0, 2): 119,
            (2, 2): -121,
            (2, 0): -119
        }
        delta = matrix_positions.get(matrix_pos)
        if delta is not None:
            return mypos - delta
        return None  # Trả về None nếu không tìm thấy kết quả phù hợp
    # Tính toán phạm vi tấn công của tất cả kẻ địch (vùng 3x3)
    my_position=(1,1)
    enemy_positions = list(pos_to_matrix(enpos=pos,mypos=mypos) for pos in enemy_positions)
    enemy_attack_range = set()
    for enemy_position in enemy_positions:
        for i in range(-1, 2):
            for j in range(-1, 2):
                enemy_attack_range.add((enemy_position[0] + i, enemy_position[1] + j))

    # Tạo danh sách các vị trí an toàn (không nằm trong phạm vi tấn công của kẻ địch)
    safe_positions = []
    for i in range(3):
        for j in range(3):
            position = (my_position[0] - 1 + i, my_position[1] - 1 + j)
            if position not in enemy_attack_range:
                safe_positions.append(position)
    safe_positions = list(matrix_to_pos(matrix_pos=pos,mypos=mypos) for pos in safe_positions)
    return safe_positions
def create_list_move(start_pos,end_pos,blocked_positions=None):
    # print(start_pos,end_pos)
    rows, cols = 60, 120
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]
    if blocked_positions == None:blocked_positions=[]
    # for r, c in blocked_positions:
    #     matrix[r][c] = 1
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
    list_move=[]
    list_move.append(start_pos)
    while start_pos != end_pos :
        shortest_distance={}
        for direction in directions:
            current=list_move[-1]
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows and  neighbor not in blocked_positions and neighbor not in list_move:
                x=abs(end_pos[0]-neighbor[0])
                y=abs(end_pos[1]-neighbor[1])
                shortest_distance[(x,y)]=neighbor
        shortest= list(shortest_distance.keys())
        shortest1=list(set(x[0] for x in shortest))
        shortest2=list(set(x[1] for x in shortest))
        shortest1.sort()
        shortest2.sort()
        st=(shortest1[0],shortest2[0])
        if st in shortest:pass
        elif len(shortest1) > len(shortest2):
            shortest.sort()
            st = shortest.pop(0)
        elif len(shortest1) < len(shortest2):
            shortest = [(y,x) for x,y in shortest]
            shortest.sort()
            y,x = shortest.pop(0)
            st=(x,y)
        elif len(shortest1) == len(shortest2):
            a = [abs(x-y) for x,y in shortest]
            b=a.copy()
            b.sort()
            st=shortest[a.index(b.pop(0))]
        else:
            st = random.choice(shortest)
        list_move.append(shortest_distance[st])
        if st ==(0,0):break
    return list_move
class py_9g_auto():
    def __init__(self,username,password,set_rich,proxy=None,item_skip:list=None):
        self.header={
            'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'Referer':'https://cmangaog.com/user/game/dashboard',
            'Origin': 'https://cmangaog.com',
            'Sec-Ch-Ua-Mobile':'?0',
            'Priority': 'u=1, i',
            'Sec-Ch-Ua-Platform':"Windows",
            'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Fetch-Dest':'empty',
            'Sec-Fetch-Mode':'cors',
            'Sec-Fetch-Site':'same-origin',
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            'X-Requested-With':'XMLHttpRequest',
           }
        self.requests = None
        self.proxies = {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}'
        }
        self.proxies = None if proxy =="" or proxy==None else self.proxies
        self.url="https://cmangaog.com"
        self.url_battle_map_player_data=f"{self.url}/api/battle_map_player_data"
        self.url_user=f"{self.url}/assets/ajax/user.php"
        self.url_battle_map=f"{self.url}/assets/ajax/battle_map.php"
        self.url_api_user_data = f"{self.url}/api/user_data"
        self.user=None
        self.character=None
        self.token_character=None
        self.map=None
        self.player_map_id=None
        self.current_hp=None
        self.list_pos_ar=None
        self.pos_now=None
        self.last_move=0
        self.level=None
        self.set_rich=set_rich
        self.username=username
        self.password=password
        self.player=False
        self.websocket_send=''
        self.t=self.get_Session()
        self.item_out={'job_exp_4':1,'egg_rare':1,'medicinal_point_plus':1,'medicinal_upgrade_king':1,'egg_legendary':1,'guild_boss_1':1,'guild_boss_2':1,'guild_boss_3':1}
        self.item_skip=[]
        self.item_skip.extend(item_skip)
    def get_Session(self,):
        print('login')
        seesion = requests.Session()
        pa = {"action":"login"}
        pa.update({"username":self.username})
        pa.update({"password":self.password})
        while True:
            try:
                a = seesion.post(url =self.url_user,data=pa,headers=self.header,proxies=self.proxies,timeout=20)
                print(f'{self.username} {a.text}')
                if a.status_code==200:break
                time.sleep(10)
            except Exception as e:time.sleep(10)
        if 'text_login_fail' in a.text:
            print(f'{self.username} text_login_fail')
            return False
        user =(a.text.replace("';location.reload();</script>",'').replace("<script>token_user = '",'')).strip()
        self.requests=seesion
        self.user=user

    def get_character(self): # lấy số character
        payload={'data':'info','user':self.user, }
        while True:
            get = self.requests.get(url=self.url_api_user_data,headers=self.header,params=payload,proxies=self.proxies,timeout=20)
            try :
                reponse = get.json()["character"]
                self.character=reponse
                break
            except Exception as e:time.sleep(10)
    def g_token_character(self):
        while True:
            try:
                url='https://cmangaog.com/user/game/dashboard'
                get = self.requests.get(url=url,headers=self.header,proxies=self.proxies,timeout=20).text.splitlines()
                self.token_character=str(get[0].split('</script><script>token_chat')[0]).split('token_character=')[1].replace("'","")
                break
            except Exception as e:
                time.sleep(10)    
    def battle_map_player_data(self):
        param = {'token_character':self.token_character,
        'player': self.character,
        'type': 'word',
        'v':int(time.time())}
        while True:
            try:
                get = self.requests.get(url=self.url_battle_map_player_data,headers=self.header,params=param,proxies=self.proxies,timeout=20)
                # print(get.text)
                if get.status_code !=200:time.sleep(1)
                else:break
            except Exception as e:time.sleep(10)
        get =get.json()
        if get!={} or get != '{}':
            self.pos_now=int(get['position'])   
            self.player_map_id=int(get['player_map_id'])
            self.map=get['area']    
            data=get['data']
            data=json.loads(data)
            self.bag =data['bag']
            self.rich=data['score'].get('rich')
            if self.rich ==None:self.rich=0
            try:
                self.current_hp=data['current_hp'].get(f'{self.character}_{self.character}')
            except:self.current_hp=None
            self.name =data['name']
            # print(self.current_hp)
            if self.current_hp !=None and self.current_hp < 10000 :self.restore()
        else :self.pos_now=0
    def level_(self):
        while True:
            try:
                url=f'https://cmangaog.com/api/get_data_by_id?table=game_character&data=info&id={self.character}'
                print(url)
                get = self.requests.get(url=url,headers=self.header,proxies=self.proxies,timeout=20).json()['info']
                get = json.loads(get)['level']['num']
                # print(get)
                self.level = get
                print(self.level)
                break
            except:time.sleep(10)
    def join_to_word(self,map=None):
        try:map=int(map)
        except:pass
        if  isinstance(map,(int)) :numword=map
        elif 1 <= self.level and self.level <= 29: numword =2
        elif 30 <= self.level and self.level <= 39: numword =3
        elif 40 <= self.level and self.level <= 49: numword =4
        elif 50 <= self.level and self.level <= 59: numword =5
        elif 60 <= self.level and self.level <= 99: numword =6
        data={'action': "join",'type': 'word','area':numword}
        print(data)
        while True:
            try:
                rp = self.requests.post(url=self.url_battle_map,data=data,headers=self.header,proxies=self.proxies,timeout=20)
                print(rp.text)
                if rp.status_code==200:break
                time.sleep(10)
            except:time.sleep(10)
        # print(f'{self.username} {rp.text}')
        if 'text_world_gold_fee' in rp.text:
            return "gold is not enough"
        self.map=numword
        sleep=get_num(rp.text)
        return sleep
    def exit_world(self):
        data={ 'action': "word_exit" , "target": "1"}
        while True:
            try:
                rp = self.requests.post(url=self.url_battle_map,data=data,headers=self.header,proxies=self.proxies,timeout=2)
                break
            except:time.sleep(10)
        if 'popup_load' in rp.text:
            self.pos_now=0
        return rp.text
    def restore(self):
        data={'action': 'restore','type': 'word',}
        try:
            rp = self.requests.post(url=self.url_battle_map,data=data,headers=self.header,proxies=self.proxies,timeout=2)
        except:pass
        # print(f'{self.username} {rp.text}')
    def repair(self):
        data={'action': 'equipment_repair'}
        try:
            rp = self.requests.post(url='https://cmangaog.com/assets/ajax/character.php',data=data,headers=self.header,proxies=self.proxies,timeout=2).text
        except:pass
        # print(f'{self.username} {rp}')

    def move(self,pos):
        st=time.time()
        times =int(time.time()/1000)
        str_to = str(pos)+'z'+self.character+self.user+str(times)
        sha1=hashlib.sha1(str_to.encode()).hexdigest()
        data={'action': "move",'type': 'word','position': pos,'area': self.map,'token_check': sha1}
        try:
            rp = self.requests.post(url=self.url_battle_map,data=data,headers=self.header,proxies=self.proxies,timeout=3).text.strip().strip('\n')
        except Exception as e:return
        print(f'{self.username} {rp}')
        self.last_move=time.time()
        if 'Lỗi vị trí' in rp:
            return False
        if 'reload_position_data' in rp:
            
            a=threading.Thread(target=send_mess,args=(rp,))
            a.start()
        print(self.username,time.time()-st)
        return rp
    def battle_data(self,id):
        url = f'https://cmangaog.com/api/get_data_by_id?table=game_battle&data=data&id={id}'
        battle=requests.get(url=url,headers=self.header,proxies=self.proxies,timeout=3).text
        battle=json.loads(battle)['data']
        battle=json.loads(battle)
        if battle['winner']==int(self.character):
            self.current_hp=int(battle['team'][str(self.character)]['current']['hp'][str(self.character)+'_'+str(self.character)])
    def battle_map_position_data(self):
            data_tre=[]
            data_pla=[]
            data_o=[]
            pos=0
            try:
                url = f"{self.url}/api/battle_map_position_data?token_character={self.token_character}&player={self.character}&type=word&v={int(time.time())}"
                map_positions=self.requests.get(url=url,headers=self.header,proxies=self.proxies,timeout=5).text
                if map_positions==None or map_positions=={} or map_positions=='{}' :
                    pos=0
                    list_pos=[]
                else:
                    map_positions=json.loads(map_positions)
                    list_pos=list(int(i.get('position')) for i in map_positions)
                    async def check_pos(i):
                            target =json.loads(i.get('data')).get('target')
                            # print(target)
                            if  target == 'player':
                                data_pla.append(i.get('position'))
                            if target =="treasure":
                                # print(target,json.loads(i.get('data'))['target_data']['sign'],self.item_skip )
                                if json.loads(i.get('data'))['target_data']['sign'] not in self.item_skip:
                                    data_tre.append(i.get('position'))
                            if target!='player' and target!='treasure' and target!= 'none':
                                data_o.append(i.get('position'))
                            # print(target)
                    async def main():
                        await asyncio.gather(*[check_pos(i) for i in map_positions])   
                    asyncio.run(main())
                    pos =get_pos(list_num=list_pos)
            except Exception as e:
                pos=0
                list_pos=[]
                
            self.pos_now=pos
            # print(pos)
            self.list_pos_ar=list_pos
            if len(data_pla)!=0:self.player=True
            self.data_position = {'p':data_pla,'t':data_tre,'o':data_o}
    def avoid_enermy(self):
            
            self.restore()
            check_player = self.data_position['p']
            pos = self.pos_now
            pos_es = get_safe_positions(enemy_positions=check_player,mypos=pos)
            pos_es_ex = [x for x in pos_es if x not in check_player and x not in self.data_position['o']]
            pos_es_end = random.choice(pos_es_ex)
            self.player=False
            return pos_es_end
    def Delay(self,time_s):
        a=0
        while True:
            t=time.time()-self.last_move
            if int(t)%2==0:
                self.battle_map_position_data()
            if  self.player==True and self.map!=1:return 'player'
            elif t>time_s :return 
            time.sleep(0.5)
    def wait_treasure(self,po_tre):
        time_move = self.last_move
        if self.move(po_tre)==False:
            return False
        if self.Delay(61)=='player':return
        self.move(po_tre)
        self.last_move=time_move
    def condition_out(self):
        self.battle_map_player_data()
        print(f'{self.username} {self.rich} {self.set_rich},{list(self.bag.keys())} ,{self.current_hp}')
        if int(self.rich) > int(self.set_rich):
            return True
        for item in list(self.bag.keys()):
            if item  in (self.item_out.keys()):
                if self.bag[item]['amount'] >=  self.item_out[item]:
                    return True
def on_message(message,auto:py_9g_auto):
    try:
        message= json.loads(message)
        try:
            message=message['d']
            try:
                message=message['b']
                try:
                    d = message.get('d')
                    try:
                        player_id=d.get('player_id')
                        list_p=list(player_id.values())
                        # print(list_p)
                        try:
                            id =auto.player_map_id
                            if id in list_p:
                                auto.player=True
                                print(f'{auto.username} {id}')
                            
                        except:print(6)
                    except:print(5)
                except:print(4)
            except:print('3')
        except:print('2')
    except:print('1')
def on_open(wsapp,auto:py_9g_auto):
    wsapp.send("""{"t":"d","d":{"r":1,"a":"s","b":{"c":{"sdk.js.8-8-1":1}}}}""")
    a=str({"t":"d","d":{"r":8,"a":"q","b":{"p":f"/Cmanga/Activity/word_{auto.map}","h":""}}}	).replace("'",'"')
    wsapp.send(a)
    data=str({"t":"d","d":{"r":9,"a":"q","b":{"p":f"/Cmanga/Activity_Noti/word_{auto.map}/{auto.character}","h":""}}}).replace("'",'"')
    wsapp.send(data)
def send_mess(str_send):
    def mess(string):
        match = re.search(r"firebase_custom\('([^']+)',\s*({.*?})\)", string.replace('\n',''))
        if match:
            path = match.group(1).rstrip("/")
            data = match.group(2)
            data_object = json.loads(data)
            mydict={}
            for index, element in enumerate(data_object['player_id']):
                mydict[str(index)] = element
            data_object['player_id']=mydict
            data_object.pop('position')
            d1={'target':data_object.pop('target')}
            d2={'value':data_object.pop('value')}
            data_object.update(d1)
            data_object.update(d2)
            out = str(json.dumps({"t":"d","d":{"r":5,"a":"p","b":{"p":f"/Cmanga{path}","d":data_object }}})).replace(' ','')
            return out
    str_send=mess(string=str_send)
    with connect("wss://s-apse1b-nss-206.asia-southeast1.firebasedatabase.app/.ws?v=5&ns=cmanga-chat-default-rtdb") as websocket:

        websocket.send(str_send)
def ws_check(auto:py_9g_auto):
    while auto.pos_now!=0:
        try:
            with connect("wss://s-apse1b-nss-206.asia-southeast1.firebasedatabase.app/.ws?v=5&ns=cmanga-chat-default-rtdb") as websocket:
                on_open(wsapp=websocket,auto=auto)
                while auto.pos_now!=0:
                        # print('stop',self.stop_thread)
                            message = websocket.recv()
                            on_message(message=message,auto=auto)
        except Exception as e:pass
def run_tool(username,passw,rich,proxy=None,item_skip=None,map=None,item_out=None):
        while True:
            try:
                proxy = proxy.split(":")
                proxy=str(proxy[2]+':'+proxy[3]+'@'+proxy[0]+':'+proxy[1]).replace(' ','')
                print(proxy)
            except:proxy=''
            print(username,passw,rich,proxy,item_skip,map,item_out)
            if map ==None or map == '':map=None
            auto =py_9g_auto(username,passw,rich,proxy,item_skip)
            if auto.t==False:return
            auto.get_character()
            auto.level_()
            if item_out !='None' or item_out !=None:
                print(item_out)
                try:
                    auto.item_out.update(eval(item_out))
                except:pass
                print(auto.item_out)
            if auto.t==False:
                print('wrong')
                return False
            print('join')
            auto.repair()
            time_join = auto.join_to_word(map)
            print(f'{username} {time_join}')
            while True:
                if time_join=="gold is not enough":
                    time.sleep(3600)
                    reloads = True
                    break
                elif type(time_join) is int:
                            time.sleep(time_join)
                            if time_join!=0:
                                auto.join_to_word()
                                reloads = True
                            elif time_join==0:reloads = False
                            break
                else:reloads = False;break
            if reloads == True:continue
            auto.g_token_character()
            auto.battle_map_player_data()
            thread_ws = threading.Thread(target=ws_check,args=(auto,))
            thread_ws.start()
            while True:
                try:
                    auto.battle_map_position_data()
                    if auto.pos_now==0 :break
                    if auto.condition_out()==True:
                        print(f'{username} out')
                        if auto.Delay(65) ==None:
                            exit=auto.exit_world()
                            if auto.pos_now==0 :break
                            print(f'{username} {exit}')
                    print(f'{username}{auto.set_rich},{auto.rich}{auto.bag} ???')
                    blocked_positions=[po_ex_xy(x) for x in auto.data_position['o']]
                    start =po_ex_xy(auto.pos_now)
                    end =po_ex_xy(random.randint(1000,6000))
                    list_move=create_list_move(start,end,blocked_positions)
                    # print(list_move)
                    try:list_move.remove(start)
                    except:pass
                    list_move = [po_ex_num(x,y) for x,y in list_move]
                    for move in list_move:
                        if thread_ws.is_alive()==False:
                            print(':))')
                            thread_ws = threading.Thread(target=ws_check,args=(auto,))
                            thread_ws.start()
                        auto.battle_map_position_data()
                        posi_ar=auto.Delay(random.uniform(4,5))
                        if auto.pos_now==0 : print('pos_now' , auto.pos_now);break
                        print(f'{username} data ar {auto.data_position},move to {move}')
                        if posi_ar =="player":
                            time.sleep(2)
                            auto.battle_map_position_data()
                            print(f'{username} player')
                            p  =auto.avoid_enermy()
                            auto.move(p)
                            auto.battle_map_position_data()
                            print(f'{username} data ar {auto.data_position},move to {move}')
                            auto.last_move=time.time()
                            auto.Delay(random.uniform(16,17))
                            break
                        elif posi_ar==None:
                            # print(f'{username} di chuyen')
                            if len(auto.data_position['t'])!=0:
                                print(f'{username} treasure')
                                if auto.wait_treasure(auto.data_position['t'][0])=='player':
                                    break
                                auto.condition_out()
                                break
                            elif move in auto.data_position['o']:
                                print(auto.data_position['o'],move)
                                print(f'{username} :)')
                                break
                            elif move in auto.list_pos_ar:
                                print(f'{username} move')
                                mov =auto.move(move)
                                if mov ==False:
                                    break
                            else:break
                except Exception as e:time.sleep(60)
def check_date():
    data=requests.api.get('https://tools.aimylogic.com/api/now?tz=Asia/Istanbul&format=dd/MM/yyyy').json()
    if data['month']!=8:
        return False
def running():
    username =input("Username: ")# d['username']
    passw=input("Password: ") #d['password']
    rich=input("rich: ")#d['rich']
    skip=input("skip: ")#d['skip']
    out =input("out: ") #d['item_out']
    # proxy=open('proxy.txt','r').read().splitlines()
    ip=input("Proxy: ")#proxy[int(d['num_proxy'])%len(proxy)]
    map=input("map: ")#d['set_map']
    try:
        a=threading.Thread(target=run_tool,args=(username,passw,rich,ip,skip,map,out,))
        a.start()
    except Exception as e:pass
    time.sleep(1000)
if __name__ == "__main__":
    try:
        # data= sys.argv
        # data.pop(0)
        # keys=['id', 'username', 'password', 'rich', 'skip', 'item_out', 'num_proxy', 'set_map']
        # d = dict(zip(keys,data))
        # print(d)
        if check_date() ==False:pass
        else:running()
    except Exception as e:print(e);time.sleep(100)
