TIME_LENGTH=120
WAGE_STEP=100
min_wage=1300#最低賃金
min_liv_wage=1100#最低生計費
wage_l=[i for i in range(500,2001,WAGE_STEP)]#時給:階級上限値
worker_l=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]#雇用者数
job_l=[0,0,0,0,0,18,30,28,7,5,3,4,1,0,1,3]#求人
unemp_n=70
unemp_l=0
history_unemp=[-1 for i in range(TIME_LENGTH)]
history_poor=[-1 for i in range(TIME_LENGTH)]
def update_min_wage(t):
    global min_wage
    if t>=60:
        min_wage=900

def update_unemp():
    global unemp_n,unemp_l,worker_l
    for i in range(len(worker_l)):
        unemp_l+=worker_l[i]*0.05
        worker_l[i]=worker_l[i]*0.9
    unemp_n+=10

def update_job():
    pass

def update_worker():
    global worker_l,job_l,unemp_n,unemp_l
    n_under_min_wage=0
    for i in range(len(worker_l)-1,-1,-1):
        if(wage_l[i]<min_wage):
            n_under_min_wage+=job_l[i]*min(1,wage_l[i]/min_wage)-worker_l[i]
            continue
        n_emp=job_l[i]*min(1,wage_l[i]/min_wage)-worker_l[i]+n_under_min_wage
        n_under_min_wage=0
        n_exp=min(n_emp,unemp_l*0.8)
        unemp_l-=n_exp
        worker_l[i]+=n_exp
        if(n_emp==n_exp):
            continue
        n_new=min(n_emp-n_exp,unemp_n)
        unemp_n-=n_new
        worker_l[i]+=n_new
        if(unemp_l<=0 and unemp_n<=0):
            break

def save_data(t):
    global history_poor,history_unemp
    history_unemp[t]=unemp_n+unemp_l
    history_poor[t]=history_unemp[t]
    for i in range(len(wage_l)):
        if wage_l[i]>min_liv_wage:
            history_poor[t]+=worker_l[i]*(min_liv_wage-wage_l[i-1])/WAGE_STEP
            break
        history_poor[t]+=worker_l[i]

for t in range(TIME_LENGTH):#months
    save_data(t)
    if t%12==0:
        update_unemp()
        update_min_wage(t)
    update_job()
    update_worker()

print("unemployed num:")
print(history_unemp)
print("poverty num:")
print(history_poor)
