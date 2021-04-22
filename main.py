from copy import deepcopy
TIME_LENGTH=80
WAGE_STEP=100
rate_match=0.34#ミスマッチ指数: job*=10でt=30での失業率2.2%となるよう調整
min_wage=1013#最低賃金
min_liv_wage=1220000/12/173.8*1013/902#最低生計費
initial_unemp_n=[17094,100271]
unemp_n=deepcopy(initial_unemp_n)#新規就労希望者 [低求人,高求人]
unemp_e=[0,0]#経験者失業
wage=[i for i in range(600,2001,WAGE_STEP)]#時給:階級上限値
worker=[
    [[0,0],[0,0]], #-600
    [[0,0],[0,0]], #-700
    [[0,0],[0,0]], #-800
    [[0,0],[0,0]], #-900
    [[0,0],[0,0]], #-1000
    [[0,0],[0,0]], #-1100
    [[0,0],[0,0]], #-1200
    [[0,0],[0,0]], #-1300
    [[0,0],[0,0]], #-1400
    [[0,0],[0,0]], #-1500
    [[0,0],[0,0]], #-1600
    [[0,0],[0,0]], #-1700
    [[0,0],[0,0]], #-1800
    [[0,0],[0,0]], #-1900
    [[0,0],[0,0]], #1901-
]#雇用者数: [時給階層][低求人/高求人][フルタイム/パートタイム]
job=[
    [0,0], #-600
    [0,0], #-700
    [0,0], #-800
    [0,0], #-900
    [0,0], #-1000
    [536,3294], #-1100
    [893,5490], #-1200
    [834,5124], #-1300
    [208,1281], #-1400
    [149,915], #-1500
    [89,549], #-1600
    [119,732], #-1700
    [30,183], #-1800
    [0,0], #-1900
    [11137,68437] #1901-
]#求人: [時給階層][低求人/高求人]: フルタイム換算
rate_part=[
    [1,1], #-600
    [1,1], #-700
    [1,1], #-800
    [1,1], #-900
    [1,1], #-1000
    [0.9,0.9], #-1100
    [0.9,0.9], #-1200
    [0.8,0.8], #-1300
    [0.7,0.7], #-1400
    [0.6,0.6], #-1500
    [0.5,0.5], #-1600
    [0.3,0.3], #-1700
    [0.2,0.2], #-1800
    [0.1,0.1], #-1900
    [0.01,0.01] #1901-
]
worktime=[1,0.53]#[フル/パート]
history_unemp=[-1 for i in range(TIME_LENGTH)]
history_poor=[-1 for i in range(TIME_LENGTH)]
def update_min_wage(t):
    global min_wage
    if t>=30: #この辺りで諸数値が安定する
        min_wage=1200

def update_unemp():
    global unemp_n,unemp_e,worker
    for type in range(len(worker[0])):
        for i in range(len(worker)):
            for full_part in range(len(worker[0][0])):
                if i==len(worker)-1: #主に正規雇用
                    rate_retire=0.025 #40年で入れ替わり
                    rate_change=0.170-rate_retire
                else:
                    rate_retire=0.025 #40年で入れ替わり
                    rate_change=0.396-rate_retire
                unemp_e[type]+=worker[i][type][full_part]*rate_change#転職
                worker[i][type][full_part]=worker[i][type][full_part]*(1-rate_change-rate_retire)#退職
    #非就業者のretire
    rate_retire=0.025
    unemp_e[0]*=(1-rate_retire)
    unemp_e[1]*=(1-rate_retire)
    unemp_n[0]*=(1-rate_retire)
    unemp_n[1]*=(1-rate_retire)
    #新規参入
    unemp_n[0]+=initial_unemp_n[0]*rate_retire
    unemp_n[1]+=initial_unemp_n[1]*rate_retire

def update_job():
    pass

#return [n_full,n_part]
def _n_job(i,type):
    n_emp_total=job[i][type]*min((wage[i]-WAGE_STEP/2)/min_wage,1) #階級値/最低賃金だけ最低賃金で雇用
    rp=rate_part[i][type] #パート比率
    n_job=[(1-rp)/(1-(worktime[0]-worktime[1])*rp) * n_emp_total,
           rp/(1-(worktime[0]-worktime[1])*rp) * n_emp_total] #人が足りている場合
    sum_n_job=n_job[0]+n_job[1]
    sum_worker=worker[i][type][0]+worker[i][type][1]
    sum_employable=rate_match*(unemp_e[type]+unemp_n[type])
    for full_part in range(2):
        n_job[full_part]*=min((sum_worker+sum_employable)/sum_n_job, 1) if sum_n_job>0 else 1
        #人手不足の調整: rate_part一定でn_jobを小さく
    return n_job

def update_worker():
    global worker,job,unemp_n,unemp_e
    for type in range(len(worker[0])):
        for i in range(len(worker)-1,-1,-1):
            if(wage[i]<=min_wage):
                break
            n_under_min_wage=[0,0]
            if(wage[i-1]<=min_wage):
                for j in range(0,i):
                    for full_part in range(len(worker[0][0])):
                        unemp_e[type]+=worker[j][type][full_part]
                        worker[j][type][full_part]=0
                        n_under_min_wage[full_part]+=_n_job(j,type)[full_part]
            n_job=_n_job(i,type)
            for full_part in range(len(worker[0][0])):
                n_emp=n_job[full_part] - worker[i][type][full_part] + n_under_min_wage[full_part]
                if n_emp>=0:
                    n_exp=min(n_emp*0.8,unemp_e[type]*rate_match) #最低2割は新人
                    unemp_e[type]-=n_exp
                    worker[i][type][full_part]+=n_exp
                    if(n_emp==n_exp):
                        continue
                    n_new=min(n_emp-n_exp,unemp_n[type]*rate_match)
                    unemp_n[type]-=n_new
                    worker[i][type][full_part]+=n_new
                    if(unemp_e[type]<=0 and unemp_n[type]<=0):
                        break
                else:
                    n_emp*=-1
                    worker[i][type][full_part]-=n_emp
                    unemp_e[type]+=n_emp

def save_data(t):
    global history_poor,history_unemp,worker,unemp_n,unemp_e
    n_people=0
    for type in range(len(worker[0])):
        for i in range(len(worker)):
            for full_part in range(len(worker[0][0])):
                n_people+=worker[i][type][full_part]
        n_people+=unemp_n[type]+unemp_e[type]
    history_unemp[t]=0
    history_poor[t]=0
    for type in range(len(worker[0])):
        history_unemp[t]+=unemp_n[type]+unemp_e[type]
        history_poor[t]+=unemp_n[type]+unemp_e[type]
        for full_part in range(len(worker[0][0])):
            for i in range(len(wage)):
                if wage[i]*worktime[full_part]>min_liv_wage:
                    history_poor[t]+=worker[i][type][full_part]*(min_liv_wage-wage[i-1]*worktime[full_part])/WAGE_STEP
                    break
                history_poor[t]+=worker[i][type][full_part]
    history_unemp[t]=history_unemp[t]/n_people*100
    history_poor[t]=history_poor[t]/n_people*100

for t in range(TIME_LENGTH):#years
    #if t%12==0:
    update_unemp()
    update_min_wage(t)
    update_job()
    update_worker()
    save_data(t)

print("unemployed num:")
print(history_unemp)
print("poverty num:")
print(history_poor)
