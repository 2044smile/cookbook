# cookbook
https://django-orm-cookbook-ko.readthedocs.io/en/latest/

# poetry
1. brew install poetry
2. poetry init
3. poetry add django
4. poetry run python manage.py runserver

# details
```python
# 1. 장고 ORM이 실행하는 실제 SQL 질의문을 확인할 수 있나요?
filter(years_ago__gt=5)  
"""
lt: 작은  # WHERE "events_event"."years_ago" < 5'
lte: 작거나 같은  # WHERE "events_event"."years_ago" <= 5'
gt: 큰  # WHERE "events_event"."years_ago" > 5'
gte: 크거나 같은  # WHERE "events_event"."years_ago" >= 5'
"""
all().order_by('-id')[:10]  # ORDER BY "events_event"."id" DESC LIMIT 10
# ---
# 2. OR 연산으로 일부 조건을 하나라도 만족하는 항목을 구하려면 어떻게 하나요?
# SELECT username, first_name, last_name, email FROM auth_user WHERE first_name LIKE 'R%' OR last_name LIKE 'D%';
queryset = User.objects.filter(
    first_name__startswith='R'
) | User.objects.filter(
    last_name__startswith='D'
)
from django.db.models import Q
queryset = User.objects.filter(Q(first_name__startswith='R')|Q(last_name__startswith='D'))
## 성능 차이는 없다, 하지만 나는 아래의 코드를 선호
# ---
# 3. AND 연산으로 여러 조건을 모두 만족하는 항목을 구하려면 어떻게 하나요?
# SELECT username, first_name, last_name, email FROM auth_user WHERE first_name LIKE 'R%' AND last_name LIKE 'D%';
## 장고 쿼리셋의 filter 메서드에서 여러 조건을 결합하는 방법은 기본적으로 AND 방식이다.
queryset1 = User.objects.filter(
    first_name__startswith='R',
    last_name__startswith='D'
)
queryset2 = User.objects.filter(first_name__startswith='R') & User.objects.filter(last_name__startswith='D')
queryset3 = User.objects.filter(Q(first_name__startswith='R')&Q(last_name__startswith='D'))

str(queryset1.query) == str(queryset2.query) == str(queryset3.query)  # True
# ---
# 4. NOT 연산으로 조건을 부정하려면 어떻게 하나요?
# SELECT id, username, first_name, last_name, email FROM auth_user WHERE NOT id < 5;
## exclude()
queryset = User.objects.exclude(id__lt=5)
## filter()
queryset = User.objects.filter(~Q(id__lt=5))  # ~Q 부정 / WHERE NOT ("auth_user"."id" < 5)'
# 5. 동일한 모델 또는 서로 다른 모델에서 구한 쿼리셋들을 합할 수 있나요?
## 여러 개의 집합을 합할 때 UNION 연산을 이용합니다.
## 장고 ORM 에서 union 메서드를 이용해 쿼리셋을 합할 수 있습니다.
## 합하려는 쿼리셋의 모델이 서로 다른 경우, 각 쿼리셋에 포함된 필드와 데이터 유형이 서로 맞아야 합니다.
q1 = User.objects.filter(id__gte=5)
q2 = User.objects.filter(id__lte=9)

q1.union(q2)
q2.union(q1)
## 쿼리셋의 필드와 데이터 유형이 서로 일치할 때만 실행할 수 있습니다.
## Here 모델과 Villain 모델은 둘 다 name 필드와 gender 필드를 갖고 있습니다.
## values_list 를 이용해 공통된 필드만 가져온 뒤 union을 수행할 수 있습니다.
Here.objects.all().values_list(
    "name", "gender"
).union(
    Villain.objects.all().values_list(
        "name", "gender
))
# ---
# 6. 필요한 열만 골라 조회하려면 어떻게 하나요?
## 쿼리셋의 values 메서드와 values_list 메서드
User.objects.filter(
    first_name__startswith='R'
).values('first_name', 'last_name')  # SELECT "auth_user"."first_name", "auth_user"."last_name" FROM "auth_user" WHERE "auth_user"."first_name"::text LIKE R%
## only 메서드
queryset = User.objects.filter(
    first_name__startswith='R'
).only('first_name', 'last_name')  # SELECT "auth_user"."id", "auth_user"."first_name", "auth_user"."last_name" FROM "auth_user" WHERE "auth_user"."first_name"::text LIKE R%
## only 메서드가 values 메서드와 다른 점은 id 필드를 가져온다는 점
# ---
```
