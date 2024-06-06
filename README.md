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
```
